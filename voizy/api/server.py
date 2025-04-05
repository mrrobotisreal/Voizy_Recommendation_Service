"""
FastAPI server for the Voizy recommender system.
"""
import logging
import threading
import time
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import datetime

from voizy.api.dependencies import (
    get_recommender,
    get_config,
    recommender_config,
    db_config,
    recommender,
    last_model_refresh,
    recommendation_cache
)
from voizy.recommender.data import (
    fetch_interactions_data,
    fetch_user_features,
    fetch_post_features
)
from voizy.recommender.utils import record_recommendation_metrics

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="Voizy Recommender API",
        description="API for the Voizy recommender system",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from voizy.api.endpoints import router as api_router

    app.include_router(
        api_router,
        dependencies=[Depends(get_recommender), Depends(get_config)]
    )

    @app.on_event("startup")
    async def startup_event():
        refresh_thread = threading.Thread(
            target=refresh_model_periodically,
            daemon=True
        )
        refresh_thread.start()
        logger.info("Started background model refresh thread")

    return app


def refresh_model_periodically():
    """
    Background thread to refresh the model periodically
    """
    global last_model_refresh, recommender, recommendation_cache

    while True:
        try:
            current_time = datetime.datetime.now()

            if last_model_refresh is None:
                last_model_refresh = current_time
                logger.info("Initialized last_model_refresh timestamp")

            seconds_since_refresh = (current_time - last_model_refresh).total_seconds()

            if seconds_since_refresh >= recommender_config['refresh_interval']:
                logger.info("Starting scheduled model refresh...")

                if recommender is None:
                    recommender = get_recommender()

                training_recommender = get_recommender()

                interactions_df = fetch_interactions_data(
                    training_recommender.conn,
                    db_config,
                    days_limit=30
                )

                user_features_df = fetch_user_features(
                    training_recommender.conn,
                    db_config
                )

                post_features_df = fetch_post_features(
                    training_recommender.conn,
                    db_config,
                    days_limit=60
                )

                interactions_matrix, user_features_matrix, post_features_matrix = training_recommender.prepare_data(
                    interactions_df, user_features_df, post_features_df
                )

                training_recommender.train_model(
                    interactions_matrix,
                    user_features_matrix,
                    post_features_matrix,
                    num_components=30,
                    learning_rate=0.05,
                    epochs=20
                )

                training_recommender.save_model(recommender_config['model_path'])

                recommender = training_recommender

                recommendation_cache.clear()

                last_model_refresh = datetime.datetime.now()
                logger.info("Model refresh completed successfully")

                record_recommendation_metrics(
                    recommender.conn,
                    "model_training_completed",
                    1.0,
                    {
                        "timestamp": last_model_refresh.isoformat(),
                        "num_users": len(recommender.user_mapping),
                        "num_posts": len(recommender.post_mapping)
                    }
                )

        except Exception as e:
            logger.error(f"Error during model refresh: {e}")

        # Sleep for a while before checking again
        time.sleep(60 * 10)  # Check every 10 minutes