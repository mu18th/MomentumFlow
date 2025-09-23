#from CS50 finance task
import requests

from flask import redirect, request, render_template, session, url_for
from functools import wraps


def apology(message, code=400):

    return render_template("apology.html", message=message), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
        
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function