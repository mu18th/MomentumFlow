"""I have created this file to seperate db logic and sql commands from app logic 
   and replace redundency with a method calls"""

# Standard library imports
import os
import sqlite3

# Third-party imports
from flask import g

DATABASE = "instance/MomentumFolw.db"

# ORDER is a constante indicate the oreder of returned quary
ORDER =  """ORDER BY
                    CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
                    due_date ASC,
                    CASE priority
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                    END ASC;"""

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
                email TEXT NOT NULL,
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

            # create summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,            
                user_id INTEGER NOT NULL,
                summary TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            print("Tables created successfully")
    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")

def execute_filtered_query(query, parameters):
    db = get_db()
    return db.execute(f"{query} {ORDER}", parameters).fetchall()

def get_tasks_by_user(user_id):
    db = get_db()

    return db.execute(
        f"SELECT * FROM tasks WHERE user_id = ? {ORDER}",
        (user_id,)).fetchall()


def get_task_by_id(task_id):
    db = get_db()

    return db.execute(
        f"SELECT * FROM tasks WHERE id = ? {ORDER}", 
        (task_id,)).fetchall()

def get_subtasks(user_id):
    db = get_db()

    return db.execute(
        f"SELECT * FROM tasks WHERE user_id = ? AND parent_id IS NOT NULL ORDER BY parent_id",
        (user_id,)).fetchall()

def get_subtasks_by_parent(user_id, parent):
    db = get_db()

    return db.execute(
        f"SELECT id FROM tasks WHERE user_id = ? AND parent_id = ? {ORDER}",
        (user_id, parent)).fetchall()

def get_tasks_by_status(user_id, status):
    db = get_db()

    return db.execute(
        f"SELECT * FROM tasks WHERE user_id = ? AND status = ? {ORDER}",
        (user_id,status)).fetchall()

def get_tasks_notDone(user_id):
    db = get_db()

    return db.execute(f"""
        SELECT id, title, description, status, priority, due_date, parent_id
        FROM tasks
        WHERE user_id = ? AND status != 'Done'
        {ORDER}
    """, (user_id,)).fetchall()

def get_summary(user_id):
    db = get_db()
    return db.execute(
        "SELECT summary FROM summaries WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()

def add_task(title, user_id, description, status, priority, due_date, parent_id=None):
    db = get_db()

    db.execute(
        """
        INSERT INTO tasks (title, user_id, description, status, priority, due_date, parent_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (title, user_id, description, status, priority, due_date, parent_id)
    )
    db.commit()

def add_summary(user_id, summary):
    db = get_db()
    db.execute(
        "INSERT INTO summaries (user_id, summary) VALUES (?, ?)",
        (user_id, summary)
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


def update_task(id, title, description, status, priority, due_date):
    db = get_db()

    db.execute(
        "UPDATE tasks SET title = ?, description = ?, status = ?, priority = ?, due_date = ? WHERE id = ?",
        (title, description, status, priority, due_date, id)
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
        f"SELECT * FROM users WHERE username = ?", 
        (username,)).fetchall()

# recursive methods through db, not a sql cmds but they are db related
def delete_subtasks_tree(user_id, task_id):
    """recursive go through tree and delete subtasks if exists"""

    subtasks = get_subtasks_by_parent(user_id, task_id)
    
    for task in subtasks:
        delete_subtasks_tree(user_id, int(task["id"]))
        
    # delete the task itself
    delete_task(user_id, task_id)

def update_subtasks_tree(user_id, task_id, status):
    """recursive go through tree and update subtasks if status = Done"""

    if status != "Done":
        update_status(status, task_id)
        return
    
    subtasks = get_subtasks_by_parent(user_id, task_id)
    for task in subtasks:
        update_subtasks_tree(user_id, int(task["id"]), status)
    
    update_status("Done", task_id)

# for test case
if __name__ == "__main__":
    init_db()
