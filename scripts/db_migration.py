"""
Database migration script for the Voizy recommender system.

This script creates the additional tables needed for the recommender system.
"""
import sys
import logging
import configparser
import mysql.connector
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/db_migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_additional_tables():
    """Create any additional tables needed for the recommender system"""
    logger.info("Starting database migration for Voizy Recommender")

    config = configparser.ConfigParser()
    config.read('../recommender_config.ini')

    db_config = {
        'host': config.get('DATABASE', 'HOST', fallback='localhost'),
        'user': config.get('DATABASE', 'USER'),
        'password': config.get('DATABASE', 'PASSWORD'),
        'database': config.get('DATABASE', 'DATABASE', fallback='voizy_db')
    }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        logger.info("Checking if analytics_events table needs updates")
        cursor.execute("SHOW COLUMNS FROM analytics_events LIKE 'event_type'")
        event_type_column = cursor.fetchone()

        if event_type_column:
            logger.info("Updating analytics_events table")
            cursor.execute("""
            ALTER TABLE analytics_events 
            MODIFY COLUMN event_type VARCHAR(100) NOT NULL,
            ADD INDEX idx_analytics_event_type (event_type),
            ADD INDEX idx_analytics_object_type_id (object_type, object_id),
            ADD INDEX idx_analytics_event_time (event_time)
            """)

        logger.info("Creating user_recommendations table")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_recommendations (
            recommendation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            post_id BIGINT NOT NULL,
            recommendation_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            source VARCHAR(50) NOT NULL DEFAULT 'recommender',
            is_clicked BOOLEAN NOT NULL DEFAULT 0,
            is_interacted BOOLEAN NOT NULL DEFAULT 0,
            interaction_type VARCHAR(50),
            interaction_time DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            INDEX idx_user_recommendations_user (user_id),
            INDEX idx_user_recommendations_time (recommendation_time)
        )
        """)

        logger.info("Creating user_similarities table")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_similarities (
            similarity_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            similar_user_id BIGINT NOT NULL,
            similarity_score FLOAT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (similar_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE INDEX idx_user_similarity_pair (user_id, similar_user_id),
            INDEX idx_user_similarity_score (user_id, similarity_score DESC)
        )
        """)

        logger.info("Creating post_similarities table")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_similarities (
            similarity_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id BIGINT NOT NULL,
            similar_post_id BIGINT NOT NULL,
            similarity_score FLOAT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (similar_post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            UNIQUE INDEX idx_post_similarity_pair (post_id, similar_post_id),
            INDEX idx_post_similarity_score (post_id, similarity_score DESC)
        )
        """)

        logger.info("Creating user_content_preferences table")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_content_preferences (
            preference_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            content_type VARCHAR(50) NOT NULL,  -- e.g., 'hashtag', 'media_type', 'author'
            content_value VARCHAR(255) NOT NULL,  -- e.g., hashtag name, media type, author id
            preference_score FLOAT NOT NULL,    -- higher = more preferred
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE INDEX idx_user_content_preference (user_id, content_type, content_value),
            INDEX idx_user_preferences (user_id, preference_score DESC)
        )
        """)

        logger.info("Creating recommender_metrics table")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommender_metrics (
            metric_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            metric_date DATE NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            metric_value FLOAT NOT NULL,
            metric_details JSON,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE INDEX idx_recommender_metric_date_name (metric_date, metric_name)
        )
        """)

        conn.commit()
        logger.info("Database migration completed successfully")

    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        conn.rollback()
        return 1
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(create_additional_tables())