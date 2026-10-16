import sqlite3
import hashlib


DB_NAME = "events.db"


def create_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            event_hash TEXT UNIQUE,

            event_name TEXT,

            organizer TEXT,

            date TEXT,

            time TEXT,

            location TEXT,

            mode TEXT,

            deadline TEXT,

            fee TEXT,

            certificate TEXT,

            prize TEXT,

            registration_link TEXT,

            score INTEGER,

            reason TEXT,

            source TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            sent INTEGER DEFAULT 0
        )
    """)

    conn.commit()

    conn.close()


def generate_hash(event):

    raw = (
        event.get("event_name", "") +
        event.get("date", "") +
        event.get("location", "") +
        event.get("registration_link", "")
    )

    return hashlib.sha256(
        raw.lower().encode()
    ).hexdigest()


def save_event(event, source):

    event_hash = generate_hash(event)

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO events (
                event_hash,
                event_name,
                organizer,
                date,
                time,
                location,
                mode,
                deadline,
                fee,
                certificate,
                prize,
                registration_link,
                score,
                reason,
                source
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            event_hash,
            event.get("event_name"),
            event.get("organizer"),
            event.get("date"),
            event.get("time"),
            event.get("location"),
            event.get("mode"),
            event.get("deadline"),
            event.get("fee"),
            event.get("certificate"),
            event.get("prize"),
            event.get("registration_link"),
            event.get("score", 0),
            event.get("reason"),
            source
        ))

        conn.commit()

        inserted = True

    except sqlite3.IntegrityError:

        inserted = False

    conn.close()

    return inserted