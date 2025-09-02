from flask import Flask, render_template

app = Flask(__name__)

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

@app.route("/form")
def form():
    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)