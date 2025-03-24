import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json


class UserFeatureExtractor:
    """Extracts features from user data for recommendation models"""

    def __init__(self, user_repository, interaction_repository):
        self.user_repository = user_repository
        self.interaction_repository = interaction_repository

    def extract_user_features(self, db, user_id: int) -> Dict[str, Any]:
        """Extract comprehensive user features for recommendation"""
        # Get user profile data
        user_data = self.user_repository.get_user_by_id(db, user_id)
        if not user_data:
            return {}

        # Get user interests
        interests = self.user_repository.get_user_interests(db, user_id)

        # Get user friends
        friends = self.user_repository.get_user_friends(db, user_id)

        # Get user activity features
        activity = self.user_repository.get_user_activity_features(db, user_id)

        # Get recent interactions
        interactions = self.interaction_repository.get_user_content_interactions(db, user_id, days=30)

        # Compute derived features
        derived_features = self._compute_derived_features(interactions)

        # Combine all features
        features = {
            "user_id": user_id,
            "profile": {
                "age": user_data.get("age"),
                "location": user_data.get("city_of_residence"),
                "days_since_joined": (datetime.now() - user_data.get("date_joined")).days if user_data.get(
                    "date_joined") else None
            },
            "interests": interests,
            "social": {
                "friend_count": len(friends),
                "friends": friends
            },
            "activity": activity,
            "interaction_patterns": derived_features
        }

        return features

    def create_user_embedding(self, db, user_id: int) -> List[float]:
        """Create user embedding vector for similarity comparison"""
        # Extract user features
        features = self.extract_user_features(db, user_id)
        if not features:
            return []

        # Convert categorical features to numerical embeddings
        # This is a simplified version - in practice, use more sophisticated embedding techniques

        # Interest embedding
        interest_embedding = self._compute_interest_embedding(features.get("interests", []))

        # Activity embedding
        activity_embedding = self._compute_activity_embedding(features.get("activity", {}))

        # Interaction embedding
        interaction_embedding = self._compute_interaction_embedding(features.get("interaction_patterns", {}))

        # Combine embeddings
        combined_embedding = interest_embedding + activity_embedding + interaction_embedding

        # Normalize
        norm = np.linalg.norm(combined_embedding)
        if norm > 0:
            combined_embedding = [x / norm for x in combined_embedding]

        # Store embedding
        self.user_repository.update_user_embedding(
            db,
            user_id,
            combined_embedding,
            embedding_type="combined"
        )

        return combined_embedding

    def _compute_derived_features(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute derived features from interaction data"""
        if not interactions:
            return {
                "reaction_distribution": {},
                "activity_times": {
                    "morning": 0,
                    "afternoon": 0,
                    "evening": 0,
                    "night": 0
                },
                "engagement_level": "low"
            }

        # Count reaction types
        reaction_counts = {}
        for interaction in interactions:
            if interaction["interaction_type"] == "reaction":
                reaction_type = interaction["interaction_subtype"]
                reaction_counts[reaction_type] = reaction_counts.get(reaction_type, 0) + 1

        # Normalize reaction distribution
        total_reactions = sum(reaction_counts.values()) if reaction_counts else 1
        reaction_distribution = {k: v / total_reactions for k, v in reaction_counts.items()}

        # Analyze activity times
        activity_times = {
            "morning": 0,  # 6-12
            "afternoon": 0,  # 12-18
            "evening": 0,  # 18-24
            "night": 0  # 0-6
        }

        for interaction in interactions:
            hour = interaction["interaction_time"].hour
            if 6 <= hour < 12:
                activity_times["morning"] += 1
            elif 12 <= hour < 18:
                activity_times["afternoon"] += 1
            elif 18 <= hour < 24:
                activity_times["evening"] += 1
            else:
                activity_times["night"] += 1

        # Normalize activity times
        total_activities = sum(activity_times.values()) if sum(activity_times.values()) > 0 else 1
        activity_times = {k: v / total_activities for k, v in activity_times.items()}

        # Determine engagement level
        engagement_level = "low"
        if len(interactions) > 50:
            engagement_level = "high"
        elif len(interactions) > 20:
            engagement_level = "medium"

        return {
            "reaction_distribution": reaction_distribution,
            "activity_times": activity_times,
            "engagement_level": engagement_level
        }

    def _compute_interest_embedding(self, interests: List[str]) -> List[float]:
        """Convert interests to embedding vector"""
        # This is a simplified version - in practice, use pre-trained embeddings or learn them
        # For demonstration, we'll create a simple one-hot-like encoding

        # Common interest categories
        categories = [
            "technology", "sports", "music", "movies", "books", "fashion",
            "food", "travel", "gaming", "fitness", "art", "photography"
        ]

        # Initialize embedding
        embedding = [0.0] * len(categories)

        # Set values for matching interests
        for interest in interests:
            interest_lower = interest.lower()
            for i, category in enumerate(categories):
                if category in interest_lower:
                    embedding[i] = 1.0

        return embedding

    def _compute_activity_embedding(self, activity: Dict[str, Any]) -> List[float]:
        """Convert activity metrics to embedding vector"""
        # Extract key metrics with defaults
        post_freq = activity.get("post_frequency", 0)
        comment_freq = activity.get("comment_frequency", 0)
        reaction_freq = activity.get("reaction_frequency", 0)
        share_freq = activity.get("share_frequency", 0)
        active_days = activity.get("active_days_per_week", 0)

        # Normalize values
        max_post = 10  # Assume 10 posts per week is maximum
        max_comment = 50  # Assume 50 comments per week is maximum
        max_reaction = 100  # Assume 100 reactions per week is maximum
        max_share = 20  # Assume 20 shares per week is maximum

        # Create embedding
        embedding = [
            min(post_freq / max_post, 1.0),
            min(comment_freq / max_comment, 1.0),
            min(reaction_freq / max_reaction, 1.0),
            min(share_freq / max_share, 1.0),
            active_days / 7.0  # Days per week normalized
        ]

        return embedding

    def _compute_interaction_embedding(self, interaction_patterns: Dict[str, Any]) -> List[float]:
        """Convert interaction patterns to embedding vector"""
        # Extract patterns
        reaction_dist = interaction_patterns.get("reaction_distribution", {})
        activity_times = interaction_patterns.get("activity_times", {})
        engagement = interaction_patterns.get("engagement_level", "low")

        # Map reaction preferences
        reaction_embedding = [
            reaction_dist.get("like", 0.0),
            reaction_dist.get("love", 0.0),
            reaction_dist.get("laugh", 0.0),
            reaction_dist.get("congratulate", 0.0),
            reaction_dist.get("shocked", 0.0),
            reaction_dist.get("sad", 0.0),
            reaction_dist.get("angry", 0.0)
        ]

        # Map activity times
        time_embedding = [
            activity_times.get("morning", 0.0),
            activity_times.get("afternoon", 0.0),
            activity_times.get("evening", 0.0),
            activity_times.get("night", 0.0)
        ]

        # Map engagement level
        engagement_value = 0.0
        if engagement == "medium":
            engagement_value = 0.5
        elif engagement == "high":
            engagement_value = 1.0

        # Combine all
        return reaction_embedding + time_embedding + [engagement_value]
