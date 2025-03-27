from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text, literal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

from app.data.schemas import (
    User, Post, PostReaction, Comment, PostShare,
    UserContentInteraction, AnalyticsEvent
)


class InteractionRepository:
    """Repository for interaction-related data operations"""

    def get_user_content_interactions(self, db: Session, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get user-content interactions within a time period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get reactions
        reactions = (
            db.query(
                PostReaction.post_id,
                PostReaction.reaction_type,
                PostReaction.reacted_at.label("interaction_time"),
                literal("reaction").label("interaction_type")
            )
            .filter(
                PostReaction.user_id == user_id,
                PostReaction.reacted_at >= cutoff_date
            )
        )

        # Get comments
        comments = (
            db.query(
                Comment.post_id,
                literal("comment").label("interaction_type"),
                Comment.created_at.label("interaction_time"),
                literal("comment").label("reaction_type")
            )
            .filter(
                Comment.user_id == user_id,
                Comment.created_at >= cutoff_date
            )
        )

        # Get shares
        shares = (
            db.query(
                PostShare.post_id,
                literal("share").label("interaction_type"),
                PostShare.shared_at.label("interaction_time"),
                literal("share").label("reaction_type")
            )
            .filter(
                PostShare.user_id == user_id,
                PostShare.shared_at >= cutoff_date
            )
        )

        combined_query = reactions.union(comments).union(shares).subquery()

        final_query = db.query(combined_query).order_by(combined_query.c.interaction_time.desc())

        # Combine all interactions
        combined = final_query.all()

        # Format results
        result = []
        for interaction in combined:
            interaction_dict = {
                "content_id": interaction.post_id,
                "interaction_type": interaction.interaction_type,
                "interaction_subtype": interaction.reaction_type,
                "interaction_time": interaction.interaction_time
            }
            result.append(interaction_dict)

        return result

    def get_user_content_interaction_matrix(self, db: Session, max_users: int = 1000, max_content: int = 5000) -> Dict[
        str, Any]:
        """
        Get user-content interaction matrix for collaborative filtering
        Returns a sparse matrix representation of user-content interactions
        """
        # Get most active users
        active_users = (
            db.query(
                UserContentInteraction.user_id,
                func.count(UserContentInteraction.content_id).label("interaction_count")
            )
            .group_by(UserContentInteraction.user_id)
            .order_by(desc("interaction_count"))
            .limit(max_users)
            .all()
        )

        active_user_ids = [u[0] for u in active_users]

        # Get most interacted content
        popular_content = (
            db.query(
                UserContentInteraction.content_id,
                func.count(UserContentInteraction.user_id).label("interaction_count")
            )
            .group_by(UserContentInteraction.content_id)
            .order_by(desc("interaction_count"))
            .limit(max_content)
            .all()
        )

        popular_content_ids = [c[0] for c in popular_content]

        # Get interaction matrix
        interactions = (
            db.query(
                UserContentInteraction.user_id,
                UserContentInteraction.content_id,
                func.avg(UserContentInteraction.interaction_value).label("avg_value")
            )
            .filter(
                UserContentInteraction.user_id.in_(active_user_ids),
                UserContentInteraction.content_id.in_(popular_content_ids)
            )
            .group_by(UserContentInteraction.user_id, UserContentInteraction.content_id)
            .all()
        )

        # Create sparse matrix representation
        matrix = {
            "users": active_user_ids,
            "content": popular_content_ids,
            "interactions": [
                {"user_id": i.user_id, "content_id": i.content_id, "value": i.avg_value}
                for i in interactions
            ]
        }

        return matrix

    def record_content_view(self, db: Session, user_id: int, content_id: int) -> None:
        """Record a content view interaction"""
        # Update post views count
        db.query(Post).filter(Post.post_id == content_id).update(
            {Post.views: Post.views + 1},
            synchronize_session=False
        )

        # Record in user_content_interactions
        interaction = UserContentInteraction(
            user_id=user_id,
            content_id=content_id,
            interaction_type="view",
            interaction_value=1.0
        )
        db.add(interaction)

        # Record analytics event
        event = AnalyticsEvent(
            user_id=user_id,
            event_type="content_view",
            object_type="post",
            object_id=content_id
        )
        db.add(event)

        db.commit()

    def record_recommendation_interaction(self, db: Session, user_id: int, content_id: int,
                                          interaction_type: str, model_id: int) -> None:
        """Record an interaction with a recommendation"""
        # Update recommendation record
        if interaction_type == "click":
            db.query(UserContentInteraction).filter(
                UserContentInteraction.user_id == user_id,
                UserContentInteraction.content_id == content_id,
                UserContentInteraction.model_id == model_id
            ).update({"was_clicked": True})
        elif interaction_type == "view":
            db.query(UserContentInteraction).filter(
                UserContentInteraction.user_id == user_id,
                UserContentInteraction.content_id == content_id,
                UserContentInteraction.model_id == model_id
            ).update({"is_seen": True})

        # Record in user_content_interactions
        interaction = UserContentInteraction(
            user_id=user_id,
            content_id=content_id,
            interaction_type=interaction_type,
            interaction_value=1.0 if interaction_type == "click" else 0.5
        )
        db.add(interaction)

        # Record analytics event
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=f"recommendation_{interaction_type}",
            object_type="post",
            object_id=content_id,
            metadata=json.dumps({"model_id": model_id})
        )
        db.add(event)

        db.commit()
