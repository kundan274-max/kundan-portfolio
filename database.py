import sqlite3


def get_db_connection():
    connection = sqlite3.connect("portfolio.db")
    connection.row_factory = sqlite3.Row
    return connection


# ================= PROFILE TABLE =================


def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            name TEXT,
            title TEXT,
            about TEXT,
            photo TEXT
        )
    """)

    connection.commit()
    connection.close()


def add_default_profile():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM profile WHERE id = 1")

    profile = cursor.fetchone()

    if profile is None:
        cursor.execute(
            """
            INSERT INTO profile (id, name, title, about, photo)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                1,
                "Kundan Kumar",
                "BCA Student",
                "I am a BCA 3rd-semester student at Jharkhand Rai University. I am learning Python programming and exploring web development by building practical projects.",
                "portfolio.jpeg",
            ),
        )

        connection.commit()

    connection.close()


# ================= SKILLS TABLE =================


def create_skills_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def add_default_skills():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM skills")
    count = cursor.fetchone()[0]

    if count == 0:
        skills = [("Python",), ("C",), ("Flask",)]

        cursor.executemany("INSERT INTO skills (name) VALUES (?)", skills)

        connection.commit()

    connection.close()
