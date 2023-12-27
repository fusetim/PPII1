from db import db
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from login import LoggedUser
from models.user import User
from sqlalchemy import select
from http import HTTPStatus
import uuid

# Creates the account "router" (aka blueprint in Flask)
bp = Blueprint("accounts", __name__)


@bp.route("/register", methods=("GET", "POST"))
@bp.route("/register.html", methods=("GET", "POST"))
def register():
    """
    Handle the register page, with the form to register.
    """
    messages = []
    status = HTTPStatus.OK
    if request.method == "POST":
        check = True
        # Get the username and password from the form
        username = request.form["username"]
        password = request.form["password"]
        password_repeat = request.form["password_repeat"]
        # Validate the form
        if username is None or password is None or password_repeat is None:
            messages.append(
                {
                    "content": "Mot de passe ou nom d'utilisateur manquant.",
                    "is_error": True,
                }
            )
            check = False
            status = HTTPStatus.BAD_REQUEST
        if password != password_repeat:
            messages.append(
                {"content": "Les mots de passe ne correspondent pas.", "is_error": True}
            )
            check = False
            status = HTTPStatus.BAD_REQUEST
        if len(password) < 8:
            messages.append(
                {
                    "content": "Le mot de passe est trop court. Choisissez un mot de passe d'au moins 8 caractères.",
                    "is_error": True,
                }
            )
            check = False
            status = HTTPStatus.BAD_REQUEST
        if len(password) > 50:
            messages.append(
                {
                    "content": "Le mot de passe est trop long, il doit faire moins de 50 caractères.",
                    "is_error": True,
                }
            )
            check = False
            status = HTTPStatus.BAD_REQUEST
        if len(username) < 3:
            messages.append(
                {
                    "content": "Le nom d'utilisateur est trop court. Choisissez un pseudonyme d'au moins 3 caractères.",
                    "is_error": True,
                }
            )
            check = False
            status = HTTPStatus.BAD_REQUEST
        if len(username) > 50:
            messages.append(
                {
                    "content": "Le pseudonyme est trop long, il doit faire moins de 50 caractères.",
                    "is_error": True,
                }
            )
            check = False
            status = HTTPStatus.BAD_REQUEST

        if check:
            # Check if the username is already taken
            if (
                db.session.execute(
                    select(User).filter(User.username == username)
                ).first()
                is not None
            ):
                messages.append(
                    {
                        "content": "Le pseudonyme est déjà utilisé, veuillez en choisir un autre.",
                        "is_error": True,
                    }
                )
                status = HTTPStatus.CONFLICT
            else:
                db.session.close()
                # Create the user
                db.session.begin()
                try:
                    user = User(
                        username=username, password=User.hash_password(password)
                    )
                    db.session.add(user)
                except Exception as e:
                    print(e)
                    db.rollback()
                    messages.append(
                        {
                            "content": "Une erreur serveur est survenue, veuillez réessayer dans quelques instants...",
                            "is_error": True,
                        }
                    )
                    status = HTTPStatus.INTERNAL_SERVER_ERROR
                else:
                    db.session.commit()
                    messages.append(
                        {
                            "content": "Votre compte a été créé avec succès. Vous pouvez désormais vous connecter :)",
                            "is_error": False,
                        }
                    )
                    status = HTTPStatus.CREATED
    return (render_template("register.html", messages=messages), status)


@bp.route("/login", methods=("GET", "POST"))
@bp.route("/login.html", methods=("GET", "POST"))
def login():
    """
    Handle the login page, with the form to login.

    It handles the authentication and the session creation.
    """
    messages = []
    status = HTTPStatus.OK
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username is None or password is None:
            messages.append(
                {"content": "Pseudonyme ou mot de passe manquant.", "is_error": True}
            )
            status = HTTPStatus.BAD_REQUEST
        else:
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
                messages.append(
                    {
                        "content": "Identifiant incorrect. Veuillez réessayer.",
                        "is_error": True,
                    }
                )
                status = HTTPStatus.FORBIDDEN
            else:
                login_user(LoggedUser(session_uid=user.session_uid))
                if "next" in request.args:
                    return redirect(request.args["next"])
                messages.append(
                    {
                        "content": "Bonjour @{} !".format(user.username),
                        "is_error": False,
                    }
                )

    return (render_template("login.html", messages=messages), status)


