import sqlite3
from flask import Flask, g, render_template, request, url_for, redirect
from db import get_db, close_db

from helpers import apology

app = Flask(__name__)
app.config["DATABASE"] = "instance/smart_kanban.db"

with app.app_context():
    db = get_db()

    db.commit()

@app.route("/")
def index():
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", (1,)).fetchall()
    return render_template("index.html", tasks=tasks)

@app.route("/about")
def about():
    
    return render_template("about.html")

@app.route("/tasks")
def tasks():
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", (1,))
    return render_template("tasks.html", tasks=tasks)

@app.route("/addtask",  methods=["GET", "POST"])
def addtask():
    if request.method == "POST":
        task = request.form.get("task")
        if not task:
            return apology("must provide task", 400)
        
        description = request.form.get("description")
        if not description:
            description = ""

        priority = request.form.get("priority")
        if not priority:
            return apology("must spacify priority", 400)
        
        status= request.form.get("status")
        if not status:
            return apology("must spacify type", 400)
        
        db.execute("INSERT INTO tasks (title, user_id, description, priority, status) VALUES (?, ?, ?, ?, ?)", 
                   (task, 1, description, priority, status))
        db.commit()

        return redirect("/")
    else:
        return render_template("addtask.html")


#db related
@app.teardown_appcontext
def teardown_appcontext_db(exception):
    close_db()

if __name__ == "__main__":
    app.run(debug=True)