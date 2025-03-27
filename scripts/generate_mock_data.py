import os
import secrets
import sys
import random
import datetime
import string
import json
import hashlib
import logging
from typing import List, Dict, Any, Tuple, Optional
import time
import uuid
from collections import defaultdict

import faker
import mysql.connector
from mysql.connector import Error
from faker import Faker, providers
from faker.providers import internet, profile, job, company
import numpy as np
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("data-generator")

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "voizy_test",
    "user": os.getenv("DBU"),
    "password": os.getenv("DBP")
}

CONFIG = {
    "users": {
        "count": 200,
        "images_per_user": (2, 20),
        "interests_per_user": (3, 10),
        "schools_per_user": (1, 3),
        "social_links_per_user": (1, 5),
        "friends_per_user": (5, 47)
    },
    "posts": {
        "posts_per_user": (50, 500),
        "comments_per_post": (0, 50),
        "typical_comments_range": (0, 20),
        "image_post_percentage": 30,
        "images_per_post": (1, 3),
        "shared_post_percentage": 10,
        "poll_percentage": 3,
        "poll_options_per_poll": (2, 5),
        "poll_votes_per_option": (0, 30),
        "hashtags_per_post": (0, 5),
        "reactions_per_post": (0, 50)
    },
    "groups": {
        "count": 20,
        "members_per_group": (5, 50)
    },
    "content": {
        "max_post_length": 500,
        "max_comment_length": 200
    }
}

PROFILE_PICTURES = [
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/0.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/01.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/0L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/1.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/11.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/111.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/12.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/121.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/13.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/15.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/151.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/16.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/161.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/17.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/171.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/19.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/1L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/2.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/20.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/201.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/21.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/22.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/221.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/24.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/25.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/251.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/26.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/261.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/27.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/28.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/2L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/3.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/30.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/31.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/32.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/33.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/331.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/34.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/35.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/351.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/37.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/38.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/381.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/39.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/3L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/40.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/4.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/43.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/45.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/47.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/48.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/49.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/4L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/50.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/501.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/52.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/53.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/54.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/58.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/59.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/5L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/6.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/60.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/61.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/62.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/621.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/63.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/65.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/66.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/661.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/6L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/7.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/70.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/71.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/711.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/72.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/721.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/73.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/79.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/7L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/8.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/80.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/801.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/81.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/82.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/821.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/83.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/831.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/84.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/85.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/86.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/861.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/87.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/88.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/89.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/8L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/9.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/90.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/91.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/92.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/93.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/931.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/94.jpg"
]

POST_MEDIA = [
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/0.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/01.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/0L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/1.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/11.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/111.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/12.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/121.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/13.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/15.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/151.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/16.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/161.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/17.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/171.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/19.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/1L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/2.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/20.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/201.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/21.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/22.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/221.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/24.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/25.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/251.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/26.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/261.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/27.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/28.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/2L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/3.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/30.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/31.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/32.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/33.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/331.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/34.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/35.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/351.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/37.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/38.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/381.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/39.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/3L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/40.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/4.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/43.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/45.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/47.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/48.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/49.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/4L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/50.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/501.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/52.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/53.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/54.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/58.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/59.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/5L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/6.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/60.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/61.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/62.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/621.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/63.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/65.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/66.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/661.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/6L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/7.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/70.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/71.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/711.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/72.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/721.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/73.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/79.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/7L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/8.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/80.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/801.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/81.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/82.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/821.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/83.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/831.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/84.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/85.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/86.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/861.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/87.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/88.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/89.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/8L.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/9.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/90.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/91.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/92.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/93.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/931.jpg",
    "https://voizy-app.s3.us-west-2.amazonaws.com/default/users/profilePics/94.jpg"
]

fake = Faker()
fake.add_provider(faker.providers.internet)
fake.add_provider(faker.providers.profile)
fake.add_provider(faker.providers.job)
fake.add_provider(faker.providers.company)

users = []
api_keys = []
user_profiles = []
interests = []
user_interests = []
schools = []
user_schools = []
social_links = []
user_images = []
friendships = []
groups = []
group_members = []
posts = []
poll_options = []
poll_votes = []
hashtags = []
post_hashtags = []
post_reactions = []
comments = []
comment_reactions = []
post_shares = []
post_media = []
recommendation_models = []
user_embeddings = []
content_embeddings = []

# Lists of realistic data
UNIVERSITIES = [
    # US
    "Harvard University", "Stanford University", "MIT", "Princeton University", "Yale University",
    "Columbia University", "University of Chicago", "University of California, Berkeley",
    "University of Pennsylvania", "Cornell University", "NYU", "UCLA", "University of Michigan",

    # Canada
    "University of Toronto", "McGill University", "University of British Columbia",
    "University of Waterloo", "McMaster University",

    # UK
    "University of Oxford", "University of Cambridge", "Imperial College London",
    "University College London", "University of Edinburgh", "King's College London",

    # France
    "Sorbonne University", "École Polytechnique", "Sciences Po", "École Normale Supérieure",

    # Israel
    "Hebrew University of Jerusalem", "Tel Aviv University", "Technion", "Weizmann Institute of Science",

    # Russia
    "Lomonosov Moscow State University", "Saint Petersburg State University",
    "Bauman Moscow State Technical University",

    # China
    "Tsinghua University", "Peking University", "Fudan University", "Shanghai Jiao Tong University",

    # Japan
    "University of Tokyo", "Kyoto University", "Osaka University", "Tohoku University",

    # Additional international universities
    "National University of Singapore", "ETH Zurich", "Technical University of Munich",
    "University of Melbourne", "University of Sydney", "Seoul National University"
]

