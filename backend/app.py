import json
import logging
import os

import redis
import mysql.connector
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

app.logger.setLevel(logging.INFO)
cache = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'cache'),
    port=int(os.environ.get('REDIS_PORT', '6379')),
    db=0,
    decode_responses=True,
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
)
CACHE_KEY = 'visitor-counter:api'
CACHE_TTL_SECONDS = 10

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def ensure_schema(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS page_views (
            id TINYINT PRIMARY KEY,
            views INT NOT NULL DEFAULT 0
        )
        """
    )
    cursor.execute(
        "INSERT IGNORE INTO page_views (id, views) VALUES (1, 0)"
    )


@app.get('/api/health')
def health():
    return {'status': 'ok'}


@app.get('/api')
def index():
    """Return the visitor count and database time, using a short Redis cache."""
    try:
        cached = cache.get(CACHE_KEY)
        if cached:
            return jsonify(json.loads(cached))
    except (redis.RedisError, json.JSONDecodeError):
        app.logger.warning('Redis unavailable; reading /api data from MySQL')

    conn = get_connection()
    cur = conn.cursor()
    ensure_schema(cur)
    conn.commit()
    cur.execute("SELECT NOW(), views FROM page_views WHERE id = 1")
    database_time, views = cur.fetchone()
    cur.close()
    conn.close()

    response = {
        'database_time': database_time.isoformat(sep=' '),
        'views': views,
    }
    try:
        cache.set(CACHE_KEY, json.dumps(response), ex=CACHE_TTL_SECONDS)
    except redis.RedisError:
        app.logger.warning('Could not write /api response to Redis cache')
    return jsonify(response)


@app.post('/api/visit')
def register_visit():
    """Persist one page-view increment in MySQL and return the new value."""
    conn = get_connection()
    cur = conn.cursor()
    ensure_schema(cur)
    cur.execute("UPDATE page_views SET views = views + 1 WHERE id = 1")
    conn.commit()
    cur.execute("SELECT views FROM page_views WHERE id = 1")
    views = cur.fetchone()[0]
    cur.close()
    conn.close()

    try:
        cache.delete(CACHE_KEY)
    except redis.RedisError:
        # The short TTL bounds staleness if Redis cannot be reached to invalidate.
        app.logger.warning('Could not invalidate /api Redis cache after visit')

    return jsonify(views=views)


if __name__ == '__main__':
    # Dev-only fallback
    app.run(host='0.0.0.0', port=8000, debug=True)
