import sqlite3
from flask import Flask, g, render_template, request, url_for, redirect
from db import get_db, close_db

from helpers import apology

app = Flask(__name__)
app.config["DATABASE"] = "instance/smart_kanban.db"

#db related
with app.app_context():
    db = get_db()

    db.commit()
    
@app.teardown_appcontext
def teardown_appcontext_db(exception):
    close_db()

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
        
        status = request.form.get("status")
        if not status:
            return apology("must spacify status", 400)
        
        db.execute("INSERT INTO tasks (title, user_id, description, priority, status) VALUES (?, ?, ?, ?, ?)", 
                   (task, 1, description, priority, status))
        db.commit()

        return redirect("/")
    else:
        return render_template("addtask.html")


@app.route("/update-status",  methods=["GET", "POST"])
def updateTask():
    if request.method == "POST":
        id = request.form.get("taskID")
    
        if not id:
            return apology("must provide ID", 400)
        
        status = request.form.get("status")
        if not status:
            return apology("must spacify status", 400)
        
        db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, id))
        db.commit()
        
        return redirect("/") 
    else:
        return render_template("update.html")
    
@app.route("/delete-task",  methods=["GET", "POST"])
def deleteTask():
    if request.method == "POST":
        id = request.form.get("taskID")

        if not id:
            return apology("must provide ID", 400)
    
        db.execute("DELETE FROM tasks WHERE id = ?", (id,))
        db.commit()

        return redirect("/")
    else:
        return render_template("delete.html")

if __name__ == "__main__":
    app.run(debug=True)