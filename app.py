import sqlite3
from flask import Flask, g, render_template, request, url_for
from db import get_db, close_db

from helpers import apology

app = Flask(__name__)
app.config["DATABASE"] = "instance/smart_kanban.db"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/tasks")
def tasks():
    tasks = ["x", "y", "z"]
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
        
        type= request.form.get("type")
        if not type:
            return apology("must spacify type", 400)
        
        #to complete storing

        return render_template("index.html")
    else:
        return render_template("addtask.html")


#db related
@app.teardown_appcontext
def teardown_appcontext_db(exception):
    close_db()

if __name__ == "__main__":
    app.run(debug=True)