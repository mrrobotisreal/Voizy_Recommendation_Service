import os
import random
import datetime
import string
import hashlib
import logging
import csv
import tempfile
import secrets
import sys
import asyncio
import signal

from typing import List, Dict, Tuple
from faker import Faker
from dotenv import load_dotenv
from tqdm import tqdm
import numpy as np
from multiprocessing import Pool, cpu_count

# Optional resource checks
import psutil

import mysql.connector
from mysql.connector import pooling, Error

load_dotenv()

# -------------------------------------------------------------------
#   LOGGING CONFIG - Very Verbose
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("data-generator")

# -------------------------------------------------------------------
#   DB & SCRIPT CONFIG
# -------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "voizy",
    "user": "mwintrow",
    "password": os.getenv("DBP"),
    "pool_name": "mypool",
    "pool_size": 24,
    "allow_local_infile": True
}

CONFIG = {
    "users": {
        "count": 150_000,
        "generation_chunk_size": 10_000,
        "posts_per_user": (3, 50),
        "friends_per_user": (5, 1000),
    },
    "posts": {
        "views_per_post": (3, 150_000),
        "reaction_ratio": (0.33, 0.66),
        "comment_ratio": (0.33, 0.66),
        "share_ratio": (0.33, 0.66),
    },
    "caps": {
        "max_reactions": 100,
        "max_comments": 50,
        "max_shares": 100,
    },
    "safeguards": {
        "max_ram_percent": 92,
        "max_cpu_percent": 94
    },
    "db_read_chunk_size": 10_000,
    "num_processes": 24
}

fake = Faker()

db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
terminate_flag = False


def signal_handler(sig, frame):
    global terminate_flag
    logger.info("Received SIGINT, initiating graceful shutdown.")
    terminate_flag = True

signal.signal(signal.SIGINT, signal_handler)

# ---------------------------------------------------------------------
#   RESOURCE CHECK
# ---------------------------------------------------------------------
def check_resources():
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=0)
    if ram > CONFIG["safeguards"]["max_ram_percent"]:
        logger.error(f"RAM usage {ram}% > {CONFIG['safeguards']['max_ram_percent']}% - aborting chunk.")
        return False
    if cpu > CONFIG["safeguards"]["max_cpu_percent"]:
        logger.warning(f"CPU usage {cpu}% > {CONFIG['safeguards']['max_cpu_percent']}%")
    return True

# ---------------------------------------------------------------------
#   CSV BULK LOAD
# ---------------------------------------------------------------------
def bulk_insert_csv(table_name: str, data: List[Dict], columns: List[str]):
    """
    Writes 'data' to a temp CSV, then calls LOAD DATA LOCAL INFILE.
    Do NOT include auto-increment columns in 'columns'.
    """
    if not data:
        return

    conn = db_pool.get_connection()
    cursor = conn.cursor()

    tmp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv")
    writer = csv.DictWriter(tmp_file, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    tmp_file.close()

    load_sql = f"""
        LOAD DATA LOCAL INFILE '{tmp_file.name}'
        INTO TABLE {table_name}
        FIELDS TERMINATED BY ',' ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 LINES
        ({", ".join(columns)})
    """
    try:
        logger.debug(f"Loading {len(data)} records into {table_name}...")
        cursor.execute(load_sql)
        conn.commit()
        logger.debug(f"Finished loading {len(data)} records into {table_name}.")
    except Error as e:
        logger.error(f"Error loading data infile to {table_name}: {e}")
    finally:
        cursor.close()
        conn.close()
        os.remove(tmp_file.name)


# ---------------------------------------------------------------------
#   RANDOM HELPERS
# ---------------------------------------------------------------------
def generate_salt() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode()).hexdigest()

def skewed_randint(min_val, max_val, skew=2):
    return int(np.random.power(skew) * (max_val - min_val) + min_val)

REACTION_TYPES = ["like","love","laugh","congratulate","shocked","sad","angry"]
REACTION_WEIGHTS = [0.5, 0.25, 0.15, 0.05, 0.02, 0.02, 0.01]