SOCIAL_PLATFORMS = [
    {"name": "Github", "domain": "github.com"},
    {"name": "LinkedIn", "domain": "linkedin.com"},
    {"name": "Facebook", "domain": "facebook.com"},
    {"name": "X", "domain": "x.com"},
    {"name": "TikTok", "domain": "tiktok.com"},
    {"name": "Instagram", "domain": "instagram.com"},
    {"name": "Snapchat", "domain": "snapchat.com"},
    {"name": "YouTube", "domain": "youtube.com"},
    {"name": "Medium", "domain": "medium.com"},
    {"name": "Pinterest", "domain": "pinterest.com"},
    {"name": "Reddit", "domain": "reddit.com"},
    {"name": "Discord", "domain": "discord.com"}
]

INTEREST_CATEGORIES = [
    "Technology", "Science", "Art", "Music", "Film", "Television", "Books", "Writing",
    "Photography", "Design", "Fashion", "Food", "Travel", "Fitness", "Sports",
    "Gaming", "Coding", "Business", "Finance", "Politics", "History", "Philosophy",
    "Languages", "Education", "Environment", "Health", "Psychology", "Spirituality"
]

INTERESTS = [
    # Technology
    "Artificial Intelligence", "Machine Learning", "Web Development", "Mobile Apps",
    "Cybersecurity", "Blockchain", "Virtual Reality", "Augmented Reality", "IoT",
    "Cloud Computing", "Big Data", "Robotics", "3D Printing", "Quantum Computing",

    # Science
    "Astronomy", "Physics", "Chemistry", "Biology", "Neuroscience", "Genetics",
    "Climate Science", "Marine Biology", "Geology", "Mathematics", "Data Science",

    # Art
    "Painting", "Drawing", "Sculpture", "Digital Art", "Anime", "Graphic Design",
    "Illustration", "Street Art", "Modern Art", "Classical Art", "Photography",

    # Music
    "Rock", "Pop", "Hip Hop", "Jazz", "Classical", "Electronic", "Folk", "Country",
    "R&B", "Indie", "Metal", "Blues", "Reggae", "Punk", "K-pop", "Music Production",

    # Film & TV
    "Movies", "Documentaries", "Animation", "Directors", "Screenwriting", "Film Theory",
    "TV Shows", "Series", "Sitcoms", "Drama", "Comedy", "Science Fiction", "Fantasy",

    # Books & Writing
    "Fiction", "Non-fiction", "Poetry", "Science Fiction", "Fantasy", "Mystery",
    "Historical Fiction", "Biography", "Self-Help", "Academic Writing", "Journalism",

    # Sports & Fitness
    "Running", "Yoga", "Weightlifting", "Basketball", "Football", "Soccer", "Tennis",
    "Swimming", "Cycling", "Hiking", "Martial Arts", "Baseball", "Golf", "Hockey",

    # Gaming
    "Video Games", "Board Games", "Card Games", "Role-Playing Games", "Strategy Games",
    "Puzzle Games", "Mobile Gaming", "Esports", "Game Development", "Virtual Worlds",

    # Business & Finance
    "Entrepreneurship", "Startups", "Investing", "Stock Market", "Cryptocurrency",
    "Personal Finance", "Marketing", "Management", "Real Estate", "E-commerce",

    # Additional categories
    "Cooking", "Baking", "Veganism", "Vegetarianism", "Sustainable Living",
    "Minimalism", "Architecture", "Interior Design", "Fashion Design", "Gardening",
    "Travel Photography", "Backpacking", "Language Learning", "History", "Philosophy",
    "Psychology", "Meditation", "Yoga", "Politics", "Social Justice", "Climate Action"
]
INTERESTS = list(dict.fromkeys(INTERESTS))

