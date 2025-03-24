from typing import List, Dict, Any, Union
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HybridRecommender:
    """
    Hybrid recommendation model combining collaborative filtering,
    content-based filtering, and contextual factors
    """

    def __init__(self, db, user_repository, content_repository, interaction_repository):
        self.db = db
        self.user_repository = user_repository
        self.content_repository = content_repository
        self.interaction_repository = interaction_repository
        self.model_weights = {
            "collaborative": 0.4,
            "content_based": 0.4,
            "popularity": 0.1,
            "recency": 0.1
        }
        self.version = "1.0.0"

    def recommend(self,
                  user_id: int,
                  user_features: Dict[str, Any] = None,
                  exclude_content_ids: List[int] = None,
                  filters: Dict[str, Any] = None,
                  limit: int = 20) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations for a user

        Args:
            user_id: User identifier
            user_features: Pre-computed user features (optional)
            exclude_content_ids: Content IDs to exclude (e.g., already seen)
            filters: Content filters to apply
            limit: Maximum number of recommendations to return

        Returns:
            List of recommendation objects with content_id, score, and factors
        """
        try:
            logger.info(f"Generating recommendations for user {user_id}")

            # Initialize results
            recommendations = []
            exclude_ids = set(exclude_content_ids or [])

            # Load user features if not provided
            if not user_features:
                user_embedding = self.user_repository.get_user_embedding(self.db, user_id)
                if not user_embedding:
                    # Create user embedding if not exists
                    from app.ml.features.user_features import UserFeatureExtractor
                    feature_extractor = UserFeatureExtractor(self.user_repository, self.interaction_repository)
                    user_embedding = feature_extractor.create_user_embedding(self.db, user_id)
            else:
                # Use pre-computed features
                user_embedding = user_features.get("embedding", [])

            # Get candidate content through different strategies
            candidates = self._get_recommendation_candidates(user_id, exclude_ids, filters)

            # Score candidates using hybrid approach
            scored_candidates = self._score_candidates(user_id, user_embedding, candidates)

            # Apply diversity and relevance balancing
            final_recommendations = self._diversify_recommendations(scored_candidates)

            # Prepare response
            recommendations = []
            for i, rec in enumerate(final_recommendations[:limit]):
                content_data = self.content_repository.get_content_by_id(self.db, rec["content_id"])
                if not content_data:
                    continue

                # Format recommendation
                recommendation = {
                    "content_id": rec["content_id"],
                    "score": rec["score"],
                    "factors": rec["factors"]
                }
                recommendations.append(recommendation)

            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _get_recommendation_candidates(self,
                                       user_id: int,
                                       exclude_ids: set,
                                       filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get candidate content for recommendations"""
        candidates = []

        # 1. Content-based candidates
        content_based_candidates = self._get_content_based_candidates(user_id, exclude_ids)
        candidates.extend(content_based_candidates)

        # 2. Collaborative filtering candidates
        cf_candidates = self._get_collaborative_candidates(user_id, exclude_ids)
        candidates.extend(cf_candidates)

        # 3. Social graph candidates
        social_candidates = self._get_social_candidates(user_id, exclude_ids)
        candidates.extend(social_candidates)

        # 4. Trending/popular candidates
        trending_candidates = self._get_trending_candidates(exclude_ids)
        candidates.extend(trending_candidates)

        # Remove duplicates
        seen_ids = set()
        unique_candidates = []

        for candidate in candidates:
            content_id = candidate["content_id"]
            if content_id not in seen_ids:
                seen_ids.add(content_id)
                unique_candidates.append(candidate)

        # Apply filters
        if filters:
            filtered_candidates = []
            for candidate in unique_candidates:
                # Apply content type filter
                if "content_types" in filters:
                    content_data = self.content_repository.get_content_by_id(self.db, candidate["content_id"])
                    if not content_data:
                        continue

                    # For simplicity, assume "post" type for regular posts
                    # "poll" for poll posts, and "repost" for reposts
                    content_type = "post"
                    if content_data.get("is_poll"):
                        content_type = "poll"
                    elif content_data.get("original_post_id"):
                        content_type = "repost"

                    if content_type not in filters["content_types"]:
                        continue

                filtered_candidates.append(candidate)

            return filtered_candidates

        return unique_candidates

    def _score_candidates(self,
                          user_id: int,
                          user_embedding: List[float],
                          candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score candidates using hybrid approach"""
        scored_candidates = []

        for candidate in candidates:
            content_id = candidate["content_id"]

            # Get content embedding
            content_embedding = self.content_repository.get_content_embedding(self.db, content_id)
            if not content_embedding:
                # Create content embedding if not exists
                from app.ml.features.content_features import ContentFeatureExtractor
                feature_extractor = ContentFeatureExtractor(self.content_repository)
                content_embedding = feature_extractor.create_content_embedding(self.db, content_id)

            # Calculate content-based similarity
            if user_embedding and content_embedding:
                content_similarity = self._calculate_similarity(user_embedding, content_embedding)
            else:
                content_similarity = 0.0

            # Get base scores from candidate
            collaborative_score = candidate.get("collaborative_score", 0.0)
            popularity_score = candidate.get("popularity_score", 0.0)
            recency_score = candidate.get("recency_score", 0.0)

            # Calculate final score using weighted sum
            final_score = (
                    self.model_weights["collaborative"] * collaborative_score +
                    self.model_weights["content_based"] * content_similarity +
                    self.model_weights["popularity"] * popularity_score +
                    self.model_weights["recency"] * recency_score
            )

            # Determine recommendation factors
            factors = []

            if collaborative_score > 0.3:
                factors.append("similar_users")
            if content_similarity > 0.3:
                factors.append("your_interests")
            if popularity_score > 0.3:
                factors.append("popular")
            if recency_score > 0.7:
                factors.append("recent")
            if "social_score" in candidate and candidate["social_score"] > 0.3:
                factors.append("friend_activity")

            # Ensure at least one factor
            if not factors:
                factors.append("recommended_for_you")

            # Create scored candidate
            scored_candidate = {
                "content_id": content_id,
                "score": final_score,
                "content_similarity": content_similarity,
                "collaborative_score": collaborative_score,
                "popularity_score": popularity_score,
                "recency_score": recency_score,
                "factors": factors
            }

            scored_candidates.append(scored_candidate)

        # Sort by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        return scored_candidates

    def _diversify_recommendations(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply diversity rules to recommendations"""
        # Group by creator
        creators_seen = {}
        diversified = []

        # Add top candidates first but limit per creator
        for candidate in candidates:
            content_id = candidate["content_id"]
            content_data = self.content_repository.get_content_by_id(self.db, content_id)
            if not content_data:
                continue

            creator_id = content_data.get("user_id")
            creator_count = creators_seen.get(creator_id, 0)

            # Limit to 2 posts per creator
            if creator_count < 2:
                diversified.append(candidate)
                creators_seen[creator_id] = creator_count + 1

            # Break if we have enough diversified recommendations
            if len(diversified) >= 50:  # Get more than needed for further filtering
                break

        # If we don't have enough, add more from original list
        if len(diversified) < 50:
            for candidate in candidates:
                if candidate not in diversified:
                    diversified.append(candidate)

                if len(diversified) >= 50:
                    break

        # Mix in some serendipity - slightly reorder the candidates
        # to avoid pure score-based ordering
        final_list = diversified[:5]  # Keep top 5 as is

        # For the rest, apply some randomness to the order
        import random
        rest = diversified[5:]

        # Give a slight boost (up to 10%) to some items to increase diversity
        for i in range(len(rest)):
            if random.random() < 0.3:  # 30% chance of boosting
                boost = random.uniform(1.0, 1.1)  # 0-10% boost
                rest[i]["score"] *= boost

        # Resort after boosting
        rest.sort(key=lambda x: x["score"], reverse=True)

        # Combine the lists
        final_list.extend(rest)

        return final_list

    def _get_content_based_candidates(self, user_id: int, exclude_ids: set) -> List[Dict[str, Any]]:
        """Get content-based recommendation candidates"""
        # Get user interests
        interests = self.user_repository.get_user_interests(self.db, user_id)

        candidates = []

        # Find posts with matching hashtags
        for interest in interests:
            # Find posts with hashtags related to interest
            posts = self.content_repository.get_content_by_hashtag(self.db, interest.lower(), limit=10)

            for post in posts:
                if post["content_id"] not in exclude_ids:
                    # Calculate recency score
                    age_days = (datetime.utcnow() - post["created_at"]).days if post["created_at"] else 30
                    recency_score = max(0, 1 - (age_days / 30))  # 0 after 30 days

                    # Add to candidates
                    candidates.append({
                        "content_id": post["content_id"],
                        "content_based_score": 0.8,  # High score for interest match
                        "collaborative_score": 0.0,
                        "popularity_score": min(post["engagement_score"] / 100, 1.0),
                        "recency_score": recency_score
                    })

        return candidates

    def _get_collaborative_candidates(self, user_id: int, exclude_ids: set) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendation candidates"""
        # This is a placeholder - in a real implementation, use matrix factorization or similar

        # Get similar users
        similar_users = self.user_repository.get_users_with_similar_interests(self.db, user_id, limit=20)

        candidates = []
        content_seen = set()

        # Get interactions from similar users
        for similar_user in similar_users:
            interactions = self.interaction_repository.get_user_content_interactions(self.db, similar_user, days=14)

            for interaction in interactions:
                content_id = interaction["content_id"]

                if content_id not in exclude_ids and content_id not in content_seen:
                    content_seen.add(content_id)

                    # Score based on interaction type
                    interaction_score = 0.5  # Default
                    if interaction["interaction_type"] == "reaction":
                        interaction_score = 0.7
                    elif interaction["interaction_type"] == "comment":
                        interaction_score = 0.8
                    elif interaction["interaction_type"] == "share":
                        interaction_score = 0.9

                    # Get content data
                    content_data = self.content_repository.get_content_by_id(self.db, content_id)
                    if not content_data:
                        continue

                    # Calculate recency score
                    age_days = (datetime.utcnow() - content_data["created_at"]).days if content_data[
                        "created_at"] else 30
                    recency_score = max(0, 1 - (age_days / 30))  # 0 after 30 days

                    # Calculate popularity score
                    engagement = content_data["total_reactions"] + (content_data["total_comments"] * 2) + (
                                content_data["total_shares"] * 3)
                    popularity_score = min(engagement / 100, 1.0)

                    candidates.append({
                        "content_id": content_id,
                        "collaborative_score": interaction_score,
                        "content_based_score": 0.0,
                        "popularity_score": popularity_score,
                        "recency_score": recency_score
                    })

        return candidates

    def _get_social_candidates(self, user_id: int, exclude_ids: set) -> List[Dict[str, Any]]:
        """Get recommendations from user's social graph"""
        # Get user's friends
        friends = self.user_repository.get_user_friends(self.db, user_id)

        candidates = []
        content_seen = set()

        # Get recent content from friends
        for friend_id in friends:
            # This would be more efficient with a direct query in a real implementation
            # Get recent posts from this friend
            posts = []  # Placeholder - would query posts by user_id in a real implementation

            for post in posts:
                content_id = post["content_id"]

                if content_id not in exclude_ids and content_id not in content_seen:
                    content_seen.add(content_id)

                    # Calculate recency score
                    age_days = (datetime.utcnow() - post["created_at"]).days if post["created_at"] else 30
                    recency_score = max(0, 1 - (age_days / 30))  # 0 after 30 days

                    candidates.append({
                        "content_id": content_id,
                        "collaborative_score": 0.0,
                        "content_based_score": 0.0,
                        "popularity_score": min(post["engagement_score"] / 100,
                                                1.0) if "engagement_score" in post else 0.5,
                        "recency_score": recency_score,
                        "social_score": 0.9  # High score for friend's content
                    })

        return candidates

    def _get_trending_candidates(self, exclude_ids: set) -> List[Dict[str, Any]]:
        """Get trending/popular content candidates"""
        trending_posts = self.content_repository.get_trending_content(days=3, limit=20)

        candidates = []

        for post in trending_posts:
            content_id = post["content_id"]

            if content_id not in exclude_ids:
                # Calculate recency score
                age_days = (datetime.utcnow() - post["created_at"]).days if post["created_at"] else 30
                recency_score = max(0, 1 - (age_days / 30))  # 0 after 30 days

                # Calculate popularity score
                engagement = post["reaction_count"] + (post["comment_count"] * 2) + (post["share_count"] * 3)
                popularity_score = min(engagement / 100, 1.0)

                candidates.append({
                    "content_id": content_id,
                    "collaborative_score": 0.0,
                    "content_based_score": 0.0,
                    "popularity_score": popularity_score,
                    "recency_score": recency_score
                })

        return candidates

    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        try:
            # Convert to numpy arrays
            array1 = np.array(vec1).reshape(1, -1)
            array2 = np.array(vec2).reshape(1, -1)

            # Calculate cosine similarity
            similarity = cosine_similarity(array1, array2)[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
