import sqlite3

DB_FILE = "db.sqlite"

SCHEMA_QUERIES = [
    
    """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT NOT NULL,
        dob TEXT NOT NULL,
        gender TEXT CHECK (gender IN ('male', 'female', 'other')) NOT NULL,
        address TEXT NOT NULL,
        role TEXT CHECK (role IN ('super_admin', 'artist_manager', 'artist')) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""",
    
    """CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dob TEXT NOT NULL,
        gender TEXT CHECK (gender IN ('male', 'female', 'other')) NOT NULL,
        address TEXT NOT NULL,
        first_released_year INTEGER NOT NULL,
        no_of_album_released INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""",
    
    """CREATE TABLE IF NOT EXISTS music (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        album_name TEXT NOT NULL,
        genre TEXT CHECK (genre IN ('rnb', 'country', 'classic', 'rock', 'jazz')) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
    );""",


]

def run_migrations():
    """Runs migrations to create necessary tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for query in SCHEMA_QUERIES:
        cursor.execute(query)

    conn.commit()
    conn.close()
    print("migrated successfully!")

if __name__ == "__main__":
    run_migrations()
