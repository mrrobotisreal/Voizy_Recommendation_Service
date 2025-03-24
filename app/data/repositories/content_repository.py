from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

from app.data.schemas import Post, PostReaction, Comment, PostShare, PostHashtag, Hashtag, ContentEmbedding


class ContentRepository:
    """Repository for content-related data operations"""

    def get_content_by_id(self, db: Session, content_id: int) -> Optional[Dict[str, Any]]:
        """Get content by ID with aggregated metrics"""
        post = db.query(Post).filter(Post.post_id == content_id).first()

        if not post:
            return None

        # Get reaction counts
        reaction_count = db.query(func.count(PostReaction.post_reaction_id)) \
            .filter(PostReaction.post_id == content_id) \
            .scalar()

        # Get comment counts
        comment_count = db.query(func.count(Comment.comment_id)) \
            .filter(Comment.post_id == content_id) \
            .scalar()

        # Get share counts
        share_count = db.query(func.count(PostShare.share_id)) \
            .filter(PostShare.post_id == content_id) \
            .scalar()

        # Get hashtags
        hashtags = db.query(Hashtag.tag) \
            .join(PostHashtag, PostHashtag.hashtag_id == Hashtag.hashtag_id) \
            .filter(PostHashtag.post_id == content_id) \
            .all()

        hashtag_list = [tag[0] for tag in hashtags]

        # Format content data
        content_data = {
            "content_id": post.post_id,
            "user_id": post.user_id,
            "to_user_id": post.to_user_id,
            "original_post_id": post.original_post_id,
            "content_text": post.content_text,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "location_name": post.location_name,
            "location_lat": post.location_lat,
            "location_lng": post.location_lng,
            "impressions": post.impressions,
            "views": post.views,
            "is_poll": post.is_poll,
            "total_reactions": reaction_count,
            "total_comments": comment_count,
            "total_shares": share_count,
            "hashtags": hashtag_list
        }

        return content_data

    def get_content_embedding(self, db: Session, content_id: int, embedding_type: str = "combined") -> Optional[
        List[float]]:
        """Get a content's embedding vector"""
        embedding = (
            db.query(ContentEmbedding)
            .filter(
                ContentEmbedding.content_id == content_id,
                ContentEmbedding.embedding_type == embedding_type
            )
            .order_by(ContentEmbedding.updated_at.desc())
            .first()
        )

        if embedding and embedding.embedding_vector:
            return json.loads(embedding.embedding_vector)

        return None

    def update_content_embedding(self, db: Session, content_id: int, embedding_vector: List[float],
                                 embedding_type: str = "combined") -> None:
        """Update or create a content embedding vector"""
        # Check if embedding exists
        embedding = (
            db.query(ContentEmbedding)
            .filter(
                ContentEmbedding.content_id == content_id,
                ContentEmbedding.embedding_type == embedding_type
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
            new_embedding = ContentEmbedding(
                content_id=content_id,
                embedding_vector=vector_json,
                embedding_type=embedding_type
            )
            db.add(new_embedding)

        db.commit()

    def get_trending_content(self, db: Session, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trending content based on engagement metrics"""
        # Calculate trending score based on recency and engagement
        date_cutoff = datetime.utcnow() - timedelta(days=days)

        trending_posts = (
            db.query(
                Post.post_id,
                Post.user_id,
                Post.content_text,
                Post.created_at,
                Post.impressions,
                Post.views,
                func.count(PostReaction.post_reaction_id).label("reaction_count"),
                func.count(Comment.comment_id).label("comment_count"),
                func.count(PostShare.share_id).label("share_count")
            )
            .outerjoin(PostReaction, PostReaction.post_id == Post.post_id)
            .outerjoin(Comment, Comment.post_id == Post.post_id)
            .outerjoin(PostShare, PostShare.post_id == Post.post_id)
            .filter(Post.created_at >= date_cutoff)
            .group_by(Post.post_id)
            .order_by(
                # Custom trending algorithm:
                # (3*shares + 2*comments + 1*reactions) / (age_in_hours + 2)^1.5
                desc(
                    (func.count(PostShare.share_id) * 3 +
                     func.count(Comment.comment_id) * 2 +
                     func.count(PostReaction.post_reaction_id)) /
                    func.power(
                        func.timestampdiff(text("HOUR"), Post.created_at, func.now()) + 2,
                        1.5
                    )
                )
            )
            .limit(limit)
            .all()
        )

        # Format results
        result = []
        for post in trending_posts:
            post_dict = {
                "content_id": post.post_id,
                "user_id": post.user_id,
                "content_text": post.content_text,
                "created_at": post.created_at,
                "impressions": post.impressions,
                "views": post.views,
                "reaction_count": post.reaction_count,
                "comment_count": post.comment_count,
                "share_count": post.share_count,
                "engagement_score": (post.share_count * 3 + post.comment_count * 2 + post.reaction_count)
            }
            result.append(post_dict)

        return result

    def get_content_by_hashtag(self, db: Session, hashtag: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get content by hashtag"""
        posts = (
            db.query(Post)
            .join(PostHashtag, PostHashtag.post_id == Post.post_id)
            .join(Hashtag, Hashtag.hashtag_id == PostHashtag.hashtag_id)
            .filter(Hashtag.tag == hashtag)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for post in posts:
            post_data = self.get_content_by_id(db, post.post_id)
            if post_data:
                result.append(post_data)

        return result

    def get_similar_content(self, db: Session, content_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get similar content to the given content_id"""
        # Get source content
        source_post = self.get_content_by_id(db, content_id)
        if not source_post:
            return []

        # Get hashtags of source post
        source_hashtags = (
            db.query(Hashtag.tag)
            .join(PostHashtag, PostHashtag.hashtag_id == Hashtag.hashtag_id)
            .filter(PostHashtag.post_id == content_id)
            .all()
        )

        source_hashtag_ids = (
            db.query(PostHashtag.hashtag_id)
            .filter(PostHashtag.post_id == content_id)
            .all()
        )

        source_hashtag_ids = [h[0] for h in source_hashtag_ids]

        if not source_hashtag_ids:
            # If no hashtags, find content with similar text
            # This is a placeholder - implement with text similarity
            return []

        # Find posts with same hashtags
        similar_posts = (
            db.query(
                Post.post_id,
                func.count(PostHashtag.hashtag_id).label("shared_hashtags")
            )
            .join(PostHashtag, PostHashtag.post_id == Post.post_id)
            .filter(
                Post.post_id != content_id,
                PostHashtag.hashtag_id.in_(source_hashtag_ids)
            )
            .group_by(Post.post_id)
            .order_by(desc("shared_hashtags"))
            .limit(limit)
            .all()
        )

        # Get full post data
        result = []
        for post in similar_posts:
            post_data = self.get_content_by_id(db, post.post_id)
            if post_data:
                post_data["shared_hashtags"] = post.shared_hashtags
                result.append(post_data)

        return result