# ---------------------------------------------------------------------
#   PHASE 1: Generate & Insert Users
# ---------------------------------------------------------------------
def generate_users_chunk(args) -> List[Dict]:
    """
    Do NOT include user_id (auto-increment).
    Just build these columns: (api_key, email, salt, password_hash, username, created_at, updated_at).

    Ensures uniqueness by embedding the global index into email/username/api_key.
    """
    start_idx, end_idx = args
    local_users = []

    start_date = datetime.datetime.now() - datetime.timedelta(days=365 * 5)
    total_count = end_idx - start_idx

    logger.info(f"Generating users for range [{start_idx}, {end_idx}) ...")

    for i in range(start_idx, end_idx):
        if terminate_flag:
            break
        if (i % 200) == 0:
            if not check_resources():
                logger.error("Resource check failed while generating users.")
                break
            logger.debug(f"User index {i} / {end_idx} ...")

        unique_suffix = str(i)
        salt_val = generate_salt()
        password_hash_val = hash_password(fake.password(), salt_val)

        user_dict = {
            "api_key":      f"api_key_{unique_suffix}",
            "email":        f"user_{unique_suffix}@test.com",
            "salt":         salt_val,
            "password_hash": password_hash_val,
            "username":     f"username_{unique_suffix}",
            "created_at":   fake.date_time_between(start_date, "now"),
            "updated_at":   datetime.datetime.now()
        }
        local_users.append(user_dict)

    logger.info(f"Finished generating {len(local_users)} user records in chunk.")
    return local_users

# ---------------------------------------------------------------------
#   PHASE 2: Generate & Insert Posts referencing user_id
# ---------------------------------------------------------------------
def fetch_users_for_posts(offset: int, limit: int):
    """
    Only the actual user_id, plus created_at needed.
    They are mapped to posts by referencing user_id.
    """
    conn = db_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT user_id, created_at
        FROM users
        ORDER BY user_id
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (limit, offset))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def generate_posts_chunk(args) -> List[Dict]:
    """
    Skip post_id (auto-increment).
    Create columns: user_id, to_user_id, impressions, views, content_text, created_at, updated_at,
                          location_name, location_lat, location_lng, is_poll
    """
    user_slice = args
    local_posts = []

    logger.info(f"Generating posts for chunk of {len(user_slice)} users...")

    for idx, user in enumerate(user_slice):
        if terminate_flag:
            break
        if (idx % 200) == 0:
            if not check_resources():
                logger.error("Resource check failed while generating posts.")
                break
            logger.debug(f"User slice index {idx}/{len(user_slice)} ...")

        user_id = user["user_id"]
        user_created_at = user["created_at"]

        num_posts = skewed_randint(*CONFIG["users"]["posts_per_user"], skew=2)

        for _p in range(num_posts):
            views = skewed_randint(*CONFIG["posts"]["views_per_post"], skew=3)
            impressions = views * 2
            created_at_post = fake.date_time_between(user_created_at, "now")

            post_dict = {
                "user_id": user_id,
                "to_user_id": -1,
                "impressions": impressions,
                "views": views,
                "content_text": fake.paragraph(),
                "created_at": created_at_post,
                "updated_at": created_at_post,
                "location_name": fake.city() if random.random() < 0.2 else None,
                "location_lat": float(fake.latitude()) if random.random() < 0.2 else None,
                "location_lng": float(fake.longitude()) if random.random() < 0.2 else None,
                "is_poll": 0
            }
            local_posts.append(post_dict)

    logger.info(f"Finished generating {len(local_posts)} posts for chunk.")
    return local_posts

