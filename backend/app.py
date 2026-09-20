from flask import Flask, jsonify
import os
import mysql.connector

app = Flask(__name__)

DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']


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
    """Return data read dynamically from MySQL."""
    conn = get_connection()
    cur = conn.cursor()
    ensure_schema(cur)
    conn.commit()
    cur.execute("SELECT NOW(), views FROM page_views WHERE id = 1")
    database_time, views = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify(database_time=database_time.isoformat(sep=" "), views=views)


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

    return jsonify(views=views)


if __name__ == '__main__':
    # Dev-only fallback
    app.run(host='0.0.0.0', port=8000, debug=True)
