"""
Script to train the initial model for the Voizy recommender system.
"""
import sys
import logging
import configparser
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from voizy.recommender.engine import VoizyRecommender
from voizy.recommender.data import (
    fetch_interactions_data,
    fetch_user_features,
    fetch_post_features
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/train_model.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function to train the initial model"""
    logger.info("Starting initial model training")

    config = configparser.ConfigParser()
    config.read('../recommender_config.ini')

    db_config = {
        'host': config.get('DATABASE', 'HOST', fallback='localhost'),
        'user': config.get('DATABASE', 'USER'),
        'password': config.get('DATABASE', 'PASSWORD'),
        'database': config.get('DATABASE', 'DATABASE', fallback='voizy_db')
    }

    # model_path = config.get('RECOMMENDER', 'MODEL_PATH', fallback='../models/voizy_recommender')
    model_path = '../models/voizy_recommender'

    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    try:
        recommender = VoizyRecommender(db_config)

        logger.info("Fetching interaction data...")
        interactions_df = fetch_interactions_data(recommender.conn, db_config, days_limit=30)

        logger.info("Fetching user features...")
        user_features_df = fetch_user_features(recommender.conn, db_config)

        logger.info("Fetching post features...")
        post_features_df = fetch_post_features(recommender.conn, db_config, days_limit=60)

        logger.info("Preparing data for model training...")
        interactions_matrix, user_features_matrix, post_features_matrix = recommender.prepare_data(
            interactions_df, user_features_df, post_features_df
        )

        logger.info("Training model...")
        recommender.train_model(
            interactions_matrix,
            user_features_matrix,
            post_features_matrix,
            num_components=30,
            learning_rate=0.05,
            epochs=20
        )

        logger.info(f"Saving model to {model_path}...")
        success = recommender.save_model(model_path)

        if success:
            logger.info("Model training completed successfully")
        else:
            logger.error("Failed to save model")
            return 1

        logger.info("Testing model with sample recommendation...")
        try:
            sample_user_id = next(iter(recommender.user_mapping.keys()))
            recommendations = recommender.get_recommendations(sample_user_id, n=5)
            logger.info(f"Sample recommendations for user {sample_user_id}: {recommendations}")
        except (StopIteration, Exception) as e:
            logger.warning(f"Couldn't generate sample recommendations: {e}")

        return 0
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())