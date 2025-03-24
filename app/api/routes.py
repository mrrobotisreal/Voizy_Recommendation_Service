from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.api.models import RecommendationRequest, RecommendationResponse, ContentItem, ModelInfo
from app.data.db import get_db
from app.data.repositories.user_repository import UserRepository
from app.data.repositories.content_repository import ContentRepository
from app.data.repositories.interaction_repository import InteractionRepository
from app.ml.models.hybrid import HybridRecommender

# Setup logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# --- Dependency Injection ---

def get_user_repository():
    return UserRepository()


def get_content_repository():
    return ContentRepository()


def get_interaction_repository():
    return InteractionRepository()


def get_recommendation_model(
        db: Session = Depends(get_db),
        user_repo: UserRepository = Depends(get_user_repository),
        content_repo: ContentRepository = Depends(get_content_repository),
        interaction_repo: InteractionRepository = Depends(get_interaction_repository)
):
    return HybridRecommender(db, user_repo, content_repo, interaction_repo)


# --- API Endpoints ---

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}


@router.post("/recommendations/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
        user_id: int,
        request: RecommendationRequest,
        model: HybridRecommender = Depends(get_recommendation_model),
        user_repo: UserRepository = Depends(get_user_repository),
        content_repo: ContentRepository = Depends(get_content_repository),
        db: Session = Depends(get_db)
):
    """Get personalized recommendations for a user"""
    try:
        # Check if user exists
        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

        # Get user features
        user_features = None  # Let the model extract features as needed

        # Get seen content IDs if excluding
        seen_content_ids = []
        if request.exclude_seen:
            # This would be implemented in a real system
            # For now, return an empty list
            pass

        # Set up filters
        filters = {}
        if request.content_types:
            filters["content_types"] = request.content_types

        # Get recommendations from model
        recommendations = model.recommend(
            user_id=user_id,
            user_features=user_features,
            exclude_content_ids=seen_content_ids,
            filters=filters,
            limit=request.limit
        )

        # Log recommendation request
        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")

        # Format response
        response_items = []
        for rec in recommendations:
            content_data = content_repo.get_content_by_id(db, rec["content_id"])
            if not content_data:
                continue

            # Determine content type
            content_type = "post"
            if content_data.get("is_poll"):
                content_type = "poll"
            elif content_data.get("original_post_id"):
                content_type = "repost"

            # Create response item
            response_items.append(ContentItem(
                content_id=content_data["content_id"],
                creator_id=content_data["user_id"],
                content_type=content_type,
                title=content_data["content_text"][:50] if content_data["content_text"] else "No title",
                created_at=content_data["created_at"] or datetime.utcnow(),
                score=rec["score"],
                relevance_factors=rec["factors"]
            ))

        return RecommendationResponse(
            user_id=user_id,
            recommendations=response_items,
            model_version=model.version,
            generated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/models/train")
async def train_model(
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        user_repo: UserRepository = Depends(get_user_repository),
        content_repo: ContentRepository = Depends(get_content_repository),
        interaction_repo: InteractionRepository = Depends(get_interaction_repository)
):
    """Trigger model training (asynchronous)"""
    try:
        # This would be implemented to train the model in the background
        # For now, just return a success response
        return {"status": "training_started", "message": "Model training has been scheduled"}
    except Exception as e:
        logger.error(f"Error scheduling model training: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scheduling model training: {str(e)}")


@router.get("/models/info", response_model=ModelInfo)
async def get_model_info(
        model: HybridRecommender = Depends(get_recommendation_model)
):
    """Get information about the current model"""
    try:
        # This would return actual model info in a real implementation
        return ModelInfo(
            version=model.version,
            is_trained=True,
            trained_at=datetime.utcnow(),
            features_used=[
                "user_interests",
                "content_text",
                "social_connections",
                "engagement_metrics"
            ],
            model_type="hybrid_recommender"
        )
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")


@router.post("/interactions/{user_id}/{content_id}")
async def record_interaction(
        user_id: int,
        content_id: int,
        interaction_type: str,
        interaction_repo: InteractionRepository = Depends(get_interaction_repository),
        db: Session = Depends(get_db)
):
    """Record a user interaction with content"""
    try:
        # Validate interaction type
        valid_types = ["view", "click", "reaction", "comment", "share"]
        if interaction_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid interaction type. Must be one of: {valid_types}")

        # Record view
        if interaction_type == "view":
            interaction_repo.record_content_view(db, user_id, content_id)

        # Other interaction types would be implemented similarly

        return {"status": "success", "message": f"Recorded {interaction_type} interaction"}
    except Exception as e:
        logger.error(f"Error recording interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error recording interaction: {str(e)}")
