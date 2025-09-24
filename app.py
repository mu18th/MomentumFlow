from flask import Flask, g, render_template, request, redirect, jsonify, url_for, make_response, session, flash
from db import get_db, close_db
from werkzeug.security import check_password_hash, generate_password_hash
from kanbanAI import generate_subtasks
from helpers import apology, login_required
from flask_session import Session

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#db related routes
with app.app_context():
    db = get_db()

    db.commit()
    
@app.teardown_appcontext
def teardown_appcontext_db(exception):
    close_db()


# index route
@app.route("/")
@login_required
def index():
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", (session["user_id"],)).fetchall()
    return render_template("index.html", tasks=tasks)


#not important routes
@app.route("/about")
def about():
    
    return render_template("about.html")

@app.route("/tasks")
@login_required
def tasks():
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? ORDERED BY priority", (session["user_id"],))
    return render_template("tasks.html", tasks=tasks)


#add task route
@app.route("/addtask",  methods=["GET", "POST"])
@login_required
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
                   (task, session["user_id"], description, priority, status))
        db.commit()

        flash("Task added!")
        return redirect("/")
    else:
        return render_template("addtask.html")


#to delete drag and drop
@app.route("/delete-task",  methods=["POST"])
@login_required
def deleteTask():
    task = request.get_json()

    id = int(task.get("taskID"))
    if not id:
        return jsonify({"message": "not valid ID"}) , 400
    
    db.execute("DELETE FROM tasks WHERE user_id = ? AND id = ?", (session["user_id"],id))
    db.commit()
    
    return jsonify({"taskID": id, "message": "updated"}), 200


#to update drag and drop
@app.route("/update-status",  methods=["POST"])
@login_required
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
@login_required
def generateSubtasks():
    
    task = request.get_json()

    id = int(task.get("taskID"))
    if not id:
        return jsonify({"message": "not valid ID"}) , 400
    
    title, description, status, priority = db.execute("SELECT title, description, status, priority FROM tasks WHERE id = ?", 
                                                      (id,)).fetchone()
    
    subtasks = generate_subtasks(title, description)

    if subtasks == "Error":
        flash("Error generating subtasks, please try again later.")
        return jsonify({"message": "could not generate tasks"}) , 400
    
    for t in subtasks:
        db.execute("INSERT INTO tasks (user_id, title, status, priority, description) VALUES (?, ?, ?, ?, ?)", 
                   (session["user_id"], "Subtask of: " + title, status, priority, t))
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
            return redirect(url_for("register", msg="passwords do not match"))
        
        try:
            db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", 
                    (username, email, generate_password_hash(password)))
            db.commit()
        except:
            return redirect(url_for("register", msg="username or email already exists"))

        return redirect(url_for("login", msg="Registered! Please log in."))
    else:
        msg = request.args.get("msg")
        if msg:
            flash(msg)
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 400)
        
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 400)
        
        data = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

        if len(data) != 1 or not check_password_hash(data[0]["hash"], password):
            return redirect(url_for("login", msg="Invalid username and/or password."))
        

        session["user_id"] = data[0]["id"]
        session["username"] = data[0]["username"]

        flash("Logged in successfully.")    
        return redirect("/")
    
    else:
        msg = request.args.get("msg")
        if msg:
            flash(msg)
        return render_template("login.html")
    
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.")

    return redirect(url_for("login", msg="You have been logged out"))

if __name__ == "__main__":
    app.run(debug=True)