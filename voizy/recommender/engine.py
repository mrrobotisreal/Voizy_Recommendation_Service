"""
Core recommender engine for Voizy

This module implements the VoizyRecommender class, which provides the core
functionality for the hybrid recommendation system combining collaborative
filtering and content-based approaches.
"""
import logging
import pickle
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.evaluation import precision_at_k, auc_score
from scipy.sparse import csr_matrix

from voizy.db.connection import get_db_connection

logger = logging.getLogger(__name__)


class VoizyRecommender:
    """
    Main recommender engine for Voizy.

    This class implements a hybrid recommendation system using LightFM,
    combining collaborative filtering with content-based approaches.
    """

    def __init__(self, db_config: Dict[str, Any], model_path: Optional[str] = None):
        """
        Initialize the recommender system

        Args:
            db_config: Database connection configuration
            model_path: Path to saved model (optional)
        """
        self.db_config = db_config
        self.conn = None
        self.model = None
        self.user_mapping = {}
        self.post_mapping = {}
        self.dataset = Dataset()

        self._connect_to_db()

        if model_path:
            self.load_model(model_path)

    def _connect_to_db(self) -> None:
        """Establish connection to the database"""
        try:
            self.conn = get_db_connection(self.db_config)
            logger.info("Successfully connected to database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def prepare_data(
            self,
            interactions_df,
            user_features_df=None,
            post_features_df=None
    ) -> Tuple[csr_matrix, Optional[csr_matrix], Optional[csr_matrix]]:
        """
        Prepare data for the LightFM model

        Args:
            interactions_df: User-post interactions
            user_features_df: User features (optional)
            post_features_df: Post features (optional)

        Returns:
            Tuple containing:
                - interactions_matrix: User-item interaction matrix
                - user_features_matrix: User features matrix (optional)
                - item_features_matrix: Item features matrix (optional)
        """
        interactions_df = interactions_df.dropna(subset=['user_id', 'post_id'])

        interactions_df['user_id'] = interactions_df['user_id'].astype(int)
        interactions_df['post_id'] = interactions_df['post_id'].astype(int)

        unique_user_ids = interactions_df['user_id'].unique()
        unique_post_ids = interactions_df['post_id'].unique()

        user_features = None
        if user_features_df is not None:
            from voizy.recommender.data import extract_user_features
            user_features = extract_user_features(user_features_df)

        item_features = None
        if post_features_df is not None:
            from voizy.recommender.data import extract_post_features
            item_features = extract_post_features(post_features_df)

        self.dataset.fit(
            users=unique_user_ids,
            items=unique_post_ids,
            user_features=user_features,
            item_features=item_features
        )

        self.user_mapping = {int(user): i for i, user in enumerate(unique_user_ids)}
        self.post_mapping = {int(post): i for i, post in enumerate(unique_post_ids)}

        from scipy.sparse import coo_matrix
        interactions = coo_matrix(
            (
                interactions_df['interaction_strength'].astype(float),
                (
                    interactions_df['user_id'].map(self.user_mapping),
                    interactions_df['post_id'].map(self.post_mapping)
                )
            ),
            shape=(len(unique_user_ids), len(unique_post_ids))
        )

        interactions_matrix = interactions.tocsr()

        user_features_matrix = None
        if user_features_df is not None and user_features:
            from voizy.recommender.data import build_user_features_matrix
            user_features_matrix = build_user_features_matrix(
                user_features_df, self.user_mapping, self.dataset, user_features
            )

        post_features_matrix = None
        if post_features_df is not None and item_features:
            from voizy.recommender.data import build_post_features_matrix
            post_features_matrix = build_post_features_matrix(
                post_features_df, self.post_mapping, self.dataset, item_features
            )

        return interactions_matrix, user_features_matrix, post_features_matrix

    def train_model(
            self,
            interactions_matrix: csr_matrix,
            user_features_matrix: Optional[csr_matrix] = None,
            post_features_matrix: Optional[csr_matrix] = None,
            num_components: int = 30,
            learning_rate: float = 0.05,
            epochs: int = 20
    ) -> LightFM:
        """
        Train the LightFM model

        Args:
            interactions_matrix: User-item interactions
            user_features_matrix: User features (optional)
            post_features_matrix: Post features (optional)
            num_components: Number of latent factors
            learning_rate: Learning rate
            epochs: Number of epochs

        Returns:
            trained model
        """
        self.model = LightFM(
            no_components=num_components,
            learning_rate=learning_rate,
            loss='warp',  # Weighted Approximate-Rank Pairwise loss for implicit feedback
            random_state=42
        )

        logger.info(f"Training model with {epochs} epochs...")
        self.model.fit(
            interactions=interactions_matrix,
            user_features=user_features_matrix,
            item_features=post_features_matrix,
            epochs=epochs,
            verbose=True
        )

        train_precision = precision_at_k(
            self.model,
            interactions_matrix,
            user_features=user_features_matrix,
            item_features=post_features_matrix,
            k=5
        ).mean()

        train_auc = auc_score(
            self.model,
            interactions_matrix,
            user_features=user_features_matrix,
            item_features=post_features_matrix
        ).mean()

        logger.info(f"Model training complete. Train precision@5: {train_precision:.4f}, Train AUC: {train_auc:.4f}")

        return self.model

    def save_model(self, path: str) -> bool:
        """
        Save model and mappings to disk

        Args:
            path: Path to save the model

        Returns:
            Success status
        """
        if self.model is None:
            logger.error("No model to save")
            return False

        try:
            with open(f"{path}_model.pkl", 'wb') as f:
                pickle.dump(self.model, f)

            with open(f"{path}_mappings.pkl", 'wb') as f:
                pickle.dump({
                    'user_mapping': self.user_mapping,
                    'post_mapping': self.post_mapping
                }, f)

            logger.info(f"Model and mappings saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False

    def load_model(self, path: str) -> bool:
        """
        Load model and mappings from disk

        Args:
            path: Path to load the model from

        Returns:
            Success status
        """
        try:
            with open(f"{path}_model.pkl", 'rb') as f:
                self.model = pickle.load(f)

            with open(f"{path}_mappings.pkl", 'rb') as f:
                mappings = pickle.load(f)
                self.user_mapping = mappings['user_mapping']
                self.post_mapping = mappings['post_mapping']

            logger.info(f"Model loaded from {path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def get_recommendations(
            self,
            user_id: int,
            n: int = 10,
            exclude_seen: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get post recommendations for a user

        Args:
            user_id: User ID
            n: Number of recommendations to return
            exclude_seen: Whether to exclude posts the user has already interacted with

        Returns:
            List of recommended post IDs with scores
        """
        if self.model is None:
            logger.error("Model not trained or loaded")
            return []

        if user_id not in self.user_mapping:
            logger.warning(f"User {user_id} not in training data")
            from voizy.recommender.data import get_popular_posts
            popular_posts = get_popular_posts(self.conn, n)
            return [{'post_id': post_id, 'score': 0.0} for post_id in popular_posts]

        user_idx = self.user_mapping[user_id]

        # Get scores for all posts using proper prediction format
        # LightFM expects arrays of user_ids and item_ids with the same length
        # For a single user, we need to repeat the user_id for each item
        n_items = len(self.post_mapping)
        user_idxs = [user_idx] * n_items
        item_idxs = list(range(n_items))

        scores = self.model.predict(
            user_ids=user_idxs,
            item_ids=item_idxs
        )

        inverse_post_mapping = {v: k for k, v in self.post_mapping.items()}
        post_scores = [(inverse_post_mapping[i], float(scores[i])) for i in range(len(scores))]

        post_scores.sort(key=lambda x: x[1], reverse=True)

        if exclude_seen:
            from voizy.recommender.data import get_user_interactions
            seen_posts = get_user_interactions(self.conn, user_id)
            post_scores = [ps for ps in post_scores if ps[0] not in seen_posts]

        top_posts = [{'post_id': ps[0], 'score': ps[1]} for ps in post_scores[:n]]
        return top_posts

    def update_analytics_after_recommendation(self, user_id: int, recommended_posts: List[int]) -> None:
        """
        Update analytics after showing recommendations to a user

        Args:
            user_id: User ID
            recommended_posts: List of recommended post IDs
        """
        cursor = self.conn.cursor()

        for post_id in recommended_posts:
            query = """
            UPDATE posts
            SET impressions = impressions + 1
            WHERE post_id = %s
            """
            cursor.execute(query, (post_id,))

            query = """
            INSERT INTO analytics_events 
            (user_id, event_type, object_type, object_id, event_time, meta_data)
            VALUES (%s, 'post_recommendation', 'post', %s, NOW(), '{"source": "recommender_system"}')
            """
            cursor.execute(query, (user_id, post_id))

            query = """
            INSERT INTO user_recommendations
            (user_id, post_id, recommendation_time, source)
            VALUES (%s, %s, NOW(), 'ml_recommender')
            """
            cursor.execute(query, (user_id, post_id))

        self.conn.commit()
        cursor.close()