@bp.route("/logout")
@bp.route("/logout.html")
def logout():
    """
    Logout page.
    """
    if current_user.is_authenticated:
        logout_user()
    return "Logged out", 200


@bp.route("/me", methods=("GET", "POST"))
@bp.route("/me.html", methods=("GET", "POST"))
@login_required
def profile_me():
    """
    Profile page of the current user.

    It handle the logic for setting a new password and editting your bio.
    """
    messages = []
    status = HTTPStatus.OK

    if request.method == "POST":
        if "change_password" in request.form:
            if not (
                "old_password" in request.form
                and "new_password" in request.form
                and "new_password_repeat" in request.form
            ):
                messages.append(
                    {
                        "content": "Requête invalide, si le problème persiste contactez un administrateur...",
                        "is_error": True,
                    }
                )
                status = HTTPStatus.BAD_REQUEST
            else:
                if request.form["new_password"] != request.form["new_password_repeat"]:
                    messages.append(
                        {
                            "content": "Les mots de passes ne correspondent pas.",
                            "is_error": True,
                        }
                    )
                    status = HTTPStatus.BAD_REQUEST
                elif len(request.form["new_password"]) < 8:
                    messages.append(
                        {
                            "content": "Le mot de passe est trop court. Choisissez un mot de passe d'au moins 8 caractères.",
                            "is_error": True,
                        }
                    )
                    status = HTTPStatus.BAD_REQUEST
                elif len(request.form["new_password"]) > 50:
                    messages.append(
                        {
                            "content": "Le mot de passe est trop long, il doit faire moins de 50 caractères.",
                            "is_error": True,
                        }
                    )
                    status = HTTPStatus.BAD_REQUEST
                else:
                    cu = current_user.get_user()
                    if User.verify_password(cu, request.form["old_password"]):
                        cu.password = User.hash_password(request.form["new_password"])
                        cu.session_uid = uuid.uuid4()
                        try:
                            db.session.commit()
                        except:
                            messages.append(
                                {
                                    "content": "Une erreur serveur est survenue. Veuillez réessayer dans quelques instants...",
                                    "is_error": True,
                                }
                            )
                            status = HTTPStatus.INTERNAL_SERVER_ERROR
                        else:
                            messages.append(
                                {
                                    "content": "Mot de passe modifié avec succès ! Vous allez maintenant être déconnecté.",
                                    "is_error": False,
                                }
                            )
                            status = HTTPStatus.ACCEPTED
                    else:
                        messages.append(
                            {
                                "content": "Mot de passe faux, veuillez réessayer.",
                                "is_error": True,
                            }
                        )
                        status = HTTPStatus.FORBIDDEN
        elif "change_profile" in request.form:
            if "bio" in request.form:
                if len(request.form["bio"]) < 500:
                    cu = current_user.get_user()
                    cu.bio = request.form["bio"]
                    try:
                        db.session.commit()
                    except:
                        messages.append(
                            {
                                "content": "Une erreur serveur est survenue. Veuillez réessayer dans quelques instants...",
                                "is_error": True,
                            }
                        )
                        status = HTTPStatus.INTERNAL_SERVER_ERROR
                    else:
                        messages.append(
                            {
                                "content": "Votre profil a été modifié avec succès !",
                                "is_error": False,
                            }
                        )
                        status = HTTPStatus.ACCEPTED
                else:
                    messages.append(
                        {"content": "Votre bio est trop longue !", "is_error": False}
                    )
                    status = HTTPStatus.BAD_REQUEST
            else:
                messages.append({"content": "Argument invalide !", "is_error": False})
                status = HTTPStatus.BAD_REQUEST
        else:
            messages.append(
                {
                    "content": "Requête invalide, si le problème persiste contactez un administrateur...",
                    "is_error": True,
                }
            )
            status = HTTPStatus.BAD_REQUEST
    cu = current_user.get_user()
    return (
        render_template(
            "me.html",
            user={"display_name": cu.username, "bio": cu.bio},
            messages=messages,
        ),
        status,
    )
