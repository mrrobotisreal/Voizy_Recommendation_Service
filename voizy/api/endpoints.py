"""
API endpoints for the Voizy recommender system.
"""
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Query, Depends, HTTPException, Header, Body
from pydantic import BaseModel, Field
import threading

from voizy.recommender.engine import VoizyRecommender
from voizy.api.dependencies import (
    get_recommender,
    get_config,
    recommendation_cache,
    recommender_config
)
from voizy.recommender.data import (
    fetch_interactions_data,
    fetch_user_features,
    fetch_post_features,
    get_popular_posts
)

logger = logging.getLogger(__name__)

router = APIRouter()


class Recommendation(BaseModel):
    post_id: int
    score: float


class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]


class PostIdList(BaseModel):
    post_ids: List[int]


class FeedbackRequest(BaseModel):
    user_id: int
    post_id: int
    feedback_type: str = Field(..., description="Feedback type, e.g., 'like', 'dislike', 'not_interested'")


class SuccessResponse(BaseModel):
    success: bool
    message: str = ""


@router.get("/api/recommendations", response_model=RecommendationResponse, tags=["recommendations"])
async def get_recommendations(
        user_id: int = Query(..., description="User ID"),
        limit: int = Query(10, ge=1, le=100, description="Number of recommendations to return"),
        exclude_seen: bool = Query(True, description="Whether to exclude already seen posts"),
        recommender: VoizyRecommender = Depends(get_recommender),
        config_dict: Dict[str, Any] = Depends(get_config)
):
    """
    Get personalized post recommendations for a user.
    """
    try:
        cache_key = f"{user_id}_{limit}_{exclude_seen}"
        current_time = datetime.now()

        if cache_key in recommendation_cache:
            cache_time, cached_recommendations = recommendation_cache[cache_key]
            seconds_since_cache = (current_time - cache_time).total_seconds()

            if seconds_since_cache < config_dict['recommender_config']['recommendation_cache_ttl']:
                logger.info(f"Returned cached recommendations for user {user_id}")
                return {"recommendations": cached_recommendations}

        recommendations = recommender.get_recommendations(user_id, n=limit, exclude_seen=exclude_seen)

        formatted_recommendations = [
            Recommendation(post_id=rec['post_id'], score=rec['score'])
            for rec in recommendations
        ]

        recommendation_cache[cache_key] = (current_time, formatted_recommendations)

        try:
            recommender.update_analytics_after_recommendation(
                user_id,
                [rec.post_id for rec in formatted_recommendations[:5]]
            )
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")

        return {"recommendations": formatted_recommendations}

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/popular", response_model=PostIdList, tags=["recommendations"])
async def get_popular_posts_endpoint(
        limit: int = Query(10, ge=1, le=100, description="Number of posts to return"),
        days: int = Query(7, ge=1, le=30, description="Limit to posts from the last N days"),
        recommender: VoizyRecommender = Depends(get_recommender)
):
    """
    Get popular posts from the last N days.
    """
    try:
        popular_posts = get_popular_posts(recommender.conn, n=limit, days_limit=days)

        return {"post_ids": popular_posts}
    except Exception as e:
        logger.error(f"Error fetching popular posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/feedback", response_model=SuccessResponse, tags=["feedback"])
async def record_feedback(
        feedback: FeedbackRequest,
        recommender: VoizyRecommender = Depends(get_recommender)
):
    """
    Record explicit user feedback for recommendations.
    """
    try:
        cursor = recommender.conn.cursor()
        query = """
        INSERT INTO analytics_events 
        (user_id, event_type, object_type, object_id, event_time, meta_data)
        VALUES (%s, %s, 'post', %s, NOW(), %s)
        """

        event_type = f"recommendation_{feedback.feedback_type}"
        meta_data = json.dumps({'source': 'recommender_system'})

        cursor.execute(query, (feedback.user_id, event_type, feedback.post_id, meta_data))

        query = """
        UPDATE user_recommendations
        SET is_interacted = 1,
            interaction_type = %s,
            interaction_time = NOW()
        WHERE user_id = %s
          AND post_id = %s
          AND is_interacted = 0
        """

        cursor.execute(query, (feedback.feedback_type, feedback.user_id, feedback.post_id))

        recommender.conn.commit()
        cursor.close()

        for key in list(recommendation_cache.keys()):
            if key.startswith(f"{feedback.user_id}_"):
                del recommendation_cache[key]

        return {"success": True, "message": "Feedback recorded successfully"}
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/refresh", response_model=SuccessResponse, tags=["admin"])
async def trigger_refresh(
        recommender: VoizyRecommender = Depends(get_recommender),
        config_dict: Dict[str, Any] = Depends(get_config),
        x_api_key: Optional[str] = Header(None)
):
    """
    Manually trigger model refresh (protected by API key).
    """
    expected_key = config_dict.get('recommender_config', {}).get('ADMIN_KEY')

    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    refresh_thread = threading.Thread(
        target=refresh_model_now,
        args=(recommender, config_dict),
        daemon=True
    )
    refresh_thread.start()

    return {"success": True, "message": "Model refresh started"}


def refresh_model_now(recommender: VoizyRecommender, config_dict: Dict[str, Any]):
    """
    Refresh the model immediately
    """
    logger.info("Starting manual model refresh...")

    try:
        db_config = config_dict['db_config']

        interactions_df = fetch_interactions_data(
            recommender.conn,
            db_config,
            days_limit=30
        )

        user_features_df = fetch_user_features(
            recommender.conn,
            db_config
        )

        post_features_df = fetch_post_features(
            recommender.conn,
            db_config,
            days_limit=60
        )

        interactions_matrix, user_features_matrix, post_features_matrix = recommender.prepare_data(
            interactions_df, user_features_df, post_features_df
        )

        recommender.train_model(
            interactions_matrix,
            user_features_matrix,
            post_features_matrix,
            num_components=30,
            learning_rate=0.05,
            epochs=20
        )

        recommender.save_model(config_dict['recommender_config']['model_path'])

        recommendation_cache.clear()

        logger.info("Manual model refresh completed successfully")
    except Exception as e:
        logger.error(f"Error during manual model refresh: {e}")