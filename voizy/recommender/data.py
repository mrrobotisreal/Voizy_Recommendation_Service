"""
Data processing functions for the Voizy recommender system.

This module provides functions for fetching and processing data for the
recommender system, including user-item interactions, user features, and
post features.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from lightfm.data import Dataset
from scipy.sparse import csr_matrix

from voizy.db.queries import (
    INTERACTIONS_QUERY,
    USER_FEATURES_QUERY,
    POST_FEATURES_QUERY,
    USER_INTERACTIONS_QUERY,
    POPULAR_POSTS_QUERY
)

logger = logging.getLogger(__name__)


def fetch_interactions_data(
        db_conn,
        db_config: Dict[str, str],
        days_limit: int = 30
) -> pd.DataFrame:
    """
    Fetch user-post interactions from database

    Args:
        db_conn: Database connection
        db_config: Database configuration
        days_limit: Limit data to recent days

    Returns:
        DataFrame with user-post interactions
    """
    cutoff_date = datetime.now() - timedelta(days=days_limit)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

    connection_str = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    engine = create_engine(connection_str)

    query = INTERACTIONS_QUERY.format(cutoff_date=cutoff_date_str)

    try:
        interactions_df = pd.read_sql(query, engine)
        logger.info(f"Fetched {len(interactions_df)} interaction records")
        return interactions_df
    except Exception as e:
        logger.error(f"Error fetching interaction data: {e}")
        raise


def fetch_user_features(db_conn, db_config: Dict[str, str]) -> pd.DataFrame:
    """
    Fetch user features for content-based filtering

    Args:
        db_conn: Database connection
        db_config: Database configuration

    Returns:
        DataFrame with user features
    """
    connection_str = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    engine = create_engine(connection_str)

    try:
        user_features_df = pd.read_sql(USER_FEATURES_QUERY, engine)
        logger.info(f"Fetched features for {len(user_features_df)} users")
        return user_features_df
    except Exception as e:
        logger.error(f"Error fetching user features: {e}")
        raise


def fetch_post_features(
        db_conn,
        db_config: Dict[str, str],
        days_limit: int = 60
) -> pd.DataFrame:
    """
    Fetch post features for content-based filtering

    Args:
        db_conn: Database connection
        db_config: Database configuration
        days_limit: Limit posts to recent days

    Returns:
        DataFrame with post features
    """
    cutoff_date = datetime.now() - timedelta(days=days_limit)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

    connection_str = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    engine = create_engine(connection_str)

    query = POST_FEATURES_QUERY.format(cutoff_date=cutoff_date_str)

    try:
        post_features_df = pd.read_sql(query, engine)
        logger.info(f"Fetched features for {len(post_features_df)} posts")
        return post_features_df
    except Exception as e:
        logger.error(f"Error fetching post features: {e}")
        raise


def extract_user_features(user_features_df: pd.DataFrame) -> List[str]:
    """
    Extract user features from DataFrame

    Args:
        user_features_df: DataFrame with user features

    Returns:
        List of feature strings
    """
    features = []

    for _, row in user_features_df.iterrows():
        if 'city_of_residence' in row and row['city_of_residence']:
            features.append(f"city:{row['city_of_residence']}")

        if 'age' in row and row['age']:
            features.append(f"age_group:{get_age_group(row['age'])}")

        if 'interests' in row and row['interests']:
            interests = row['interests'].split(',')
            for interest in interests:
                features.append(f"interest:{interest.strip()}")

    return list(set(features))


def extract_post_features(post_features_df: pd.DataFrame) -> List[str]:
    """
    Extract post features from DataFrame

    Args:
        post_features_df: DataFrame with post features

    Returns:
        List of feature strings
    """
    features = []

    for _, row in post_features_df.iterrows():
        if 'author_id' in row and row['author_id']:
            features.append(f"author:{row['author_id']}")

        if 'is_poll' in row and row['is_poll']:
            features.append("content_type:poll")

        if 'has_location' in row and row['has_location']:
            features.append("has_location")

        if 'hashtags' in row and row['hashtags']:
            hashtags = row['hashtags'].split(',')
            for hashtag in hashtags:
                features.append(f"hashtag:{hashtag.strip()}")

        if 'media_types' in row and row['media_types']:
            media_types = row['media_types'].split(',')
            for media_type in media_types:
                features.append(f"media:{media_type.strip()}")

    return list(set(features))


def get_age_group(age: int) -> str:
    """
    Convert age to age group

    Args:
        age: User age

    Returns:
        Age group string
    """
    if age < 18:
        return "under18"
    elif age < 25:
        return "18-24"
    elif age < 35:
        return "25-34"
    elif age < 45:
        return "35-44"
    elif age < 55:
        return "45-54"
    else:
        return "55plus"


def build_user_features_matrix(
        user_features_df: pd.DataFrame,
        user_mapping: Dict[int, int],
        dataset: Dataset,
        features: List[str]
) -> csr_matrix:
    """
    Build user features matrix from DataFrame

    Args:
        user_features_df: DataFrame with user features
        user_mapping: Mapping from user IDs to indices
        dataset: LightFM dataset
        features: List of feature strings

    Returns:
        User features matrix
    """
    user_features = {}

    for _, row in user_features_df.iterrows():
        if 'user_id' not in row:
            continue

        user_id = int(row['user_id'])
        if user_id not in user_mapping:
            continue

        user_features_list = []

        if 'city_of_residence' in row and row['city_of_residence']:
            user_features_list.append(f"city:{row['city_of_residence']}")

        if 'age' in row and row['age']:
            user_features_list.append(f"age_group:{get_age_group(row['age'])}")

        if 'interests' in row and row['interests']:
            interests = row['interests'].split(',')
            for interest in interests:
                user_features_list.append(f"interest:{interest.strip()}")

        user_features[user_id] = user_features_list

    return dataset.build_user_features(
        ((user_id, features) for user_id, features in user_features.items() if user_id in user_mapping),
        normalize=True
    )


def build_post_features_matrix(
        post_features_df: pd.DataFrame,
        post_mapping: Dict[int, int],
        dataset: Dataset,
        features: List[str]
) -> csr_matrix:
    """
    Build post features matrix from DataFrame

    Args:
        post_features_df: DataFrame with post features
        post_mapping: Mapping from post IDs to indices
        dataset: LightFM dataset
        features: List of feature strings

    Returns:
        Post features matrix
    """
    post_features = {}

    for _, row in post_features_df.iterrows():
        if 'post_id' not in row:
            continue

        post_id = int(row['post_id'])
        if post_id not in post_mapping:
            continue

        post_features_list = []

        if 'author_id' in row and row['author_id']:
            post_features_list.append(f"author:{row['author_id']}")

        if 'is_poll' in row and row['is_poll']:
            post_features_list.append("content_type:poll")

        if 'has_location' in row and row['has_location']:
            post_features_list.append("has_location")

        if 'hashtags' in row and row['hashtags']:
            hashtags = row['hashtags'].split(',')
            for hashtag in hashtags:
                post_features_list.append(f"hashtag:{hashtag.strip()}")

        if 'media_types' in row and row['media_types']:
            media_types = row['media_types'].split(',')
            for media_type in media_types:
                post_features_list.append(f"media:{media_type.strip()}")

        post_features[post_id] = post_features_list

    return dataset.build_item_features(
        ((post_id, features) for post_id, features in post_features.items() if post_id in post_mapping),
        normalize=True
    )


def get_user_interactions(db_conn, user_id: int) -> List[int]:
    """
    Get posts that user has already interacted with

    Args:
        db_conn: Database connection
        user_id: User ID

    Returns:
        List of post IDs
    """
    cursor = db_conn.cursor()

    cursor.execute(USER_INTERACTIONS_QUERY, (user_id, user_id, user_id, user_id))
    result = cursor.fetchall()
    cursor.close()

    seen_posts = [row[0] for row in result]
    return seen_posts


def get_popular_posts(db_conn, n: int = 10, days_limit: int = 7) -> List[int]:
    """
    Get most popular recent posts as fallback

    Args:
        db_conn: Database connection
        n: Number of posts to return
        days_limit: Limit to posts from the last N days

    Returns:
        List of post IDs
    """
    cursor = db_conn.cursor()

    cutoff_date = datetime.now() - timedelta(days=days_limit)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

    query = POPULAR_POSTS_QUERY.format(cutoff_date=cutoff_date_str, limit=n)

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    popular_posts = [row[0] for row in result]
    return popular_posts