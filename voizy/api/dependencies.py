"""
Shared dependencies for the Voizy recommender API.

This module contains dependencies and shared resources used by both
server.py and endpoints.py to avoid circular imports.
"""
import logging
import configparser
from typing import Dict, Any
from datetime import datetime

from voizy.recommender.engine import VoizyRecommender

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('recommender_config.ini')

db_config = {
    'host': config.get('DATABASE', 'HOST', fallback='localhost'),
    'user': config.get('DATABASE', 'USER'),
    'password': config.get('DATABASE', 'PASSWORD'),
    'database': config.get('DATABASE', 'DATABASE', fallback='voizy_db')
}

recommender_config = {
    'model_path': config.get('RECOMMENDER', 'MODEL_PATH', fallback='./models/voizy_recommender'),
    'refresh_interval': config.getint('RECOMMENDER', 'REFRESH_INTERVAL', fallback=24 * 60 * 60),  # Default: 1 day
    'recommendation_cache_ttl': config.getint('RECOMMENDER', 'CACHE_TTL', fallback=60 * 60)  # Default: 1 hour
}

recommender = None
last_model_refresh = datetime.now()
recommendation_cache = {}

def get_recommender():
    """
    Dependency to get the recommender instance
    """
    global recommender
    if recommender is None:
        recommender = VoizyRecommender(db_config, model_path=recommender_config['model_path'])
    return recommender

def get_config():
    """
    Dependency to get the configuration
    """
    return {
        'db_config': db_config,
        'recommender_config': recommender_config
    }