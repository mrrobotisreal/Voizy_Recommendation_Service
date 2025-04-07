import mysql.connector
import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("schema-creator")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "database": "voizy",
    "user": "mwintrow",
    "password": os.getenv("DBP")
}


def create_tables():
    """Create all tables in the database if they don't exist."""
    try:
        logger.info("Connecting to database...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Users and profiles
        logger.info("Creating API keys table...")
        api_keys_table = '''
        CREATE TABLE IF NOT EXISTS api_keys (
            api_key_id       BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id          BIGINT NOT NULL,
            api_key          VARCHAR(255) NOT NULL UNIQUE,
            created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at       DATETIME NOT NULL,
            last_used_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        '''
        cursor.execute(api_keys_table)

        logger.info("Creating users table...")
        users_table = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
            api_key         VARCHAR(255) NOT NULL UNIQUE,
            email           VARCHAR(255) NOT NULL UNIQUE,
            salt            VARCHAR(255) NOT NULL,
            password_hash   VARCHAR(255) NOT NULL,
            username        VARCHAR(50) NOT NULL UNIQUE,
            created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        '''
        cursor.execute(users_table)

        logger.info("Creating user profiles table...")
        user_profiles_table = '''
        CREATE TABLE IF NOT EXISTS user_profiles (
            profile_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id           BIGINT NOT NULL,
            first_name        VARCHAR(100),
            last_name         VARCHAR(100),
            preferred_name    VARCHAR(100),
            birth_date        DATE,
            city_of_residence VARCHAR(255),
            place_of_work     VARCHAR(255),
            date_joined       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(user_profiles_table)

        logger.info("Creating user schools table...")
        user_schools_table = '''
        CREATE TABLE IF NOT EXISTS user_schools (
            user_school_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id           BIGINT NOT NULL,
            school_name       VARCHAR(255) NOT NULL,
            start_year        INT,
            end_year          INT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(user_schools_table)

        logger.info("Creating interests table...")
        interests_table = '''
        CREATE TABLE IF NOT EXISTS interests (
            interest_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(255) NOT NULL UNIQUE
        );
        '''
        cursor.execute(interests_table)

        logger.info("Creating user interests table...")
        user_interests_table = '''
        CREATE TABLE IF NOT EXISTS user_interests (
            user_interest_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id          BIGINT NOT NULL,
            interest_id      BIGINT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (interest_id) REFERENCES interests(interest_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(user_interests_table)

        logger.info("Creating user social links table...")
        user_social_links_table = '''
        CREATE TABLE IF NOT EXISTS user_social_links (
            link_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id   BIGINT NOT NULL,
            platform  VARCHAR(100) NOT NULL,
            url       VARCHAR(255) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(user_social_links_table)

        logger.info("Creating user images table...")
        user_images_table = '''
        CREATE TABLE IF NOT EXISTS user_images (
            user_image_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id        BIGINT NOT NULL,
            image_url      VARCHAR(255) NOT NULL,
            is_profile_pic BOOLEAN NOT NULL DEFAULT 0,
            is_cover_pic   BOOLEAN NOT NULL DEFAULT 0,
            uploaded_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(user_images_table)

        logger.info("Creating songs table...")
        songs_table = '''
        CREATE TABLE IF NOT EXISTS songs (
            song_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
            title    VARCHAR(255) NOT NULL,
            artist   VARCHAR(255) NOT NULL,
            song_url VARCHAR(255) NOT NULL
        );
        '''
        cursor.execute(songs_table)

        logger.info("Creating user songs table...")
        user_songs_table = '''
        CREATE TABLE IF NOT EXISTS user_songs (
            user_song_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id      BIGINT NOT NULL,
            song_id      BIGINT NOT NULL,
            updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(user_songs_table)

        # Friendships
        logger.info("Creating friendships table...")
        friendships_table = '''
        CREATE TABLE IF NOT EXISTS friendships (
            friendship_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            friend_id     BIGINT NOT NULL,
            status        ENUM('pending','accepted','blocked') NOT NULL DEFAULT 'pending',
            created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (friend_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(friendships_table)

        # Groups
        logger.info("Creating groups table...")
        groups_table = '''
        CREATE TABLE IF NOT EXISTS groups_table (
            group_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(255) NOT NULL,
            description TEXT,
            privacy     ENUM('public','private','closed') NOT NULL DEFAULT 'public',
            creator_id  BIGINT NOT NULL,
            created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(groups_table)

        logger.info("Creating group members table...")
        group_members_table = '''
        CREATE TABLE IF NOT EXISTS group_members (
            group_member_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            group_id        BIGINT NOT NULL,
            user_id         BIGINT NOT NULL,
            role            ENUM('member','moderator','admin') NOT NULL DEFAULT 'member',
            joined_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups_table(group_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(group_members_table)

        # Posts
        logger.info("Creating posts table...")
        posts_table = '''
        CREATE TABLE IF NOT EXISTS posts (
            post_id            BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id            BIGINT NOT NULL,
            to_user_id         BIGINT NOT NULL DEFAULT -1,
            original_post_id   BIGINT NULL DEFAULT NULL,
            impressions        BIGINT NOT NULL DEFAULT 0,
            views              BIGINT NOT NULL DEFAULT 0,
            content_text       TEXT,
            created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            location_name      VARCHAR(255),
            location_lat       DECIMAL(9,6),
            location_lng       DECIMAL(9,6),
            is_poll            BOOLEAN NOT NULL DEFAULT 0,
            poll_question      VARCHAR(255),
            poll_duration_type ENUM('hours','days','weeks') DEFAULT 'days',
            poll_duration_length INT DEFAULT 1,
            poll_end_datetime  DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (original_post_id) REFERENCES posts(post_id) ON DELETE SET NULL
        );
        '''
        cursor.execute(posts_table)

        logger.info("Creating poll options table...")
        poll_options_table = '''
        CREATE TABLE IF NOT EXISTS poll_options (
            poll_option_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id        BIGINT NOT NULL,
            option_text    VARCHAR(255) NOT NULL,
            vote_count     INT DEFAULT 0,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(poll_options_table)

        logger.info("Creating poll votes table...")
        poll_votes_table = '''
        CREATE TABLE IF NOT EXISTS poll_votes (
            poll_vote_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id        BIGINT NOT NULL,
            poll_option_id BIGINT NOT NULL,
            user_id        BIGINT NOT NULL,
            voted_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (poll_option_id) REFERENCES poll_options(poll_option_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(poll_votes_table)

        logger.info("Creating hashtags table...")
        hashtags_table = '''
        CREATE TABLE IF NOT EXISTS hashtags (
            hashtag_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
            tag         VARCHAR(255) NOT NULL UNIQUE,
            created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        '''
        cursor.execute(hashtags_table)

        logger.info("Creating post hashtags table...")
        post_hashtags_table = '''
        CREATE TABLE IF NOT EXISTS post_hashtags (
            post_hashtag_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id         BIGINT NOT NULL,
            hashtag_id      BIGINT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (hashtag_id) REFERENCES hashtags(hashtag_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(post_hashtags_table)

        logger.info("Creating post reactions table...")
        post_reactions_table = '''
        CREATE TABLE IF NOT EXISTS post_reactions (
            post_reaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id          BIGINT NOT NULL,
            user_id          BIGINT NOT NULL,
            reaction_type    ENUM('like','love','laugh','congratulate','shocked','sad','angry') NOT NULL,
            reacted_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(post_reactions_table)

        logger.info("Creating comments table...")
        comments_table = '''
        CREATE TABLE IF NOT EXISTS comments (
            comment_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id      BIGINT NOT NULL,
            user_id      BIGINT NOT NULL,
            content_text TEXT NOT NULL,
            created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(comments_table)

        logger.info("Creating comment reactions table...")
        comment_reactions_table = '''
        CREATE TABLE IF NOT EXISTS comment_reactions (
            comment_reaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            comment_id          BIGINT NOT NULL,
            user_id             BIGINT NOT NULL,
            reaction_type       ENUM('like','love','laugh','congratulate','shocked','sad','angry') NOT NULL,
            reacted_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(comment_reactions_table)

        logger.info("Creating post shares table...")
        post_shares_table = '''
        CREATE TABLE IF NOT EXISTS post_shares (
            share_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id    BIGINT NOT NULL,
            user_id    BIGINT NOT NULL,
            shared_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(post_shares_table)

        logger.info("Creating post media table...")
        post_media_table = '''
        CREATE TABLE IF NOT EXISTS post_media (
            media_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id     BIGINT NOT NULL,
            media_url   VARCHAR(255) NOT NULL,
            media_type  ENUM('image','video') NOT NULL,
            uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(post_media_table)

        logger.info("Creating post views table...")
        post_views_table = '''
        CREATE TABLE IF NOT EXISTS post_views (
            view_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            viewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE KEY unique_view (post_id, user_id)
        )
        '''

        logger.info("Creating post impressions table...")
        post_impressions_table = '''
        CREATE TABLE IF NOT EXISTS post_impressions (
            impression_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            post_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            impressed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        '''

        # Messages and Chat
        logger.info("Creating conversations table...")
        conversations_table = '''
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
            conversation_name VARCHAR(255),
            is_group_chat     BOOLEAN NOT NULL DEFAULT 0,
            created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        '''
        cursor.execute(conversations_table)

        logger.info("Creating conversation members table...")
        conversation_members_table = '''
        CREATE TABLE IF NOT EXISTS conversation_members (
            conv_member_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
            conversation_id BIGINT NOT NULL,
            user_id         BIGINT NOT NULL,
            joined_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(conversation_members_table)

        logger.info("Creating messages table...")
        messages_table = '''
        CREATE TABLE IF NOT EXISTS messages (
            message_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
            conversation_id BIGINT NOT NULL,
            sender_id       BIGINT NOT NULL,
            content_text    TEXT,
            sent_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(messages_table)

        logger.info("Creating message recipients table...")
        message_recipients_table = '''
        CREATE TABLE IF NOT EXISTS message_recipients (
            msg_recipient_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            message_id       BIGINT NOT NULL,
            recipient_id     BIGINT NOT NULL,
            is_read          BOOLEAN NOT NULL DEFAULT 0,
            read_at          DATETIME,
            FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
            FOREIGN KEY (recipient_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(message_recipients_table)

        logger.info("Creating message attachments table...")
        message_attachments_table = '''
        CREATE TABLE IF NOT EXISTS message_attachments (
            attachment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            message_id    BIGINT NOT NULL,
            file_url      VARCHAR(255) NOT NULL,
            file_type     ENUM('image','video','doc') DEFAULT 'image',
            uploaded_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(message_attachments_table)

        logger.info("Creating message reactions table...")
        message_reactions_table = '''
        CREATE TABLE IF NOT EXISTS message_reactions (
            message_reaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            message_id          BIGINT NOT NULL,
            user_id             BIGINT NOT NULL,
            reaction_type       ENUM('like','love','laugh','congratulate','shocked','sad','angry') NOT NULL,
            reacted_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(message_reactions_table)

        # Analytics
        logger.info("Creating analytics events table...")
        analytics_events_table = '''
        CREATE TABLE IF NOT EXISTS analytics_events (
            event_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id      BIGINT NOT NULL,
            event_type   VARCHAR(100) NOT NULL,
            object_type  VARCHAR(100),
            object_id    BIGINT,
            event_time   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            meta_data      JSON,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        '''
        cursor.execute(analytics_events_table)

        conn.commit()
        logger.info("All tables created successfully!")

    except mysql.connector.Error as err:
        logger.error(f"MySQL Error: {err}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            logger.info("MySQL connection is closed")


def check_database_exists():
    """Check if the database exists, create it if it doesn't"""
    try:
        # Connect without specifying the database
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SHOW DATABASES LIKE '{DB_CONFIG['database']}'")
        result = cursor.fetchone()

        if not result:
            logger.info(f"Database '{DB_CONFIG['database']}' does not exist. Creating it...")
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            logger.info(f"Database '{DB_CONFIG['database']}' created successfully!")
        else:
            logger.info(f"Database '{DB_CONFIG['database']}' already exists.")

        conn.close()
        return True
    except mysql.connector.Error as err:
        logger.error(f"Error checking/creating database: {err}")
        return False


def main():
    """Main function"""
    if not check_database_exists():
        sys.exit(1)

    create_tables()


if __name__ == "__main__":
    main()
