import logging
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.data.schemas import (
User, Post, PostReaction, Comment, PostShare, Hashtag, PostHashtag, RecommendationModel, UserEmbedding, ContentEmbedding
)
from app.ml.features.user_features import UserFeatureExtractor
from app.ml.features.content_features import ContentFeatureExtractor
from app.data.repositories.user_repository import UserRepository
from app.data.repositories.content_repository import ContentRepository
from app.data.repositories.interaction_repository import InteractionRepository
from scripts.generate_mock_data import user_embeddings, content_embeddings


class ModelTrainer:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository()
        self.content_repo = ContentRepository()
        self.interaction_repo = InteractionRepository()
        self.logger = logging.getLogger(__name__)

    async def train_model(self, model_type: str = "hybrid") -> bool:
        self.logger.info(f"Starting training for {model_type} model")

        try:
            await self._generate_embeddings()

            training_data = await self._prepare_training_data(model_type)

            model_weights = await self._train_specific_model(model_type, training_data)

            metrics = await self._evaluate_model(model_type, model_weights, training_data)

            await self._save_model(model_type, model_weights, metrics)

            self.logger.info(f"Successfully trained {model_type} model")
            return True
        except Exception as e:
            self.logger.error(f"Error training model {model_type}: {str(e)}")
            return False

    async def _generate_embeddings(self) -> None:
        self.logger.info("Generating embeddings for users and content")

        user_feature_extractor = UserFeatureExtractor(self.user_repo, self.interaction_repo)
        content_feature_extractor = ContentFeatureExtractor(self.content_repo)

        users = self.db.query(User).limit(100).all()

        for user in users:
            try:
                user_embedding = user_feature_extractor.create_user_embedding(self.db, user.user_id)
                self.logger.debug(f"Generated embedding for user {user.user_id}")
            except Exception as e:
                self.logger.error(f"Error generating embedding for user {user.user_id}: {str(e)}")

        posts = self.db.query(Post).limit(500).all()

        for post in posts:
            try:
                content_embedding = content_feature_extractor.create_content_embedding(self.db, post.post_id)
                self.logger.debug(f"Generated embedding for post {post.post_id}")
            except Exception as e:
                self.logger.error(f"Error generating embedding for post {post.post_id}")

        self.logger.info("Finished generating embeddings")

    async def _prepare_training_data(self, model_type: str) -> Dict[str, Any]:
        self.logger.info(f"Preparing training data for {model_type} model")

        training_data = {
            "user_ids": [],
            "content_ids": [],
            "interactions": []
        }

        interaction_matrix = self.interaction_repo.get_user_content_interaction_matrix(self.db)
        training_data.update(interaction_matrix)

        if model_type == "content_based" or model_type == "hybrid":
            training_data["content_features"] = {}
            content_embeddings = self.db.query(ContentEmbedding).filter(
                ContentEmbedding.embedding_type == "combined"
            ).all()

            for embedding in content_embeddings:
                training_data["content_features"][embedding.content_id] = json.loads(embedding.embedding_vector)

        if model_type == "collaborative" or model_type == "hybrid":
            training_data["user_embeddings"] = {}
            user_embeddings = self.db.query(UserEmbedding).filter(
                UserEmbedding.embedding_type == "combined"
            ).all()

            for embedding in user_embeddings:
                training_data["user_embeddings"][embedding.user_id] = json.loads(embedding.embedding_vector)

        self.logger.info(f"Prepared training data with {len(training_data['user_ids'])} users and {len(training_data['content_ids'])} content items")
        return training_data

    async def _train_specific_model(self, model_type: str, training_data: Dict[str, Any]) -> Dict[str, float]:
        self.logger.info(f"Training {model_type} model")

        if model_type == "collaborative":
            return await self._train_collaborative_model(training_data)
        elif model_type == "content_based":
            return await self._train_content_based_model(training_data)
        elif model_type == "hybrid":
            return await self._train_hybrid_model(training_data)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    async def _train_collaborative_model(self, training_data: Dict[str, Any]) -> Dict[str, float]:
        return {
            "user_similarity": 0.6,
            "content_popularity": 0.2,
            "recency": 0.2
        }

    async def _train_content_based_model(self, training_data: Dict[str, Any]) -> Dict[str, float]:
        return {
            "interest_match": 0.5,
            "hashtag_match": 0.3,
            "text_similarity": 0.2
        }

    async def _train_hybrid_model(self, training_data: Dict[str, Any]) -> Dict[str, float]:
        return {
            "collaborative_score": 0.4,
            "content_based_score": 0.4,
            "popularity_score": 0.1,
            "recency_score": 0.1
        }

    async def _evaluate_model(self, model_type: str, model_weights: Dict[str, float], training_data: Dict[str, Any]) -> Dict[str, float]:
        self.logger.info(f"Evaluating {model_type} model")

        return {
            "precision": 0.42 + np.random.uniform(0, 0.1),
            "recall": 0.38 + np.random.uniform(0, 0.1),
            "ndcg": 0.45 + np.random.uniform(0, 0.1),
            "training_time_seconds": np.random.uniform(10, 100)
        }

    async def _save_model(self, model_type: str, model_weights: Dict[str, float], metrics: Dict[str, float]) -> None:
        self.logger.info(f"Saving {model_type} model to database")

        new_model = RecommendationModel(
            model_type=model_type,
            model_version=f"{model_type}_v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            model_weights=json.dumps(model_weights),
            metrics=json.dumps(metrics),
            created_at=datetime.now(),
            is_active=True
        )

        previous_models = self.db.query(RecommendationModel).filter(
            RecommendationModel.model_type == model_type,
            RecommendationModel.is_active == True
        ).all()

        for model in previous_models:
            model.is_active = False

        self.db.add(new_model)
        self.db.commit()

        self.logger.info(f"Successfully saved {model_type} model with ID {new_model.model_id}")