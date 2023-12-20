from flask import Blueprint, request, render_template, redirect, url_for
from sqlalchemy import select
from db import db
from models.user import User

# Creates the account "router" (aka blueprint in Flask)
bp = Blueprint("accounts", __name__)

@bp.route("/register", methods=("GET", "POST"))
@bp.route("/register.html", methods=("GET", "POST"))
def register():
    """
    Handle the register page, with the form to register.
    """
    if request.method == "POST":
        # Get the username and password from the form
        username = request.form["username"]
        password = request.form["password"]
        password_repeat = request.form["password_repeat"]
        # Validate the form
        if username is None or password is None or password_repeat is None:
            return ("Missing username or password", 400)
        if password != password_repeat:
            return ("Passwords don't match", 400)
        if len(password) < 8:
            return ("Password too short (8 min)", 400)
        if len(password) > 50:
            return ("Password too long (50 max)", 400)
        if len(username) < 3:
            return ("Username too short (3 min)", 400)
        if len(username) > 50:
            return ("Username too long (50 max)", 400)
        # Check if the username is already taken
        if db.session.execute(select(User).filter(User.username == username)).first() is not None:
            return ("Username already taken", 400)
        db.session.close()
        # Create the user
        db.session.begin()
        try:
            user = User(username=username, password=User.hash_password(password))
            db.session.add(user)
        except Exception as e:
            print(e)
            db.rollback()
            return ("An error occured", 500)
        else:
            db.session.commit()
            return ("User created", 201)
    return render_template("register.html")