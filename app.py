from flask import Flask, g, render_template, request, redirect, jsonify, make_response
from db import get_db, close_db
from werkzeug.security import check_password_hash, generate_password_hash
from kanbanAI import generate_subtasks
from helpers import apology

# Configure application and database
app = Flask(__name__)
app.config["DATABASE"] = "instance/smart_kanban.db"


#db related routes
with app.app_context():
    db = get_db()

    db.commit()
    
@app.teardown_appcontext
def teardown_appcontext_db(exception):
    close_db()


# index route
@app.route("/")
def index():
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", (1,)).fetchall()
    return render_template("index.html", tasks=tasks)


#not important routes
@app.route("/about")
def about():
    
    return render_template("about.html")

@app.route("/tasks")
def tasks():
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? ORDERED BY priority", (1,))
    return render_template("tasks.html", tasks=tasks)


#add task route
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


#to delete drag and drop
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


#register and logen routes
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
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
        
        try:
            db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", 
                    (username, email, generate_password_hash(password)))
            db.commit()
        except:
            return apology("username or email already exists", 400)

        return redirect("/")
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)