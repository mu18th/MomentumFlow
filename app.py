import sqlite3
from flask import Flask, g, render_template, request, redirect, jsonify, make_response
from db import get_db, close_db

from kanbanAI import generate_subtasks
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
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? ORDERED BY priority", (1,))
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


"""@app.route("/update-status",  methods=["GET", "POST"])
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
        return render_template("update.html")"""
    
"""@app.route("/delete-task",  methods=["GET", "POST"])
def deleteTask():
    if request.method == "POST":
        id = request.form.get("taskID")

        if not id:
            return apology("must provide ID", 400)
    
        db.execute("DELETE FROM tasks WHERE id = ?", (id,))
        db.commit()

        return redirect("/")
    else:
        return render_template("delete.html")"""

@app.route("/delete-task",  methods=["POST"])
def deleteTask():
    task = request.get_json()

    id = int(task.get("taskID"))
    if not id:
        return jsonify({"message": "not valid ID"}) , 400
    
    db.execute("DELETE FROM tasks WHERE user_id = ? AND id = ?", (1,id))
    db.commit()
    
    return jsonify({"taskID": id, "message": "updated"}), 200


#to update drag and drop
@app.route("/update-status",  methods=["POST"])
def updateTask():
    
    task = request.get_json()

    id = int(task.get("taskID"))
    if not id:
        return jsonify({"message": "not updated"}) , 400
        
    status = task.get("status")
    if not status:
        return jsonify({"message": "not updated"}) , 400
        
    db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, id))
    db.commit()
        
    return jsonify({"taskID": id, "status": status, "message": "updated"}), 200
    

#AI subtasks
@app.route("/generate_subtasks", methods=["POST"])
def generateSubtasks():
    
    task = request.get_json()

    id = int(task.get("taskID"))
    if not id:
        return jsonify({"message": "not valid ID"}) , 400
    
    title, description, status, priority = db.execute("SELECT title, description, status, priority FROM tasks WHERE id = ?", (id,)).fetchone()
    
    subtasks = generate_subtasks(title, description)

    if subtasks == "Error":
        return jsonify({"message": "could not generate tasks"}) , 400
    
    for t in subtasks:
        db.execute("INSERT INTO tasks (user_id, title, status, priority, description) VALUES (?, ?, ?, ?, ?)", 
                   (1, "Subtask of: " + title, status, priority, t))
        db.commit()
    
    return jsonify({"taskID": id, "message": "updated"}), 200

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("username")
        if not user_name:
            return apology("must provide username", 400)
        
        email = request.form.get("email")
        if not email:
            return apology("must provide email", 400)
        
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 400)
        
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must provide password confirmation", 400)
        
        if password != confirmation:
            return apology("passwords do not match", 400)
        
        return redirect("/")
    else:
        return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)