HASHTAGS = [
    "tech", "innovation", "ai", "machinelearning", "webdev", "coding", "programming",
    "datascience", "cloud", "cybersecurity", "blockchain", "startup", "entrepreneur",
    "business", "marketing", "socialmedia", "digital", "mobile", "app", "software",
    "design", "ux", "ui", "userexperience", "creative", "art", "photography", "photo",
    "travel", "adventure", "explore", "wanderlust", "nature", "landscape", "wildlife",
    "sustainability", "green", "eco", "environment", "climate", "renewable", "future",
    "health", "wellness", "fitness", "workout", "nutrition", "mindfulness", "meditation",
    "yoga", "running", "sports", "athlete", "training", "performance", "competition",
    "music", "musician", "band", "concert", "festival", "song", "album", "artist",
    "film", "movie", "cinema", "director", "actor", "actress", "hollywood", "indie",
    "book", "reading", "author", "literature", "novel", "story", "writing", "education",
    "learning", "student", "study", "university", "college", "academic", "research",
    "science", "space", "astronomy", "physics", "biology", "chemistry", "engineering",
    "history", "culture", "heritage", "tradition", "community", "society", "social",
    "politics", "policy", "government", "economy", "finance", "investment", "money",
    "motivation", "inspiration", "success", "leadership", "growth", "development",
    "career", "job", "work", "professional", "networking", "collaboration", "team",
    "food", "cooking", "recipe", "chef", "restaurant", "cuisine", "foodie", "delicious",
    "fashion", "style", "trend", "model", "clothing", "accessory", "beauty", "makeup",
    "gaming", "gamer", "videogames", "esports", "streaming", "youtuber", "content",
    "funny", "humor", "comedy", "laugh", "joke", "meme", "entertainment", "fun",
    "love", "relationship", "family", "friend", "life", "lifestyle", "happy", "smile",
    "quote", "wisdom", "philosophy", "thought", "idea", "creativity", "innovation",
    "throwback", "nostalgia", "memory", "experience", "moment", "capture", "share"
]
HASHTAGS = list(dict.fromkeys(HASHTAGS))

REACTION_TYPES = ["like", "love", "laugh", "congratulate", "shocked", "sad", "angry"]

POLL_DURATIONS = ["hours", "days", "weeks"]

MEDIA_TYPES = ["image", "video"]


def generate_api_key() -> dict:
    """Generate a random API key."""
    api_key_length = 32
    random_bytes = secrets.token_bytes(api_key_length)

    key = f"sk_{random_bytes.hex()}"

    key_rotation_days = 90
    current_time = datetime.datetime.now()
    expires_at = current_time + datetime.timedelta(days=key_rotation_days)

    api_key_data = {
        "api_key": key,
        "created_at": current_time,
        "expires_at": expires_at,
        "last_used_at": current_time,
        "updated_at": current_time
    }

    return api_key_data

