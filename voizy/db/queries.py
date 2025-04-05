"""
SQL queries used by the Voizy recommender system.
"""

INTERACTIONS_QUERY = """
-- Post views (weight: 1)
SELECT 
    user_id, 
    object_id AS post_id, 
    1 AS interaction_strength,
    'view' AS interaction_type, 
    ae.event_time AS timestamp
FROM analytics_events ae
WHERE ae.event_type = 'post_view'
  AND ae.object_type = 'post'
  AND ae.event_time > '{cutoff_date}'

UNION ALL

-- Post reactions (weight: 3)
SELECT 
    user_id, 
    post_id, 
    3 AS interaction_strength,
    'reaction' AS interaction_type, 
    reacted_at AS timestamp
FROM post_reactions
WHERE reacted_at > '{cutoff_date}'

UNION ALL

-- Post comments (weight: 4)
SELECT 
    user_id, 
    post_id, 
    4 AS interaction_strength,
    'comment' AS interaction_type, 
    created_at AS timestamp
FROM comments
WHERE created_at > '{cutoff_date}'

UNION ALL

-- Post shares (weight: 5)
SELECT 
    user_id, 
    post_id, 
    5 AS interaction_strength,
    'share' AS interaction_type, 
    shared_at AS timestamp
FROM post_shares
WHERE shared_at > '{cutoff_date}'
"""

USER_FEATURES_QUERY = """
-- Basic user info
SELECT 
    u.user_id,
    DATE(u.created_at) AS user_join_date,
    up.city_of_residence,
    TIMESTAMPDIFF(YEAR, up.birth_date, CURDATE()) AS age,
    NULL as interests
FROM users u
LEFT JOIN user_profiles up ON u.user_id = up.user_id

UNION ALL

-- User interests
SELECT 
    ui.user_id,
    NULL AS user_join_date,
    NULL AS city_of_residence,
    NULL AS age,
    GROUP_CONCAT(i.name) AS interests
FROM user_interests ui
JOIN interests i ON ui.interest_id = i.interest_id
GROUP BY ui.user_id
"""

POST_FEATURES_QUERY = """
-- Basic post info
SELECT 
    p.post_id,
    p.user_id AS author_id,
    p.content_text,
    p.created_at,
    p.is_poll,
    CASE WHEN p.location_name IS NOT NULL THEN 1 ELSE 0 END AS has_location,
    p.views,
    p.impressions,
    NULL AS hashtags,
    NULL AS media_type
FROM posts p
WHERE p.created_at > '{cutoff_date}'

UNION ALL

-- Post hashtags
SELECT 
    ph.post_id,
    NULL AS author_id,
    NULL AS content_text,
    NULL AS created_at,
    NULL AS is_poll,
    NULL AS has_location,
    NULL AS views,
    NULL AS impressions,
    GROUP_CONCAT(h.tag) AS hashtags,
    NULL AS media_types
FROM post_hashtags ph
JOIN hashtags h ON ph.hashtag_id = h.hashtag_id
JOIN posts p ON ph.post_id = p.post_id
WHERE p.created_at > '{cutoff_date}'
GROUP BY ph.post_id

UNION ALL

-- Post media types
SELECT 
    pm.post_id,
    NULL AS author_id,
    NULL AS content_text,
    NULL AS created_at,
    NULL AS is_poll,
    NULL AS has_location,
    NULL AS views,
    NULL AS impressions,
    NULL AS hashtags,
    GROUP_CONCAT(pm.media_type) AS media_types
FROM post_media pm
JOIN posts p ON pm.post_id = p.post_id
WHERE p.created_at > '{cutoff_date}'
GROUP BY pm.post_id
"""

USER_INTERACTIONS_QUERY = """
-- Posts the user has viewed
SELECT DISTINCT object_id AS post_id
FROM analytics_events
WHERE user_id = %s 
  AND event_type = 'post_view'
  AND object_type = 'post'

UNION

-- Posts the user has reacted to
SELECT DISTINCT post_id
FROM post_reactions
WHERE user_id = %s

UNION

-- Posts the user has commented on
SELECT DISTINCT post_id
FROM comments
WHERE user_id = %s

UNION

-- Posts the user has shared
SELECT DISTINCT post_id
FROM post_shares
WHERE user_id = %s
"""

POPULAR_POSTS_QUERY = """
SELECT p.post_id,
       (p.views * 1 + 
        COUNT(DISTINCT pr.post_reaction_id) * 3 + 
        COUNT(DISTINCT c.comment_id) * 4 + 
        COUNT(DISTINCT ps.share_id) * 5) AS score
FROM posts p
LEFT JOIN post_reactions pr ON p.post_id = pr.post_id
LEFT JOIN comments c ON p.post_id = c.post_id
LEFT JOIN post_shares ps ON p.post_id = ps.post_id
WHERE p.created_at > '{cutoff_date}'
GROUP BY p.post_id
ORDER BY score DESC
LIMIT {limit}
"""