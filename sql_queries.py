import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

ARN = config.get("IAM_ROLE", "ARN")
LOG_DATA = config.get("S3", "LOG_DATA")
LOG_JSONPATH = config.get("S3", "LOG_JSONPATH")
SONG_DATA = config.get("S3", "SONG_DATA")

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events (
    artist VARCHAR,
    auth VARCHAR,
    firstName VARCHAR,
    gender VARCHAR,
    itemInSession INT,
    lastName VARCHAR,
    length VARCHAR,
    level VARCHAR,
    location VARCHAR,
    method VARCHAR,
    page VARCHAR,
    registration VARCHAR,
    sessionId INT SORTKEY DISTKEY,
    song VARCHAR,
    status INT,
    ts INT,
    userAgent VARCHAR,
    userId INT
)
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs (
    artist_id VARCHAR SORTKEY DISTKEY,
    artist_latitude VARCHAR,
    artist_location VARCHAR,
    artist_longitude VARCHAR,
    artist_name VARCHAR,
    duration VARCHAR,
    num_songs INT,
    song_id VARCHAR,
    title VARCHAR,
    year INT
)
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays(
    songplay_id INT IDENTITY(0,1) SORTKEY,
    startime TIMESTAMP NOT NULL,
    user_id INT NOT NULL DISTKEY,
    level VARCHAR NOT NULL,
    song_id VARCHAR NOT NULL,
    artist_id VARCHAR NOT NULL,
    session_id INT NOT NULL,
    location VARCHAR NOT NULL,
    user_agent VARCHAR NOT NULL
)
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users(
    user_id INT NOT NULL SORTKEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    gender VARCHAR NOT NULL,
    level VARCHAR NOT NULL
)
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs(
    song_id VARCHAR NOT NULL SORTKEY,
    title VARCHAR NOT NULL,
    artist_id VARCHAR NOT NULL,
    year VARCHAR INT NOT NULL,
    duration VARCHAR NOT NULL
)
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists(
    artist_id VARCHAR NOT NULL SORTKEY,
    name VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    lattitude VARCHAR NOT NULL,
    longitude VARCHAR NOT NULL
)
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time(
    start_time TIMESTAMP NOT NULL SORTKEY,
    hour INT NOT NULL,
    day INT NOT NULL,
    week INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    weekday VARCHAR NOT NULL
)
""")

# STAGING TABLES

staging_events_copy = ("""
    copy staging_events_copy from {} 
    credentials aws_iam_role {}
    json {};
""").format(LOG_DATA, ARN, LOG_JSONPATH)

staging_songs_copy = ("""
    copy staging_events_copy from {} 
    credentials aws_iam_role {}
    json 'auto';
""").format(SONG_DATA, ARN)

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT DISTINCT 
    timestamp with time zone 'epoch' + se.ts/1000 * interval '1 second', se.userId, se.level, 
    ss.song_id, ss.artist_id, se.sessionId, se.location, se.userAgent
FROM 
    staging_events AS se INNER JOIN staging_songs AS ss
ON 
    se.song = ss.title AND se.artist = ss.artist_name AND se.length = ss.duration
WHERE 
    se.page = 'NextSong'
""")

user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT 
    userId, firstName, lastName, gender, level
FROM 
    staging_events
WHERE 
    page = 'NextSong' AND userId IS NOT NULL
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT 
    song_id, title, artist_id, year, duration
FROM 
    staging_songs
WHERE 
    song_id IS NOT NULL
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT 
    artist_id, artist_name, artist_location, artist_latitude, artist_longitude
FROM 
    staging_songs
WHERE 
    artist_id IS NOT NULL
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT 
    start_time, 
    extract(hour from start_time), 
    extract(day from start_time), 
    extract(week from start_time), 
    extract(month from start_time), 
    extract(year from start_time), 
    extract(weekday from start_time)
FROM 
    songplays
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
