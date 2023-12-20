from db import db
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from login import LoggedUser
from models.user import User
from sqlalchemy import select

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
        if (
            db.session.execute(select(User).filter(User.username == username)).first()
            is not None
        ):
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


@bp.route("/login", methods=("GET", "POST"))
@bp.route("/login.html", methods=("GET", "POST"))
def login():
    """
    Handle the login page, with the form to login.

    It handles the authentication and the session creation.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username is None or password is None:
            return ("Missing username or password", 400)
        user = (
            db.session.execute(select(User).filter(User.username == username))
            .scalars()
            .first()
        )
        if user is None or (not User.verify_password(user, password)):
            # For security reasons, a website should not tell the
            # user if the username exists or not, otherwise an attacker
            # could use this to find valid usernames, or try to
            # retrace all the website used by a same person.
            return "Wrong credentials", 401
        login_user(LoggedUser(session_uid=user.session_uid))
        if "next" in request.args:
            return redirect(request.args["next"])
        return "Logged in", 200

    return render_template("login.html")


@bp.route("/logout")
@bp.route("/logout.html")
def logout():
    """
    Logout page.
    """
    if current_user.is_authenticated:
        logout_user()
    return "Logged out", 200


@bp.route("/me")
@bp.route("/me.html")
@login_required
def profile_me():
    """
    Profile page for the current user.
    """
    cu = current_user.get_user()
    return render_template("me.html", username=cu.username, bio=cu.bio)
