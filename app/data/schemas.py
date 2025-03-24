from sqlalchemy import Column, Integer, String, Boolean, Text, Float, ForeignKey, Enum, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.data.db import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    salt = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="user")
    interests = relationship("UserInterest", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    preferred_name = Column(String(100))
    birth_date = Column(DateTime)
    city_of_residence = Column(String(255))
    place_of_work = Column(String(255))
    date_joined = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")


class Interest(Base):
    __tablename__ = "interests"

    interest_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)

    # Relationships
    users = relationship("UserInterest", back_populates="interest")


class UserInterest(Base):
    __tablename__ = "user_interests"

    user_interest_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    interest_id = Column(Integer, ForeignKey("interests.interest_id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="interests")
    interest = relationship("Interest", back_populates="users")


class Friendship(Base):
    __tablename__ = "friendships"

    friendship_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("pending", "accepted", "blocked"), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class Group(Base):
    __tablename__ = "groups_table"

    group_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    privacy = Column(Enum("public", "private", "closed"), default="public")
    creator_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    members = relationship("GroupMember", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    group_member_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups_table.group_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum("member", "moderator", "admin"), default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="members")


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    to_user_id = Column(Integer, default=-1, nullable=False)
    original_post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="SET NULL"), nullable=True)
    impressions = Column(Integer, default=0, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    content_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    location_name = Column(String(255))
    location_lat = Column(Float)
    location_lng = Column(Float)
    is_poll = Column(Boolean, default=False)
    poll_question = Column(String(255))
    poll_duration_type = Column(Enum("hours", "days", "weeks"), default="days")
    poll_duration_length = Column(Integer, default=1)
    poll_end_datetime = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="posts")
    original_post = relationship("Post", remote_side=[post_id])
    reactions = relationship("PostReaction", back_populates="post")
    comments = relationship("Comment", back_populates="post")
    shares = relationship("PostShare", back_populates="post")
    hashtags = relationship("PostHashtag", back_populates="post")
    media = relationship("PostMedia", back_populates="post")


class Hashtag(Base):
    __tablename__ = "hashtags"

    hashtag_id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    posts = relationship("PostHashtag", back_populates="hashtag")


class PostHashtag(Base):
    __tablename__ = "post_hashtags"

    post_hashtag_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    hashtag_id = Column(Integer, ForeignKey("hashtags.hashtag_id", ondelete="CASCADE"), nullable=False)

    # Relationships
    post = relationship("Post", back_populates="hashtags")
    hashtag = relationship("Hashtag", back_populates="posts")


class PostReaction(Base):
    __tablename__ = "post_reactions"

    post_reaction_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    reaction_type = Column(Enum("like", "love", "laugh", "congratulate", "shocked", "sad", "angry"), nullable=False)
    reacted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship("Post", back_populates="reactions")


class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    post = relationship("Post", back_populates="comments")
    reactions = relationship("CommentReaction", back_populates="comment")


class CommentReaction(Base):
    __tablename__ = "comment_reactions"

    comment_reaction_id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.comment_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    reaction_type = Column(Enum("like", "love", "laugh", "congratulate", "shocked", "sad", "angry"), nullable=False)
    reacted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    comment = relationship("Comment", back_populates="reactions")


class PostShare(Base):
    __tablename__ = "post_shares"

    share_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    shared_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship("Post", back_populates="shares")


class PostMedia(Base):
    __tablename__ = "post_media"

    media_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    media_url = Column(String(255), nullable=False)
    media_type = Column(Enum("image", "video"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    post = relationship("Post", back_populates="media")


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    event_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)
    object_type = Column(String(100))
    object_id = Column(Integer)
    event_time = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)


# Add additional tables for recommendations

class UserEmbedding(Base):
    __tablename__ = "user_embeddings"

    embedding_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    embedding_vector = Column(JSON, nullable=False)  # Store as JSON array
    embedding_type = Column(String(50), nullable=False)  # e.g., "interest", "behavior", "combined"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContentEmbedding(Base):
    __tablename__ = "content_embeddings"

    embedding_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    embedding_vector = Column(JSON, nullable=False)  # Store as JSON array
    embedding_type = Column(String(50), nullable=False)  # e.g., "text", "hashtag", "combined"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserContentInteraction(Base):
    __tablename__ = "user_content_interactions"

    interaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # e.g., "view", "click", "reaction", "comment", "share"
    interaction_value = Column(Float, default=1.0)  # Strength/weight of the interaction
    created_at = Column(DateTime, default=datetime.utcnow)


class RecommendationModel(Base):
    __tablename__ = "recommendation_models"

    model_id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(100), nullable=False)  # e.g., "collaborative", "content_based", "hybrid"
    model_version = Column(String(50), nullable=False)
    model_weights = Column(JSON)  # Store model parameters as JSON
    metrics = Column(JSON)  # Store evaluation metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)


class UserRecommendation(Base):
    __tablename__ = "user_recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    model_id = Column(Integer, ForeignKey("recommendation_models.model_id"), nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(JSON)  # Store explanation factors as JSON
    is_seen = Column(Boolean, default=False)
    was_clicked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
