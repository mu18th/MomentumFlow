"""collection of functions that is not related to a specific logic, inspired from CS50 finance"""

# Standard library imports
from datetime import date, timedelta
from functools import wraps

# Third-party imports
from flask import redirect, request, render_template, session, url_for

def apology(message, code=400):
    """return the apology page an error occur and is not flashed"""
    
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

def get_date_deatails():
    """return date of today and after tommorow when called"""

    today = date.today()
    after_tomorrow = today + timedelta(days=2)
    return today, after_tomorrow
