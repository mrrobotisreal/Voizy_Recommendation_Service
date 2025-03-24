from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    limit: int = Field(20, description="Maximum number of recommendations to return")
    exclude_seen: bool = Field(True, description="Whether to exclude content the user has already seen")
    content_types: Optional[List[str]] = Field(None, description="Content types to include")


class ContentItem(BaseModel):
    """Content item in recommendation response"""
    content_id: int
    creator_id: int
    content_type: str
    title: str
    created_at: datetime
    score: float
    relevance_factors: List[str] = []


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    user_id: int
    recommendations: List[ContentItem]
    model_version: str
    generated_at: datetime


class TrainingRequest(BaseModel):
    """Request model for model training"""
    model_type: str = Field("hybrid", description="Type of model to train")


class ModelInfo(BaseModel):
    """Model information"""
    version: str
    is_trained: bool
    trained_at: Optional[datetime]
    features_used: List[str]
    model_type: str
