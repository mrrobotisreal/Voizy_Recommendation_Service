import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re


class ContentFeatureExtractor:
    """Extracts features from content data for recommendation models"""

    def __init__(self, content_repository):
        self.content_repository = content_repository

    def extract_content_features(self, db, content_id: int) -> Dict[str, Any]:
        """Extract comprehensive content features for recommendation"""
        # Get content data
        content_data = self.content_repository.get_content_by_id(db, content_id)
        if not content_data:
            return {}

        # Text features
        text_features = self._extract_text_features(content_data.get("content_text", ""))

        # Engagement features
        engagement_features = {
            "impressions": content_data.get("impressions", 0),
            "views": content_data.get("views", 0),
            "total_reactions": content_data.get("total_reactions", 0),
            "total_comments": content_data.get("total_comments", 0),
            "total_shares": content_data.get("total_shares", 0),
            "engagement_rate": self._calculate_engagement_rate(content_data)
        }

        # Temporal features
        temporal_features = self._extract_temporal_features(content_data.get("created_at"))

        # Location features
        location_features = {}
        if content_data.get("location_name"):
            location_features = {
                "has_location": True,
                "location_name": content_data.get("location_name"),
                "coordinates": [
                    content_data.get("location_lat"),
                    content_data.get("location_lng")
                ] if content_data.get("location_lat") else None
            }
        else:
            location_features = {
                "has_location": False
            }

        # Content type features
        content_type_features = {
            "is_poll": content_data.get("is_poll", False),
            "is_repost": content_data.get("original_post_id") is not None,
            "has_hashtags": len(content_data.get("hashtags", [])) > 0,
            "hashtag_count": len(content_data.get("hashtags", [])),
            "hashtags": content_data.get("hashtags", [])
        }

        # Combined features
        features = {
            "content_id": content_id,
            "user_id": content_data.get("user_id"),
            "text_features": text_features,
            "engagement": engagement_features,
            "temporal": temporal_features,
            "location": location_features,
            "content_type": content_type_features
        }

        return features

    def create_content_embedding(self, db, content_id: int) -> List[float]:
        """Create content embedding vector for similarity comparison"""
        # Extract content features
        features = self.extract_content_features(db, content_id)
        if not features:
            return []

        # Text embedding (simplified - in practice use NLP models)
        text_embedding = self._compute_text_embedding(features.get("text_features", {}))

        # Engagement embedding
        engagement_embedding = self._compute_engagement_embedding(features.get("engagement", {}))

        # Hashtag embedding
        hashtag_embedding = self._compute_hashtag_embedding(features.get("content_type", {}).get("hashtags", []))

        # Combine embeddings
        combined_embedding = text_embedding + engagement_embedding + hashtag_embedding

        # Normalize
        norm = np.linalg.norm(combined_embedding)
        if norm > 0:
            combined_embedding = [x / norm for x in combined_embedding]

        # Store embedding
        self.content_repository.update_content_embedding(
            db,
            content_id,
            combined_embedding,
            embedding_type="combined"
        )

        return combined_embedding

    def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract features from content text"""
        if not text:
            return {
                "length": 0,
                "word_count": 0,
                "has_url": False,
                "has_mention": False,
                "sentiment": "neutral",
                "topics": []
            }

        # Basic text stats
        word_count = len(text.split())

        # Check for URLs
        has_url = bool(re.search(r'https?://\S+', text))

        # Check for mentions
        has_mention = bool(re.search(r'@\w+', text))

        # Sentiment analysis (simplified)
        sentiment = self._analyze_sentiment(text)

        # Topic extraction (simplified)
        topics = self._extract_topics(text)

        return {
            "length": len(text),
            "word_count": word_count,
            "has_url": has_url,
            "has_mention": has_mention,
            "sentiment": sentiment,
            "topics": topics
        }

    def _analyze_sentiment(self, text: str) -> str:
        """Simplified sentiment analysis"""
        # In practice, use a proper NLP model for sentiment analysis
        positive_words = ["good", "great", "awesome", "excellent", "happy", "love", "best", "amazing"]
        negative_words = ["bad", "terrible", "awful", "worst", "hate", "sad", "poor", "disappointing"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_topics(self, text: str) -> List[str]:
        """Simplified topic extraction"""
        # In practice, use NLP models like LDA or word embeddings
        topic_keywords = {
            "technology": ["tech", "software", "app", "computer", "code", "programming"],
            "sports": ["game", "team", "player", "score", "win", "sports"],
            "entertainment": ["movie", "show", "music", "actor", "song", "artist"],
            "politics": ["government", "election", "policy", "president", "vote"],
            "business": ["company", "market", "stock", "investment", "business"]
        }

        text_lower = text.lower()
        topics = []

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _extract_temporal_features(self, created_at: Optional[datetime]) -> Dict[str, Any]:
        """Extract temporal features from content creation time"""
        if not created_at:
            return {
                "age_days": None,
                "day_of_week": None,
                "hour_of_day": None,
                "is_weekend": None
            }

        now = datetime.utcnow()
        age_days = (now - created_at).days

        return {
            "age_days": age_days,
            "day_of_week": created_at.weekday(),
            "hour_of_day": created_at.hour,
            "is_weekend": created_at.weekday() >= 5  # 5 = Saturday, 6 = Sunday
        }

    def _calculate_engagement_rate(self, content_data: Dict[str, Any]) -> float:
        """Calculate engagement rate"""
        impressions = content_data.get("impressions", 0)
        if impressions == 0:
            return 0.0

        total_engagement = (
                content_data.get("total_reactions", 0) +
                content_data.get("total_comments", 0) * 2 +  # Comments weighted higher
                content_data.get("total_shares", 0) * 3  # Shares weighted highest
        )

        return total_engagement / impressions

    def _compute_text_embedding(self, text_features: Dict[str, Any]) -> List[float]:
        """Convert text features to embedding vector"""
        # In practice, use pre-trained text embeddings from models like BERT

        # Sentiment encoding
        sentiment_value = 0.0  # neutral
        if text_features.get("sentiment") == "positive":
            sentiment_value = 1.0
        elif text_features.get("sentiment") == "negative":
            sentiment_value = -1.0

        # Topic encoding (simplified)
        topic_embedding = [0.0] * 5  # 5 topics
        topics = text_features.get("topics", [])

        topic_indices = {
            "technology": 0,
            "sports": 1,
            "entertainment": 2,
            "politics": 3,
            "business": 4
        }

        for topic in topics:
            if topic in topic_indices:
                topic_embedding[topic_indices[topic]] = 1.0

        # Text characteristics
        text_chars = [
            min(text_features.get("length", 0) / 500, 1.0),  # Normalize length
            min(text_features.get("word_count", 0) / 100, 1.0),  # Normalize word count
            1.0 if text_features.get("has_url", False) else 0.0,
            1.0 if text_features.get("has_mention", False) else 0.0
        ]

        return [sentiment_value] + topic_embedding + text_chars

    def _compute_engagement_embedding(self, engagement: Dict[str, Any]) -> List[float]:
        """Convert engagement metrics to embedding vector"""
        # Normalize engagement metrics
        max_impressions = 10000
        max_reactions = 500
        max_comments = 100
        max_shares = 50

        impressions_norm = min(engagement.get("impressions", 0) / max_impressions, 1.0)
        views_norm = min(engagement.get("views", 0) / max_impressions, 1.0)
        reactions_norm = min(engagement.get("total_reactions", 0) / max_reactions, 1.0)
        comments_norm = min(engagement.get("total_comments", 0) / max_comments, 1.0)
        shares_norm = min(engagement.get("total_shares", 0) / max_shares, 1.0)

        engagement_rate = engagement.get("engagement_rate", 0.0)

        return [impressions_norm, views_norm, reactions_norm, comments_norm, shares_norm, engagement_rate]

    def _compute_hashtag_embedding(self, hashtags: List[str]) -> List[float]:
        """Convert hashtags to embedding vector"""
        # Common hashtag categories (simplified)
        categories = [
            "tech", "sport", "music", "movie", "book", "fashion",
            "food", "travel", "game", "fitness", "art", "photo",
            "news", "politics", "business", "science", "health"
        ]

        # Initialize embedding
        embedding = [0.0] * len(categories)

        # Set values for matching categories
        for hashtag in hashtags:
            hashtag_lower = hashtag.lower()
            for i, category in enumerate(categories):
                if category in hashtag_lower:
                    embedding[i] = 1.0

        return embedding
