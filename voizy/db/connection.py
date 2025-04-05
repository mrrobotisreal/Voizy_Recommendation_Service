"""
Database connection utilities for Voizy recommender system.
"""
import logging
from typing import Dict, Any
import mysql.connector

logger = logging.getLogger(__name__)


def get_db_connection(db_config: Dict[str, Any]):
    """
    Create a connection to the database

    Args:
        db_config: Database configuration parameters

    Returns:
        MySQL connection object
    """
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Failed to connect to database: {err}")
        raise