def generate_salt() -> str:
    """Generate a random salt for password hashing."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def hash_password(password: str, salt: str) -> str:
    """Hash a password using a salt."""
    salted = password + salt
    return hashlib.sha256(salted.encode()).hexdigest()


def get_random_date(start_date: datetime.datetime, end_date: datetime.datetime) -> datetime.datetime:
    """Get a random date between start_date and end_date."""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)


def generate_users() -> None:
    """Generate mock users."""
    logger.info("Generating users...")
    global users, user_profiles

    current_date = datetime.datetime.now()
    start_date = current_date - datetime.timedelta(days=365 * 5)  # Up to 5 years ago

    unique_emails = set()
    unique_usernames = set()

    for i in tqdm(range(CONFIG["users"]["count"])):
        # Generate user
        while True:
            email = fake.email()
            if email not in unique_emails:
                unique_emails.add(email)
                break

        while True:
            username = fake.user_name() + str(safe_randint(1, 999))
            if username not in unique_usernames:
                unique_usernames.add(username)
                break
        password = fake.password()
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        api_key_data = generate_api_key()
        api_key = api_key_data["api_key"]
        created_at = get_random_date(start_date, current_date)

        users.append({
            "user_id": i + 1,
            "api_key": api_key,
            "email": email,
            "salt": salt,
            "password_hash": password_hash,
            "username": username,
            "created_at": created_at,
            "updated_at": created_at
        })

        api_keys.append({
            "api_key_id": i + 1,
            "user_id": i + 1,
            "api_key": api_key,
            "created_at": created_at,
            "expires_at": created_at + datetime.timedelta(days=90),
            "last_used_at": created_at,
            "updated_at": created_at
        })

        # Generate user profile
        first_name = fake.first_name()
        last_name = fake.last_name()
        preferred_name = first_name if random.random() < 0.8 else fake.first_name()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=70)
        city = fake.city()
        place_of_work = fake.company() if random.random() < 0.7 else None

        user_profiles.append({
            "profile_id": i + 1,
            "user_id": i + 1,
            "first_name": first_name,
            "last_name": last_name,
            "preferred_name": preferred_name,
            "birth_date": birth_date,
            "city_of_residence": city,
            "place_of_work": place_of_work,
            "date_joined": created_at
        })


def generate_interests() -> None:
    """Generate interests and assign to users."""
    logger.info("Generating interests...")
    global interests, user_interests

    # Create interests
    for i, interest_name in enumerate(INTERESTS):
        interests.append({
            "interest_id": i + 1,
            "name": interest_name
        })

    # Assign interests to users
    interest_id = 1
    for user_id in tqdm(range(1, len(users) + 1)):
        num_interests = safe_randint(*CONFIG["users"]["interests_per_user"])
        user_interest_ids = random.sample(range(1, len(interests) + 1), min(num_interests, len(interests)))

        for interest_id_for_user in user_interest_ids:
            user_interests.append({
                "user_interest_id": interest_id,
                "user_id": user_id,
                "interest_id": interest_id_for_user
            })
            interest_id += 1


def generate_schools() -> None:
    """Generate schools and assign to users."""
    logger.info("Generating schools for users...")
    global schools, user_schools

    # Create schools from the UNIVERSITIES list
    for i, school_name in enumerate(UNIVERSITIES):
        schools.append({
            "school_id": i + 1,
            "name": school_name
        })

    # Assign schools to users
    user_school_id = 1
    for user_id in tqdm(range(1, len(users) + 1)):
        num_schools = safe_randint(*CONFIG["users"]["schools_per_user"])
        user_school_ids = random.sample(range(1, len(schools) + 1), min(num_schools, len(schools)))

        for school_id in user_school_ids:
            # Random start and end years for education
            current_year = datetime.datetime.now().year
            age = current_year - user_profiles[user_id - 1]["birth_date"].year
            max_start = current_year - max(0, age - 22)  # Assume education starts at 18+
            min_start = max(max_start - 15, current_year - age + 18)  # Don't start before they're 18

            start_year = safe_randint(min_start, max_start)
            end_year = safe_randint(start_year, start_year + 5)
            if end_year > current_year:  # Still attending
                end_year = None

            user_schools.append({
                "user_school_id": user_school_id,
                "user_id": user_id,
                "school_name": schools[school_id - 1]["name"],
                "start_year": start_year,
                "end_year": end_year
            })
            user_school_id += 1


def generate_social_links() -> None:
    """Generate social links for users."""
    logger.info("Generating social links for users...")
    global social_links

    link_id = 1
    for user_id in tqdm(range(1, len(users) + 1)):
        num_links = safe_randint(*CONFIG["users"]["social_links_per_user"])
        platforms = random.sample(SOCIAL_PLATFORMS, min(num_links, len(SOCIAL_PLATFORMS)))

        for platform in platforms:
            username = fake.user_name() if random.random() < 0.7 else users[user_id - 1]["username"]
            url = f"https://www.{platform['domain']}/{username}"

            social_links.append({
                "link_id": link_id,
                "user_id": user_id,
                "platform": platform["name"],
                "url": url
            })
            link_id += 1


def generate_user_images() -> None:
    """Generate profile and cover images for users."""
    logger.info("Generating images for users...")
    global user_images

    image_id = 1
    for user_id in tqdm(range(1, len(users) + 1)):
        num_images = safe_randint(*CONFIG["users"]["images_per_user"])

        # Ensure at least one profile pic and possibly one cover pic
        has_profile_pic = False
        has_cover_pic = False

        for _ in range(num_images):
            is_profile_pic = False
            is_cover_pic = False

            if not has_profile_pic:
                is_profile_pic = True
                has_profile_pic = True
            elif not has_cover_pic and random.random() < 0.7:
                is_cover_pic = True
                has_cover_pic = True

            # Either use sample images or generate URLs
            if PROFILE_PICTURES and random.random() < 0.7:
                image_url = random.choice(PROFILE_PICTURES)
            else:
                image_url = f"https://voizy-app.s3.amazonaws.com/users/{user_id}/image_{image_id}.jpg"

            user_images.append({
                "user_image_id": image_id,
                "user_id": user_id,
                "image_url": image_url,
                "is_profile_pic": is_profile_pic,
                "is_cover_pic": is_cover_pic,
                "uploaded_at": users[user_id - 1]["created_at"] + datetime.timedelta(days=safe_randint(0, 365))
            })
            image_id += 1


def generate_friendships() -> None:
    """Generate friendships between users."""
    logger.info("Generating friendships between users...")
    global friendships

    friendship_id = 1
    friendship_pairs = set()  # To avoid duplicate friendships

    for user_id in tqdm(range(1, len(users) + 1)):
        num_friends = safe_randint(*CONFIG["users"]["friends_per_user"])
        potential_friends = list(range(1, len(users) + 1))
        potential_friends.remove(user_id)  # Remove self

        # Limit to available friends
        actual_num_friends = min(num_friends, len(potential_friends))
        friend_ids = random.sample(potential_friends, actual_num_friends)

        for friend_id in friend_ids:
            # Skip if friendship already exists
            pair = tuple(sorted([user_id, friend_id]))
            if pair in friendship_pairs:
                continue

            friendship_pairs.add(pair)

            # Determine status (mostly accepted, some pending, few blocked)
            status = random.choices(
                ["accepted", "pending", "blocked"],
                weights=[0.85, 0.1, 0.05],
                k=1
            )[0]

            created_at = min(
                users[user_id - 1]["created_at"],
                users[friend_id - 1]["created_at"]
            ) + datetime.timedelta(days=safe_randint(1, 365))

            friendships.append({
                "friendship_id": friendship_id,
                "user_id": user_id,
                "friend_id": friend_id,
                "status": status,
                "created_at": created_at
            })
            friendship_id += 1


def generate_groups() -> None:
    """Generate groups and group memberships."""
    logger.info("Generating groups and memberships...")
    global groups, group_members

    # Generate groups
    for i in tqdm(range(CONFIG["groups"]["count"])):
        creator_id = safe_randint(1, len(users))
        name = fake.bs().title()
        description = fake.paragraph()
        privacy = random.choice(["public", "private", "closed"])
        created_at = users[creator_id - 1]["created_at"] + datetime.timedelta(days=safe_randint(0, 365))

        groups.append({
            "group_id": i + 1,
            "name": name,
            "description": description,
            "privacy": privacy,
            "creator_id": creator_id,
            "created_at": created_at
        })

    # Generate group memberships
    member_id = 1
    for group_id in tqdm(range(1, len(groups) + 1)):
        num_members = safe_randint(*CONFIG["groups"]["members_per_group"])
        creator_id = groups[group_id - 1]["creator_id"]

        # Add creator as admin
        group_members.append({
            "group_member_id": member_id,
            "group_id": group_id,
            "user_id": creator_id,
            "role": "admin",
            "joined_at": groups[group_id - 1]["created_at"]
        })
        member_id += 1

        # Add other members
        potential_members = list(range(1, len(users) + 1))
        potential_members.remove(creator_id)  # Remove creator

        actual_num_members = min(num_members, len(potential_members))
        member_ids = random.sample(potential_members, actual_num_members)

        for user_id in member_ids:
            role = random.choices(
                ["member", "moderator", "admin"],
                weights=[0.8, 0.15, 0.05],
                k=1
            )[0]

            joined_at = max(
                groups[group_id - 1]["created_at"],
                users[user_id - 1]["created_at"]
            ) + datetime.timedelta(days=safe_randint(0, 180))

            group_members.append({
                "group_member_id": member_id,
                "group_id": group_id,
                "user_id": user_id,
                "role": role,
                "joined_at": joined_at
            })
            member_id += 1


def generate_hashtags() -> None:
    """Generate hashtags."""
    logger.info("Generating hashtags...")
    global hashtags

    for i, tag in enumerate(HASHTAGS):
        hashtags.append({
            "hashtag_id": i + 1,
            "tag": tag,
            "created_at": datetime.datetime.now() - datetime.timedelta(days=safe_randint(0, 365))
        })


def generate_posts_and_interactions() -> None:
    """Generate posts and all related interactions."""
    logger.info("Generating posts and interactions...")
    global posts, poll_options, poll_votes, post_hashtags, post_reactions, comments, comment_reactions, post_shares, post_media

    post_id = 1
    poll_option_id = 1
    poll_vote_id = 1
    post_hashtag_id = 1
    reaction_id = 1
    comment_id = 1
    comment_reaction_id = 1
    share_id = 1
    media_id = 1

    # For each user, generate posts
    for user_id in tqdm(range(1, len(users) + 1)):
        # Determine number of posts for this user
        num_posts = safe_randint(*CONFIG["posts"]["posts_per_user"])

        # User's creation date
        user_created_at = users[user_id - 1]["created_at"]

        # Generate posts
        for _ in range(num_posts):
            # Determine if this is a repost/share
            is_repost = random.random() < (CONFIG["posts"]["shared_post_percentage"] / 100)
            original_post_id = None
            to_user_id = -1  # Default value

            if is_repost and post_id > 10:  # Only repost if we have enough posts
                original_post_id = safe_randint(1, post_id - 1)

            # Determine if post is to another user's wall
            if not is_repost and random.random() < 0.1:  # 10% of posts are to other users
                to_user_id = random.choice([i for i in range(1, len(users) + 1) if i != user_id])

            # Determine if this is a poll
            is_poll = random.random() < (CONFIG["posts"]["poll_percentage"] / 100)
            poll_question = None
            poll_duration_type = None
            poll_duration_length = None
            poll_end_datetime = None

            if is_poll:
                poll_question = fake.sentence()
                poll_duration_type = random.choice(POLL_DURATIONS)
                poll_duration_length = safe_randint(1, 10)

                # Calculate end date based on duration
                created_at = user_created_at + datetime.timedelta(days=safe_randint(1, 365))
                if poll_duration_type == "hours":
                    poll_end_datetime = created_at + datetime.timedelta(hours=poll_duration_length)
                elif poll_duration_type == "days":
                    poll_end_datetime = created_at + datetime.timedelta(days=poll_duration_length)
                else:  # weeks
                    poll_end_datetime = created_at + datetime.timedelta(weeks=poll_duration_length)

            # Generate post content
            content_text = None
            if not is_repost or random.random() < 0.5:  # 50% of reposts have additional text
                content_text = fake.paragraph(nb_sentences=safe_randint(1, 10))
                if len(content_text) > CONFIG["content"]["max_post_length"]:
                    content_text = content_text[:CONFIG["content"]["max_post_length"]]

            # Random location (20% of posts have location)
            location_name = None
            location_lat = None
            location_lng = None

            if random.random() < 0.2:
                location_name = fake.city()
                location_lat = float(fake.latitude())
                location_lng = float(fake.longitude())

            # Add post
            post_created_at = user_created_at + datetime.timedelta(days=safe_randint(1, 365))
            post_updated_at = post_created_at

            # Sometimes update the post
            if random.random() < 0.1:  # 10% of posts are edited
                post_updated_at = post_created_at + datetime.timedelta(minutes=safe_randint(1, 60 * 24))

            posts.append({
                "post_id": post_id,
                "user_id": user_id,
                "to_user_id": to_user_id,
                "original_post_id": original_post_id,
                "impressions": safe_randint(10, 1000),
                "views": safe_randint(5, 500),
                "content_text": content_text,
                "created_at": post_created_at,
                "updated_at": post_updated_at,
                "location_name": location_name,
                "location_lat": location_lat,
                "location_lng": location_lng,
                "is_poll": is_poll,
                "poll_question": poll_question,
                "poll_duration_type": poll_duration_type,
                "poll_duration_length": poll_duration_length,
                "poll_end_datetime": poll_end_datetime
            })

            # Generate poll options if this is a poll
            if is_poll:
                num_options = safe_randint(*CONFIG["posts"]["poll_options_per_poll"])

                for i in range(num_options):
                    option_text = fake.sentence(nb_words=safe_randint(2, 6))

                    poll_options.append({
                        "poll_option_id": poll_option_id,
                        "post_id": post_id,
                        "option_text": option_text,
                        "vote_count": 0  # Will be updated after votes are added
                    })

                    # Generate votes for this option
                    num_votes = safe_randint(*CONFIG["posts"]["poll_votes_per_option"])
                    voter_ids = random.sample(range(1, len(users) + 1), min(num_votes, len(users)))

                    for voter_id in voter_ids:
                        # Skip if user created the poll after voter joined
                        if users[voter_id - 1]["created_at"] > post_created_at:
                            continue

                        # Add vote
                        voted_at = post_created_at + datetime.timedelta(
                            minutes=safe_randint(1, int((poll_end_datetime - post_created_at).total_seconds() / 60)))

                        poll_votes.append({
                            "poll_vote_id": poll_vote_id,
                            "post_id": post_id,
                            "poll_option_id": poll_option_id,
                            "user_id": voter_id,
                            "voted_at": voted_at
                        })
                        poll_vote_id += 1

                    poll_option_id += 1

            # Add hashtags to post
            num_hashtags = safe_randint(*CONFIG["posts"]["hashtags_per_post"])
            post_hashtag_ids = random.sample(range(1, len(hashtags) + 1), min(num_hashtags, len(hashtags)))

            for hashtag_id in post_hashtag_ids:
                post_hashtags.append({
                    "post_hashtag_id": post_hashtag_id,
                    "post_id": post_id,
                    "hashtag_id": hashtag_id
                })
                post_hashtag_id += 1

            # Add reactions to post
            num_reactions = safe_randint(*CONFIG["posts"]["reactions_per_post"])
            reactor_ids = random.sample(range(1, len(users) + 1), min(num_reactions, len(users)))

            for reactor_id in reactor_ids:
                # Skip if reactor joined after post was created
                if users[reactor_id - 1]["created_at"] > post_created_at:
                    continue

                reaction_type = random.choice(REACTION_TYPES)
                reacted_at = post_created_at + datetime.timedelta(
                    minutes=safe_randint(1, 60 * 24 * 7))  # Within a week

                post_reactions.append({
                    "post_reaction_id": reaction_id,
                    "post_id": post_id,
                    "user_id": reactor_id,
                    "reaction_type": reaction_type,
                    "reacted_at": reacted_at
                })
                reaction_id += 1

            # Add comments to post
            # Use typical range for most posts, full range for some
            if random.random() < 0.2:  # 20% of posts use full comment range
                num_comments = safe_randint(*CONFIG["posts"]["comments_per_post"])
            else:
                num_comments = safe_randint(*CONFIG["posts"]["typical_comments_range"])

            commenter_ids = random.sample(range(1, len(users) + 1), min(num_comments, len(users)))

            for commenter_id in commenter_ids:
                # Skip if commenter joined after post was created
                if users[commenter_id - 1]["created_at"] > post_created_at:
                    continue

                comment_text = fake.paragraph(nb_sentences=safe_randint(1, 3))
                if len(comment_text) > CONFIG["content"]["max_comment_length"]:
                    comment_text = comment_text[:CONFIG["content"]["max_comment_length"]]

                comment_created_at = post_created_at + datetime.timedelta(
                    minutes=safe_randint(1, 60 * 24 * 14))  # Within two weeks
                comment_updated_at = comment_created_at

                # Sometimes update the comment
                if random.random() < 0.05:  # 5% of comments are edited
                    comment_updated_at = comment_created_at + datetime.timedelta(minutes=safe_randint(1, 60))

                comments.append({
                    "comment_id": comment_id,
                    "post_id": post_id,
                    "user_id": commenter_id,
                    "content_text": comment_text,
                    "created_at": comment_created_at,
                    "updated_at": comment_updated_at
                })

                # Add reactions to comment
                num_comment_reactions = safe_randint(0, 10)
                comment_reactor_ids = random.sample(range(1, len(users) + 1), min(num_comment_reactions, len(users)))

                for reactor_id in comment_reactor_ids:
                    # Skip if reactor joined after comment was created
                    if users[reactor_id - 1]["created_at"] > comment_created_at:
                        continue

                    reaction_type = random.choice(REACTION_TYPES)
                    reacted_at = comment_created_at + datetime.timedelta(
                        minutes=safe_randint(1, 60 * 24 * 3))  # Within three days

                    comment_reactions.append({
                        "comment_reaction_id": comment_reaction_id,
                        "comment_id": comment_id,
                        "user_id": reactor_id,
                        "reaction_type": reaction_type,
                        "reacted_at": reacted_at
                    })
                    comment_reaction_id += 1

                comment_id += 1

            # Add shares to post
            if random.random() < (CONFIG["posts"]["shared_post_percentage"] / 100):
                num_shares = safe_randint(1, 10)
                sharer_ids = random.sample(range(1, len(users) + 1), min(num_shares, len(users)))

                for sharer_id in sharer_ids:
                    # Skip if sharer is post creator or joined after post was created
                    if sharer_id == user_id or users[sharer_id - 1]["created_at"] > post_created_at:
                        continue

                    shared_at = post_created_at + datetime.timedelta(
                        minutes=safe_randint(1, 60 * 24 * 30))  # Within a month

                    post_shares.append({
                        "share_id": share_id,
                        "post_id": post_id,
                        "user_id": sharer_id,
                        "shared_at": shared_at
                    })
                    share_id += 1

            # Add media to post
            if random.random() < (CONFIG["posts"]["image_post_percentage"] / 100):
                num_media = safe_randint(*CONFIG["posts"]["images_per_post"])

                for _ in range(num_media):
                    media_type = random.choices(MEDIA_TYPES, weights=[0.9, 0.1], k=1)[0]  # 90% images, 10% videos

                    # Use sample media or generate URL
                    if POST_MEDIA and media_type == "image" and random.random() < 0.7:
                        media_url = random.choice(POST_MEDIA)
                    else:
                        media_url = f"https://voizy-app.s3.amazonaws.com/posts/{post_id}/media_{media_id}.{media_type}"

                    post_media.append({
                        "media_id": media_id,
                        "post_id": post_id,
                        "media_url": media_url,
                        "media_type": media_type,
                        "uploaded_at": post_created_at
                    })
                    media_id += 1

            post_id += 1


def generate_recommendation_models() -> None:
    """Generate recommendation models and user/content embeddings."""
    logger.info("Generating recommendation models and embeddings...")
    global recommendation_models, user_embeddings, content_embeddings

    # Create a couple of recommendation models
    model_types = ["collaborative", "content_based", "hybrid"]

    for i, model_type in enumerate(model_types):
        created_at = datetime.datetime.now() - datetime.timedelta(days=30 * (i + 1))

        # Sample model weights
        weights = {
            "collaborative": {
                "user_similarity": 0.4,
                "content_similarity": 0.3,
                "popularity": 0.2,
                "recency": 0.1
            },
            "content_based": {
                "interest_match": 0.5,
                "hashtag_match": 0.3,
                "text_similarity": 0.2
            },
            "hybrid": {
                "collaborative_score": 0.4,
                "content_based_score": 0.4,
                "popularity_score": 0.1,
                "recency_score": 0.1
            }
        }

        # Sample metrics
        metrics = {
            "precision": random.uniform(0.3, 0.6),
            "recall": random.uniform(0.3, 0.6),
            "ndcg": random.uniform(0.3, 0.7),
            "click_through_rate": random.uniform(0.05, 0.2)
        }

        recommendation_models.append({
            "model_id": i + 1,
            "model_type": model_type,
            "model_version": f"1.{i}.0",
            "model_weights": json.dumps(weights[model_type]),
            "metrics": json.dumps(metrics),
            "created_at": created_at,
            "is_active": i == len(model_types) - 1  # Most recent is active
        })

    # Generate user embeddings (simple random vectors for demonstration)
    embedding_id = 1
    embedding_types = ["interest", "behavior", "combined"]

    for user_id in range(1, len(users) + 1):
        for embedding_type in embedding_types:
            # Generate random embedding vector (64 dimensions)
            embedding_vector = [random.uniform(-1, 1) for _ in range(64)]

            # Normalize
            norm = np.linalg.norm(embedding_vector)
            if norm > 0:
                embedding_vector = [v / norm for v in embedding_vector]

            user_embeddings.append({
                "embedding_id": embedding_id,
                "user_id": user_id,
                "embedding_vector": json.dumps(embedding_vector),
                "embedding_type": embedding_type,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=safe_randint(1, 30)),
                "updated_at": datetime.datetime.now() - datetime.timedelta(days=safe_randint(0, 7))
            })
            embedding_id += 1

    # Generate content embeddings for posts
    embedding_id = 1
    embedding_types = ["text", "hashtag", "combined"]

    for post_id in range(1, len(posts) + 1):
        # Only create embeddings for a subset of posts to save time
        if random.random() < 0.3:  # 30% of posts get embeddings
            for embedding_type in embedding_types:
                # Generate random embedding vector (64 dimensions)
                embedding_vector = [random.uniform(-1, 1) for _ in range(64)]

                # Normalize
                norm = np.linalg.norm(embedding_vector)
                if norm > 0:
                    embedding_vector = [v / norm for v in embedding_vector]

                content_embeddings.append({
                    "embedding_id": embedding_id,
                    "content_id": post_id,
                    "embedding_vector": json.dumps(embedding_vector),
                    "embedding_type": embedding_type,
                    "created_at": posts[post_id - 1]["created_at"],
                    "updated_at": posts[post_id - 1]["created_at"] + datetime.timedelta(hours=safe_randint(1, 24))
                })
                embedding_id += 1


def insert_data_to_db() -> None:
    """Insert all generated data into the database."""
    try:
        logger.info("Connecting to database...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Helper function to insert data
        def insert_data(table_name, data, columns=None):
            if not data:
                logger.warning(f"No data to insert for {table_name}")
                return 0

            if columns is None:
                columns = data[0].keys()

            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))

            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

            rows = []
            for item in data:
                row = [item[col] if col in item else None for col in columns]
                rows.append(row)

            logger.info(f"Inserting {len(rows)} rows into {table_name}...")

            # Insert in batches to avoid memory issues
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                cursor.executemany(query, batch)
                conn.commit()

            return len(rows)

        # Insert data into tables
        total_rows = 0

        # API Keys
        total_rows += insert_data("api_keys", api_keys)

        # Users and profiles
        total_rows += insert_data("users", users)
        total_rows += insert_data("user_profiles", user_profiles)

        # Interests
        total_rows += insert_data("interests", interests)
        total_rows += insert_data("user_interests", user_interests)

        # Schools
        # For user_schools, we need to handle different column names
        user_schools_columns = ["user_school_id", "user_id", "school_name", "start_year", "end_year"]
        total_rows += insert_data("user_schools", user_schools, user_schools_columns)

        # Social links
        total_rows += insert_data("user_social_links", social_links)

        # User images
        total_rows += insert_data("user_images", user_images)

        # Friendships
        total_rows += insert_data("friendships", friendships)

        # Groups
        total_rows += insert_data("groups_table", groups)
        total_rows += insert_data("group_members", group_members)

        # Hashtags
        total_rows += insert_data("hashtags", hashtags)

        # Posts and related content
        total_rows += insert_data("posts", posts)
        total_rows += insert_data("poll_options", poll_options)
        total_rows += insert_data("poll_votes", poll_votes)
        total_rows += insert_data("post_hashtags", post_hashtags)
        total_rows += insert_data("post_reactions", post_reactions)
        total_rows += insert_data("comments", comments)
        total_rows += insert_data("comment_reactions", comment_reactions)
        total_rows += insert_data("post_shares", post_shares)
        total_rows += insert_data("post_media", post_media)

        # Recommendation models and embeddings
        # Create tables if not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendation_models (
            model_id          INT PRIMARY KEY AUTO_INCREMENT,
            model_type        VARCHAR(100) NOT NULL,
            model_version     VARCHAR(50) NOT NULL,
            model_weights     JSON,
            metrics           JSON,
            created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            is_active         BOOLEAN NOT NULL DEFAULT FALSE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_embeddings (
            embedding_id      INT PRIMARY KEY AUTO_INCREMENT,
            user_id           BIGINT NOT NULL,
            embedding_vector  JSON NOT NULL,
            embedding_type    VARCHAR(50) NOT NULL,
            created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_embeddings (
            embedding_id      INT PRIMARY KEY AUTO_INCREMENT,
            content_id        BIGINT NOT NULL,
            embedding_vector  JSON NOT NULL,
            embedding_type    VARCHAR(50) NOT NULL,
            created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES posts(post_id) ON DELETE CASCADE
        )
        """)

        conn.commit()

        # Insert recommendation data
        total_rows += insert_data("recommendation_models", recommendation_models)
        total_rows += insert_data("user_embeddings", user_embeddings)
        total_rows += insert_data("content_embeddings", content_embeddings)

        logger.info(f"Successfully inserted {total_rows} total rows.")

        # Update vote counts in poll_options
        logger.info("Updating poll vote counts...")
        cursor.execute("""
        UPDATE poll_options po
        SET vote_count = (
            SELECT COUNT(*) FROM poll_votes pv
            WHERE pv.poll_option_id = po.poll_option_id
        )
        """)
        conn.commit()

        logger.info("Data generation and insertion complete!")

    except Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logger.info("Database connection closed.")

def safe_randint(min_val, max_val):
    if min_val >= max_val:
        return min_val
    return random.randint(min_val, max_val)

def main():
    """Main function to coordinate data generation and insertion."""
    start_time = time.time()

    # Validate database connection
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()
        logger.info("Database connection successful.")
    except Error as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

    # Generate data
    generate_users()
    generate_interests()
    generate_schools()
    generate_social_links()
    generate_user_images()
    generate_friendships()
    generate_groups()
    generate_hashtags()
    generate_posts_and_interactions()
    generate_recommendation_models()

    # Insert data to database
    insert_data_to_db()

    elapsed_time = time.time() - start_time
    logger.info(f"Total execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()