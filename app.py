from flask import Flask, render_template, request, redirect, jsonify, url_for, make_response, session, flash
from db import *
from werkzeug.security import check_password_hash, generate_password_hash
from kanbanAI import generate_subtasks, suggest_next_task, summarize_board
from helpers import apology, login_required, get_date_deatails
from flask_session import Session
from urllib.parse import unquote

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# index route
@app.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    priority = request.args.get("priority")
    start = request.args.get("start")
    end = request.args.get("end")

    parameters = [session["user_id"]]
    query = "SELECT * FROM tasks WHERE user_id = ? "

    if search:
        query += "AND (title LIKE ? OR description LIKE ?) "
        like_search = f"%{search}%"
        parameters.extend([like_search, like_search])

    if priority:
        query += "AND priority = ? "
        parameters.append(priority)

    if start and end:
        query += "AND due_date BETWEEN ? AND ? "
        parameters.extend([start, end])

    query += "ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date ASC"

    tasks = execute_filtered_query(query, parameters)
    subtasks = get_subtasks(session["user_id"])

    today, after_tommorow = get_date_deatails()
    return render_template("index.html", tasks=tasks, subtasks=subtasks, today=today, after_tommorow=after_tommorow)


#not important routes
@app.route("/about")
def about():
    
    return render_template("about.html")

@app.route("/tasks")
@login_required
def tasks():
    tasks =  get_tasks_by_user(session["user_id"])
    subtasks = get_subtasks(session["user_id"])
    return render_template("tasks.html", tasks=tasks,  subtasks=subtasks)


#add task route
@app.route("/addtask",  methods=["GET", "POST"])
@login_required
def addtask():
    if request.method == "POST":
        title = request.form.get("title")
        if not title:
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
        
        due_date = request.form.get("due_date")
        if not due_date:
            due_date = None
        
        add_task(title, session["user_id"], description, status, priority, due_date)

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
    
    delete_subtasks(id)  
    delete_task(session["user_id"], id)
    
    return jsonify({"taskID": id, "message": "updated"}), 200


# to update status by drag and drop
@app.route("/update-status",  methods=["POST"])
@login_required
def updateTaskStatus():
    
    task = request.get_json()

    id = int(task.get("taskID"))

    subtasks = get_subtasks_by_parent(session["user_id"], id)

    if not id:
        return jsonify({"message": "not updated"}) , 400
        
    status = task.get("status")
    if not status:
        return jsonify({"message": "not updated"}) , 400
    
    if status == "Done":
        for t in subtasks:
            update_status(status, int(t["id"]))

    update_status(status, id)
    
    sub_ids = [sub["id"] for sub in subtasks]
    return jsonify({"taskID": id, "status": status, "subtask_ids": sub_ids, "message": "updated"}), 200
    
@app.route("/column/<string:status>/html")
@login_required
def column_html(status):

    column_id = None
    if status == "To Do":
        column_id = "todo"
    elif status == "In Progress":
        column_id = "in-progress"
    elif status == "Done":
        column_id = "done"
    else:
        return jsonify({"error": f"Invalid status: {status}"}), 400

    tasks = get_tasks_by_user(session["user_id"])
    subtasks = get_subtasks(session["user_id"])
    today, after_tommorow = get_date_deatails()

    return render_template(
        "/_column.html",
        tasks=tasks,
        subtasks=subtasks,
        column_id=column_id,
        column_title=status,
        bg_color = "var(--back-todo)" if status == "To Do" else ("var(--back-progress)" if status == "In Progress" else "var(--back-done)"),
        today=today,
        after_tommorow=after_tommorow
    )

@app.route("/next_task", methods=["GET"])
@login_required
def nextTask():
    tasks = get_tasks_notDone(session["user_id"])

    next_task_id = suggest_next_task(tasks)

    # if falls, return first in the list
    if not next_task_id:
        next_task_id = tasks[0]["id"]

    return jsonify({"task_id": next_task_id})


@app.route("/summary", methods=["POST"])
@login_required
def summarizeBoard():
    tasks = get_tasks_by_user(session["user_id"])

    summary = summarize_board(tasks)

    if summary.startswith("{") and summary.endswith("}"):
        summary = summary[1:-1].strip()
    
    add_summary(session["user_id"], summary)

    return jsonify({"summary": summary})


@app.route("/get_summary", methods=["GET"])
@login_required
def getSummay():
    row = get_summary(session["user_id"])

    if row:
        summary_text = row["summary"]
    else:
        summary_text = None
    
    return jsonify({"summary": summary_text})


@app.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def editTask(id):
    
    if request.method == "POST":
        title = request.form.get("title")
        if not title:
            return apology("must provide task", 400)
        
        description = request.form.get("description")
        if not description:
            description = ""
        
        priority = request.form.get("priority")
        if not priority:
            return apology("must spacify priority", 400)
        
        status =  request.form.get("status")
        if not status:
            return apology("must spacify status", 400)
        
        due_date = request.form.get("due_date")
        if not due_date:
            due_date = None

        update_task(id, title, description, status, priority, due_date)        


        flash("Task updated!")
        return redirect("/")
    else:
        task = get_task_by_id(id)
        if len(task) != 1:
            return redirect(url_for("index", msg="not your task"))
        
        return render_template("edittask.html", task=task[0])


#AI subtasks
@app.route("/generate_subtasks", methods=["POST"])
@login_required
def generateSubtasks():
    
    task = request.get_json()

    id = int(task.get("taskID"))
    if not id:
        return jsonify({"message": "not valid ID"}) , 400
    
    mainTask = get_task_by_id(id)
    if len(mainTask) != 1:
        return jsonify({"message": "not your task"}) , 400
    
    subtasks = generate_subtasks(mainTask[0]["title"], mainTask[0]["description"])

    if subtasks == "Error":
        return jsonify({"message": "could not generate tasks"}) , 500
    
    for task in subtasks:
        title = task.split()
        title = " ".join(title[1:2])
        add_task(title, session["user_id"], task,
                  mainTask[0]["status"], mainTask[0]["priority"], mainTask[0]["due_date"], id)
    
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
            email = "empty email"

        password = request.form.get("password")
        if not password:
            return apology("must provide password", 400)
        
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must provide password confirmation", 400)
        
        
        if password != confirmation:
            return redirect(url_for("register", msg="passwords do not match"))
        
        try:
            register_user(username, email, generate_password_hash(password))
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
        
        data = get_user_by_username(username)

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