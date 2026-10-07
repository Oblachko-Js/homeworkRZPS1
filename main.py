import os
from contextlib import closing

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False
DATABASE_URL = os.environ["DATABASE_URL"]


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    with closing(get_conn()) as conn, conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT now()
            )
            """
        )


@app.get("/notes")
def list_notes():
    with closing(get_conn()) as conn, conn.cursor() as cur:
        cur.execute("SELECT id, text, created_at FROM notes ORDER BY id")
        rows = cur.fetchall()
    return jsonify(
        [{"id": r[0], "text": r[1], "created_at": r[2].isoformat()} for r in rows]
    )


@app.post("/notes")
def add_note():
    text = (request.get_json(silent=True) or {}).get("text")
    if not text:
        return jsonify({"error": "field 'text' is required"}), 400
    with closing(get_conn()) as conn, conn, conn.cursor() as cur:
        cur.execute("INSERT INTO notes (text) VALUES (%s) RETURNING id", (text,))
        note_id = cur.fetchone()[0]
    return jsonify({"id": note_id, "text": text}), 201


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