# ---------------------------------------------------------------------
#   PHASE 3: Generate Post Interactions referencing post_id
# ---------------------------------------------------------------------
def fetch_posts_for_interactions(offset: int, limit: int):
    """
    Get the auto-incremented post_id and user_id from 'posts'.
    Use them to generate reactions, comments, shares by referencing post_id & user_id
    """
    conn = db_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT post_id, user_id, created_at
        FROM posts
        ORDER BY post_id
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (limit, offset))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def generate_post_interactions_chunk(args):
    """
    For each post in this chunk, create:
      - reactions (capped at max_reactions)
      - comments (capped at max_comments)
      - shares (capped at max_shares)

    Should produce 3 separate lists:
      post_reactions: (post_id, user_id, reaction_type, reacted_at)
      comments: (post_id, user_id, content_text, created_at, updated_at)
      post_shares: (post_id, user_id, shared_at)

    We skip the auto-increment IDs for each table, letting MySQL do it.
    """
    posts_slice = args
    local_reactions = []
    local_comments = []
    local_shares = []

    max_reactions = CONFIG["caps"]["max_reactions"]
    max_comments  = CONFIG["caps"]["max_comments"]
    max_shares    = CONFIG["caps"]["max_shares"]

    logger.info(f"Generating interactions for {len(posts_slice)} posts...")

    for idx, post_row in enumerate(posts_slice):
        if terminate_flag:
            break
        if (idx % 200) == 0:
            if not check_resources():
                logger.error("Resource check failed while generating post interactions.")
                break
            logger.debug(f"Post slice index {idx}/{len(posts_slice)} ...")

        post_id = post_row["post_id"]
        user_id_owner = post_row["user_id"]
        post_created_at = post_row["created_at"]

        views = random.randint(0, 149_999)  # <- don't forget to adjust this to correspond to the num users generated

        # Reactions
        # ratio-based
        ratio = random.uniform(*CONFIG["posts"]["reaction_ratio"])
        num_reactions = min(int(ratio * views), max_reactions)
        for _r in range(num_reactions):
            local_reactions.append({
                "post_id": post_id,
                "user_id": random.randint(1, CONFIG["users"]["count"]),  # random user referencing
                "reaction_type": random.choices(REACTION_TYPES, weights=REACTION_WEIGHTS, k=1)[0],
                "reacted_at": fake.date_time_between(post_created_at, "now")
            })

        # Comments
        ratio_c = random.uniform(*CONFIG["posts"]["comment_ratio"])
        num_comments = min(int(ratio_c * num_reactions), max_comments)
        for _c in range(num_comments):
            local_comments.append({
                "post_id": post_id,
                "user_id": random.randint(1, CONFIG["users"]["count"]),
                "content_text": fake.sentence(),
                "created_at": fake.date_time_between(post_created_at, "now"),
                "updated_at": datetime.datetime.now()
            })

        # Shares
        ratio_s = random.uniform(*CONFIG["posts"]["share_ratio"])
        num_shares = min(int(ratio_s * num_reactions), max_shares)
        for _s in range(num_shares):
            local_shares.append({
                "post_id": post_id,
                "user_id": random.randint(1, CONFIG["users"]["count"]),
                "shared_at": fake.date_time_between(post_created_at, "now")
            })

    logger.info(f"Finished generating interactions. Reactions={len(local_reactions)}, Comments={len(local_comments)}, Shares={len(local_shares)}")
    return (local_reactions, local_comments, local_shares)


# ---------------------------------------------------------------------
#   PHASE 4: Generate Friendships referencing user_id
# ---------------------------------------------------------------------
def fetch_users_for_friendships(offset: int, limit: int):
    """
    Fetches user_id from 'users' again to create random friend pairs.
    """
    conn = db_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT user_id
        FROM users
        ORDER BY user_id
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (limit, offset))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def generate_friendships_chunk(args):
    """
    Produces rows for `friendships` table:
      (user_id, friend_id, status, created_at)
    Skip friendship_id (auto-increment).
    """
    users_slice = args
    local_friendships = []
    pairs = set()

    logger.info(f"Generating friendships for {len(users_slice)} users...")

    for idx, user_row in enumerate(users_slice):
        if terminate_flag:
            break
        if (idx % 200) == 0:
            if not check_resources():
                logger.error("Resource check failed while generating friendships.")
                break

        user_id = user_row["user_id"]
        # random num of friends
        friend_factor = random.randint(*CONFIG["users"]["friends_per_user"])
        # generate random friend IDs
        for _f in range(friend_factor):
            friend_id = random.randint(1, CONFIG["users"]["count"])
            if friend_id == user_id:
                continue
            pair = tuple(sorted([user_id, friend_id]))
            if pair not in pairs:
                pairs.add(pair)
                local_friendships.append({
                    "user_id": user_id,
                    "friend_id": friend_id,
                    "status": "accepted",
                    "created_at": datetime.datetime.now()
                })

    logger.info(f"Finished generating {len(local_friendships)} friendships in chunk.")
    return local_friendships


