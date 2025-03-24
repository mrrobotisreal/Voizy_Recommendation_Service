from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

from app.data.schemas import User, UserProfile, UserInterest, Interest, Friendship, UserEmbedding


class UserRepository:
    """Repository for user-related data operations"""

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID with profile information"""
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            return None

        # Get profile data
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        # Format user data
        user_data = {
            "user_id": user.user_id,
            "username": user.username,
            "created_at": user.created_at,
        }

        # Add profile data if exists
        if profile:
            user_data.update({
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "preferred_name": profile.preferred_name,
                "age": self._calculate_age(profile.birth_date) if profile.birth_date else None,
                "city_of_residence": profile.city_of_residence,
                "place_of_work": profile.place_of_work,
                "date_joined": profile.date_joined
            })

        return user_data

    def get_user_interests(self, db: Session, user_id: int) -> List[str]:
        """Get user interests as a list of interest names"""
        interests = (
            db.query(Interest.name)
            .join(UserInterest, UserInterest.interest_id == Interest.interest_id)
            .filter(UserInterest.user_id == user_id)
            .all()
        )

        return [interest[0] for interest in interests]

    def get_user_friends(self, db: Session, user_id: int) -> List[int]:
        """Get list of user's friends (accepted friendships)"""
        friends = (
            db.query(Friendship.friend_id)
            .filter(
                Friendship.user_id == user_id,
                Friendship.status == "accepted"
            )
            .union(
                db.query(Friendship.user_id)
                .filter(
                    Friendship.friend_id == user_id,
                    Friendship.status == "accepted"
                )
            )
            .all()
        )

        return [friend[0] for friend in friends]

    def get_user_embedding(self, db: Session, user_id: int, embedding_type: str = "combined") -> Optional[List[float]]:
        """Get a user's embedding vector"""
        embedding = (
            db.query(UserEmbedding)
            .filter(
                UserEmbedding.user_id == user_id,
                UserEmbedding.embedding_type == embedding_type
            )
            .order_by(UserEmbedding.updated_at.desc())
            .first()
        )

        if embedding and embedding.embedding_vector:
            return json.loads(embedding.embedding_vector)

        return None

    def update_user_embedding(self, db: Session, user_id: int, embedding_vector: List[float],
                              embedding_type: str = "combined") -> None:
        """Update or create a user embedding vector"""
        # Check if embedding exists
        embedding = (
            db.query(UserEmbedding)
            .filter(
                UserEmbedding.user_id == user_id,
                UserEmbedding.embedding_type == embedding_type
            )
            .first()
        )

        # Convert vector to JSON string
        vector_json = json.dumps(embedding_vector)

        if embedding:
            # Update existing embedding
            embedding.embedding_vector = vector_json
            embedding.updated_at = datetime.utcnow()
        else:
            # Create new embedding
            new_embedding = UserEmbedding(
                user_id=user_id,
                embedding_vector=vector_json,
                embedding_type=embedding_type
            )
            db.add(new_embedding)

        db.commit()

    def get_users_with_similar_interests(self, db: Session, user_id: int, limit: int = 20) -> List[int]:
        """Find users with similar interests"""
        # Get user's interests
        user_interests = (
            db.query(UserInterest.interest_id)
            .filter(UserInterest.user_id == user_id)
            .subquery()
        )

        # Find users who share interests with this user
        similar_users = (
            db.query(
                UserInterest.user_id,
                func.count(UserInterest.interest_id).label("shared_interests")
            )
            .filter(
                UserInterest.interest_id.in_(user_interests),
                UserInterest.user_id != user_id
            )
            .group_by(UserInterest.user_id)
            .order_by(desc("shared_interests"))
            .limit(limit)
            .all()
        )

        return [user[0] for user in similar_users]

    def get_similar_users_by_embedding(self, db: Session, embedding_vector: List[float], limit: int = 20) -> List[int]:
        """
        Find similar users based on embedding vector
        Note: This is a placeholder. In a real implementation, you would use
        a vector database or approximate nearest neighbor search.
        """
        # Placeholder implementation - in practice, use a vector database or specialized search
        return []

    def _calculate_age(self, birth_date):
        """Calculate age from birth date"""
        if not birth_date:
            return None

        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    def get_user_activity_features(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get user activity features for recommendation"""
        # This is a placeholder - implement with actual queries to get activity metrics
        return {
            "post_frequency": 0,
            "comment_frequency": 0,
            "reaction_frequency": 0,
            "share_frequency": 0,
            "active_days_per_week": 0,
            "avg_session_duration": 0
        }
