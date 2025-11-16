# Standard library imports
import os

# Third-party imports
from flask import Flask, render_template, request, redirect, jsonify, url_for, make_response, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Local application imports
from db import *
from MomentumFlowAI import generate_subtasks, suggest_next_task, summarize_board
from helpers import apology, login_required, get_date_deatails

# Configure application
app = Flask(__name__)
init_db()
app.teardown_appcontext(close_db)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

""" board routes """

@app.route("/")
@login_required
def index():
    """main app page, show the the kanban board and responsible of filter and search process"""

    # listener variables for any search and/or filter inputs 
    search = request.args.get("search", "").strip()
    priority = request.args.get("priority")
    start = request.args.get("start")
    end = request.args.get("end")

    # quary and parameters depends on user inputs for search and filter, if no, show all tasks
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

    # create queries
    tasks = execute_filtered_query(query, parameters)
    subtasks = get_subtasks(session["user_id"])

    # get date of today and to days after for due-date logic
    today, after_tommorow = get_date_deatails()

    return render_template("index.html", 
        tasks=tasks, 
        subtasks=subtasks, 
        today=today, 
        after_tommorow=after_tommorow
    )

 
@app.route("/column/<string:status>/html")
@login_required
def column_html(status):
    """ function to update the whole column if a task droped on it, mainly for done column
        because a btns (subtasks generator) and some details should not be shown on it 
        like due-date, priority, subtasks"""
    
    column_id = None
    if status == "To Do":
        column_id = "todo"
    elif status == "In Progress":
        column_id = "in-progress"
    elif status == "Done":
        column_id = "done"
    else:
        return jsonify({"error": f"Invalid status: {status}"}), 400

    bg_color = (
        "var(--back-todo)" if status == "To Do"
        else "var(--back-progress)" if status == "In Progress"
        else "var(--back-done)"
    )

    tasks = get_tasks_by_user(session["user_id"])
    subtasks = get_subtasks(session["user_id"])
    today, after_tommorow = get_date_deatails()

    return render_template(
        "/_column.html",
        tasks=tasks,
        subtasks=subtasks,
        column_id=column_id,
        column_title=status,
        bg_color=bg_color,
        today=today,
        after_tommorow=after_tommorow
    )

""" form routes """

@app.route("/addtask",  methods=["GET", "POST"])
@login_required
def addtask():
    """function connected to addtask form, get data of task from user and register it on db"""

    # if post, register date if  and return user to the board, else reunder the page for the user (get call)
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

@app.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def editTask(id):
    """a function to update any of the task data, show a form like the addtask form
       useful for generated subtasks, can be accessed through a URL simmilar to a btn"""
    
    # if post call method, deal with data and update them in the quary, otherwise render the 
    # if the call is valid, else flash a message for bad call
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

""" js routes """

@app.route("/delete-task",  methods=["POST"])
@login_required
def deleteTask():
    """function to delete task through post using Js (btn delete task), if updated is parent all subtasks
       are deleted from the db and user is asked to refresh the page through showMessage Js"""

    task = request.get_json()

    id = int(task.get("taskID"))
    if not id:
        return jsonify({"message": "not valid ID"}) , 400
    
    # if it's a parent task, delete any subtasks of it and then delete it
    delete_subtasks_tree(session["user_id"], id)
    
    return jsonify({"taskID": id, "message": "updated"}), 200


@app.route("/update-status",  methods=["POST"])
@login_required
def updateTaskStatus():
    """function to update status by post through Js (drag and drop), if updated is parent and is done
       all of its childs are moved to done column and refresh is forced in DragAndDrop method"""
    
    task = request.get_json()

    id = int(task.get("taskID"))
    
    if not id:
        return jsonify({"message": "not updated"}) , 400
        
    status = task.get("status")
    if not status:
        return jsonify({"message": "not updated"}) , 400
    
    update_subtasks_tree(session["user_id"], id, status)

    subtasks = True if get_subtasks_by_parent(session["user_id"], id) else False

    return jsonify({"taskID": id, "status": status, "subtasks": subtasks, "message": "updated"}), 200

""" AI routes """

@app.route("/generate_subtasks", methods=["POST"])
@login_required
def generateSubtasks():
    """a function call AI to generate 3 subtasks of a specific task (break it to three subtasks) 
       connected to "Generate 3 subtasks" btn"""

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


@app.route("/next_task", methods=["GET"])
@login_required
def nextTask():
    """a function call AI to suggest a specific task that the user should work on, if AI failed: 
       it return the task with highest oreder in the quary (done tasks are not involved in it)
       connected to "what should I do know" btn"""

    tasks = get_tasks_notDone(session["user_id"])

    if not tasks:
        flash("No Tasks Yet")
        return jsonify({"summary": "No Tasks Yet"})
    
    next_task_id = suggest_next_task(tasks)

    # if falls, return first in the list
    if not next_task_id:
        next_task_id = tasks[0]["id"]

    return jsonify({"task_id": next_task_id})


@app.route("/summary", methods=["POST"])
@login_required
def summarizeBoard():
    """a function call AI to summarize the board, and add the summary to summary quary
       connected to "Refresh summary" btn"""
    
    tasks = get_tasks_by_user(session["user_id"])

    if not tasks:
        return jsonify({"summary": "No Tasks Yet"})
    
    summary = summarize_board(tasks)

    if summary.startswith("{") and summary.endswith("}"):
        summary = summary[1:-1].strip()
    
    add_summary(session["user_id"], summary)

    return jsonify({"summary": summary})


@app.route("/get_summary", methods=["GET"])
@login_required
def getSummay():
    """a function return last saved summary in the board
       connected to "Summarize the board" btn"""

    row = get_summary(session["user_id"])

    
    summary_text = row["summary"] if row else None
    
    return jsonify({"summary": summary_text})

""" Register and logging forms"""

@app.route("/register", methods=["GET", "POST"])
def register():
    """a function to register new user to the users quary"""

    # if post, try to register the use, if cannot flash a message (in same page), otherwise register new user
    # if get render the register form and show flashed message if any
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
    """a function to login a user to new session"""
    session.clear()

    # if post try to retrive the data , if wrong data flash message (in same page), otherwise log user in
    # if get, render the login form and show flashed message if any
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
    """a function to logthe user out and flash an indicate message"""
    session.clear()

    flash("Logged out successfully.")

    return redirect(url_for("login", msg="You have been logged out"))


if __name__ == "__main__":
    app.run(debug=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))