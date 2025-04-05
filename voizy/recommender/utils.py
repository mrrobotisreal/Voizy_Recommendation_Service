"""
Utility functions for the Voizy recommender system.
"""
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def record_recommendation_metrics(
        db_conn,
        metric_name: str,
        metric_value: float,
        details: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Record metrics about the recommendation system

    Args:
        db_conn: Database connection
        metric_name: Name of the metric
        metric_value: Value of the metric
        details: Additional details about the metric (optional)

    Returns:
        Success status
    """
    try:
        cursor = db_conn.cursor()

        query = """
        INSERT INTO recommender_metrics
        (metric_date, metric_name, metric_value, metric_details, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
        metric_value = %s,
        metric_details = %s,
        created_at = NOW()
        """

        details_json = json.dumps(details) if details else None

        current_date = datetime.now().date()

        cursor.execute(
            query,
            (
                current_date,
                metric_name,
                metric_value,
                details_json,
                metric_value,
                details_json
            )
        )

        db_conn.commit()
        cursor.close()

        return True
    except Exception as e:
        logger.error(f"Error recording metrics: {e}")
        return False


def calculate_similarity_score(
        user_id1: int,
        user_id2: int,
        db_conn
) -> float:
    """
    Calculate similarity score between two users based on their interactions

    Args:
        user_id1: First user ID
        user_id2: Second user ID
        db_conn: Database connection

    Returns:
        Similarity score between 0 and 1
    """
    try:
        cursor = db_conn.cursor()

        query = """
        SELECT 
            COUNT(DISTINCT t1.post_id) AS common_interactions
        FROM 
            (
                SELECT DISTINCT post_id 
                FROM post_reactions 
                WHERE user_id = %s

                UNION

                SELECT DISTINCT post_id 
                FROM comments 
                WHERE user_id = %s

                UNION

                SELECT DISTINCT post_id 
                FROM post_shares 
                WHERE user_id = %s

                UNION

                SELECT DISTINCT object_id AS post_id 
                FROM analytics_events 
                WHERE user_id = %s 
                  AND event_type = 'post_view'
                  AND object_type = 'post'
            ) t1
        JOIN 
            (
                SELECT DISTINCT post_id 
                FROM post_reactions 
                WHERE user_id = %s

                UNION

                SELECT DISTINCT post_id 
                FROM comments 
                WHERE user_id = %s

                UNION

                SELECT DISTINCT post_id 
                FROM post_shares 
                WHERE user_id = %s

                UNION

                SELECT DISTINCT object_id AS post_id 
                FROM analytics_events 
                WHERE user_id = %s 
                  AND event_type = 'post_view'
                  AND object_type = 'post'
            ) t2
        ON t1.post_id = t2.post_id
        """

        cursor.execute(query, (user_id1, user_id1, user_id1, user_id1, user_id2, user_id2, user_id2, user_id2))
        common_interactions = cursor.fetchone()[0]

        query = """
        SELECT 
            (
                SELECT COUNT(DISTINCT post_id) 
                FROM (
                    SELECT DISTINCT post_id FROM post_reactions WHERE user_id = %s
                    UNION
                    SELECT DISTINCT post_id FROM comments WHERE user_id = %s
                    UNION
                    SELECT DISTINCT post_id FROM post_shares WHERE user_id = %s
                    UNION
                    SELECT DISTINCT object_id AS post_id FROM analytics_events 
                    WHERE user_id = %s AND event_type = 'post_view' AND object_type = 'post'
                ) t1
            ) AS user1_total,
            (
                SELECT COUNT(DISTINCT post_id) 
                FROM (
                    SELECT DISTINCT post_id FROM post_reactions WHERE user_id = %s
                    UNION
                    SELECT DISTINCT post_id FROM comments WHERE user_id = %s
                    UNION
                    SELECT DISTINCT post_id FROM post_shares WHERE user_id = %s
                    UNION
                    SELECT DISTINCT object_id AS post_id FROM analytics_events 
                    WHERE user_id = %s AND event_type = 'post_view' AND object_type = 'post'
                ) t2
            ) AS user2_total
        """

        cursor.execute(query, (user_id1, user_id1, user_id1, user_id1, user_id2, user_id2, user_id2, user_id2))
        result = cursor.fetchone()
        user1_total, user2_total = result

        cursor.close()

        if user1_total == 0 or user2_total == 0:
            return 0.0

        union_size = user1_total + user2_total - common_interactions
        similarity = common_interactions / union_size if union_size > 0 else 0.0

        return similarity
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return 0.0


def store_user_similarity(
        db_conn,
        user_id1: int,
        user_id2: int,
        similarity_score: float
) -> bool:
    """
    Store similarity score between two users

    Args:
        db_conn: Database connection
        user_id1: First user ID
        user_id2: Second user ID
        similarity_score: Similarity score

    Returns:
        Success status
    """
    try:
        cursor = db_conn.cursor()

        if user_id1 > user_id2:
            user_id1, user_id2 = user_id2, user_id1

        query = """
        INSERT INTO user_similarities
        (user_id, similar_user_id, similarity_score, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        ON DUPLICATE KEY UPDATE
        similarity_score = %s,
        updated_at = NOW()
        """

        cursor.execute(query, (user_id1, user_id2, similarity_score, similarity_score))

        db_conn.commit()
        cursor.close()

        return True
    except Exception as e:
        logger.error(f"Error storing similarity: {e}")
        return False