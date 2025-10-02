import sqlite3
from flask import g

DATABASE = "instance/smart_kanban.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False  
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
        
def init_db():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hash TEXT NOT NULL
                )
            """)

            # Create tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                title TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'To Do',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                priority TEXT NOT NULL, 
                due_date DATE,
                parent_id INTEGER DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,            
                user_id INTEGER NOT NULL,
                summary TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            """)

            conn.commit()
            print("Tables created successfully")
    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")


def get_tasks_by_user(user_id):
    db = get_db()
    return db.execute(
        """SELECT * FROM tasks WHERE user_id = ? ORDER BY 
        CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, 
        due_date ASC, 
        CASE priority 
            WHEN 'high' THEN 1 
            WHEN 'medium' THEN 2 
            WHEN 'low' THEN 3 
        END ASC; 
        """,(user_id,)).fetchall()


def get_task_by_id(task_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM tasks WHERE id = ?", 
        (task_id,)).fetchall()

def get_subtasks(user_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND parent_id IS NOT NULL ORDER BY parent_id",
        (user_id,)).fetchall()


def get_tasks_notDone(user_id):
    db = get_db()
    return db.execute("""
        SELECT id, title, description, status, priority, due_date, parent_id
        FROM tasks
        WHERE user_id = ? AND status != 'Done'
        ORDER BY
            CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
            due_date ASC,
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END ASC;
    """, (user_id,)).fetchall()

def add_task(title, user_id, description, status, priority, due_date, parent_id=None):
    db = get_db()
    db.execute(
        "INSERT INTO tasks (title, user_id, description, status, priority, due_date, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, user_id, description, status, priority, due_date, parent_id)
    )
    db.commit()


def delete_task(user_id, task_id):
    db = get_db()

    db.execute(
        "DELETE FROM tasks WHERE user_id = ? AND id = ?", 
        (user_id, task_id))
    db.commit()

def delete_subtasks(parent_id):
    db = get_db()

    db.execute(
        "DELETE FROM tasks WHERE parent_id = ?", 
        (parent_id,))
    db.commit()

def update_status(status, task_id):
    db = get_db()

    db.execute(
        "UPDATE tasks SET status = ? WHERE id = ?", 
        (status, task_id))
    db.commit()


def update_task(id, title, description, priority, due_date):
    db = get_db()

    db.execute(
        "UPDATE tasks SET title = ?, description = ?, priority = ?, due_date = ? WHERE id = ?",
        (title, description, priority, due_date, id)
    )
    db.commit()


def register_user(username, email, password_hash):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    db.commit()


def get_user_by_username(username):
    db = get_db()
    return db.execute(
        "SELECT * FROM users WHERE username = ?", 
        (username,)).fetchall()

def add_summary(user_id, summary):
    db = get_db()
    db.execute(
        "INSERT INTO summaries (user_id, summary) VALUES (?, ?)",
        (user_id, summary)
    )
    db.commit()

def get_summary(user_id):
    db = get_db()
    return db.execute(
        "SELECT summary FROM summaries WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()

if __name__ == "__main__":
    init_db()