# ---------------------------------------------------------------------
#   MAIN - MULTI-PHASE
# ---------------------------------------------------------------------
def main():
    global terminate_flag
    num_processes = CONFIG["num_processes"]
    logger.info(f"Using {num_processes} processes on {cpu_count()} cores.")

    # TODO: add real network calls for trending topics, etc.

    # ----------------------------------
    # PHASE 1: Generate & load users
    # ----------------------------------
    logger.info("PHASE 1: Generating & loading users in chunks.")
    user_count = CONFIG["users"]["count"]
    generation_chunk_size = CONFIG["users"]["generation_chunk_size"]

    user_tasks = []
    for start in range(0, user_count, generation_chunk_size):
        end = min(start + generation_chunk_size, user_count)
        user_tasks.append((start, end))

    with Pool(num_processes) as pool:
        # tqdm progress bar for user generation
        for chunk_result in tqdm(pool.imap_unordered(generate_users_chunk, user_tasks), total=len(user_tasks)):
            if terminate_flag:
                break
            if chunk_result:
                columns = list(chunk_result[0].keys())
                bulk_insert_csv("users", chunk_result, columns)

    logger.info("PHASE 1 complete. Users inserted.")

    if terminate_flag:
        logger.info("Terminated after Phase 1.")
        return

    # ----------------------------------
    # PHASE 2: Generate & load posts
    # ----------------------------------
    logger.info("PHASE 2: Generating posts referencing the actual user_id from DB.")
    offset = 0
    read_size = CONFIG["db_read_chunk_size"]

    with Pool(num_processes) as pool:
        while True:
            if terminate_flag:
                break
            users_slice = fetch_users_for_posts(offset, read_size)
            if not users_slice:
                break
            offset += len(users_slice)

            sub_size = max(5_000, len(users_slice) // num_processes)
            tasks = []
            for i in range(0, len(users_slice), sub_size):
                tasks.append(users_slice[i : i + sub_size])

            all_posts = []
            for posts_chunk in pool.imap_unordered(generate_posts_chunk, tasks):
                if posts_chunk:
                    all_posts.extend(posts_chunk)

            if all_posts:
                columns = list(all_posts[0].keys())  # user_id, to_user_id, ...
                batch_size = 10_000
                for i in range(0, len(all_posts), batch_size):
                    partial = all_posts[i : i + batch_size]
                    bulk_insert_csv("posts", partial, columns)

            if len(users_slice) < read_size:
                logger.info("No more users to read for posts; PHASE 2 done.")
                break

    if terminate_flag:
        logger.info("Terminated after Phase 2.")
        return

    # ----------------------------------
    # PHASE 3: Generate post interactions (reactions, comments, shares)
    # ----------------------------------
    logger.info("PHASE 3: Generating reactions/comments/shares referencing post_id.")
    offset = 0

    with Pool(num_processes) as pool:
        while True:
            if terminate_flag:
                break
            posts_slice = fetch_posts_for_interactions(offset, read_size)
            if not posts_slice:
                break
            offset += len(posts_slice)

            sub_size = max(5_000, len(posts_slice) // num_processes)
            tasks = []
            for i in range(0, len(posts_slice), sub_size):
                tasks.append(posts_slice[i : i + sub_size])

            all_reactions = []
            all_comments = []
            all_shares = []

            for (reactions, comments, shares) in pool.imap_unordered(generate_post_interactions_chunk, tasks):
                if reactions:
                    all_reactions.extend(reactions)
                if comments:
                    all_comments.extend(comments)
                if shares:
                    all_shares.extend(shares)

            if all_reactions:
                col_r = list(all_reactions[0].keys())
                batch_size = 10_000
                for i in range(0, len(all_reactions), batch_size):
                    partial = all_reactions[i : i + batch_size]
                    bulk_insert_csv("post_reactions", partial, col_r)

            if all_comments:
                col_c = list(all_comments[0].keys())
                batch_size = 10_000
                for i in range(0, len(all_comments), batch_size):
                    partial = all_comments[i : i + batch_size]
                    bulk_insert_csv("comments", partial, col_c)

            if all_shares:
                col_s = list(all_shares[0].keys())
                batch_size = 10_000
                for i in range(0, len(all_shares), batch_size):
                    partial = all_shares[i : i + batch_size]
                    bulk_insert_csv("post_shares", partial, col_s)

            if len(posts_slice) < read_size:
                logger.info("No more posts to read for interactions; PHASE 3 done.")
                break

    if terminate_flag:
        logger.info("Terminated after Phase 3.")
        return

    # ----------------------------------
    # PHASE 4: Generate friendships referencing user_id
    # ----------------------------------
    logger.info("PHASE 4: Generating friendships referencing user_id again.")
    offset = 0

    with Pool(num_processes) as pool:
        while True:
            if terminate_flag:
                break
            user_slice = fetch_users_for_friendships(offset, read_size)
            if not user_slice:
                break
            offset += len(user_slice)

            sub_size = max(5_000, len(user_slice) // num_processes)
            tasks = []
            for i in range(0, len(user_slice), sub_size):
                tasks.append(user_slice[i : i + sub_size])

            all_friends = []
            for friend_chunk in pool.imap_unordered(generate_friendships_chunk, tasks):
                if friend_chunk:
                    all_friends.extend(friend_chunk)

            if all_friends:
                col_f = list(all_friends[0].keys())
                batch_size = 10_000
                for i in range(0, len(all_friends), batch_size):
                    partial = all_friends[i : i + batch_size]
                    bulk_insert_csv("friendships", partial, col_f)

            if len(user_slice) < read_size:
                logger.info("No more users to read for friendships; PHASE 4 done.")
                break

    logger.info("All phases complete. Data generation done!")


if __name__ == "__main__":
    main()
