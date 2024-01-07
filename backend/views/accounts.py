from db import db
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from login import LoggedUser
from models.user import User
from sqlalchemy import select
from http import HTTPStatus
import uuid
from util.upload_helper import upload_formfile

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
        status = HTTPStatus.BAD_REQUEST
        # Get the username and password from the form
        username = request.form["username"]
        password = request.form["password"]
        # Validate the form
        (check_form, errors) = validate_register_form(request.form)
        messages.extend(map(lambda e: {"content": e, "is_error": True}, errors))

        if check_form:
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
                        username=username, display_name=username, password=User.hash_password(password)
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


def validate_register_form(form_data):
    """
    Validate the register form data.

    Args:
        form_data (dict): The form data.
    
    Returns:
        (bool, list[str]): A tuple containing the validity of the form and a list of messages to display.
    """
    messages = []
    if form_data["username"] is None or form_data["password"] is None or form_data["password_repeat"] is None:
        messages.append("Mot de passe ou nom d'utilisateur manquant.")
    elif form_data["password"] != form_data["password_repeat"]:
        messages.append("Les mots de passe ne correspondent pas.")
    elif len(form_data["password"]) < 8:
        messages.append("Le mot de passe est trop court. Choisissez un mot de passe d'au moins 8 caractères.")
    elif len(form_data["password"]) > 50:
        messages.append("Le mot de passe est trop long, il doit faire moins de 50 caractères.")
    elif len(form_data["username"]) < 3:
        messages.append("Le nom d'utilisateur est trop court. Choisissez un pseudonyme d'au moins 3 caractères.")
    elif len(form_data["username"]) > 50:
        messages.append("Le pseudonyme est trop long, il doit faire moins de 50 caractères.")
    elif not form_data["username"].isidentifier():
        messages.append("Le pseudonyme doit être un identifiant valide (composé uniquement de lettres, chiffres et underscore, dont le premier caractère est une lettre).")
    else:
        return (True, [])
    return (False, messages)


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
            (check_form, errors) = validate_password_reset_form(request.form)
            status = HTTPStatus.BAD_REQUEST
            messages.extend(map(lambda e: {"content": e, "is_error": True}, errors))
            if check_form:
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
            (check_form, errors) = validate_profile_edit_form(request.form)
            status = HTTPStatus.BAD_REQUEST
            messages.extend(map(lambda e: {"content": e, "is_error": True}, errors))
            if check_form:
                cu = current_user.get_user()
                if "avatar" in request.files:
                    (upload, errors) = upload_formfile(request.files["avatar"], current_user.user_uid, error_on_empty=False)
                    messages.extend(map(lambda e: {"content": e, "is_error": True}, errors))
                    if upload is not None:
                        cu.avatar_uid = upload.upload_uid
                else:
                    messages.append(
                        {
                            "content": "Aucun avatar fourni, l'avatar actuel ne sera pas modifié.",
                            "is_error": False,
                        }
                    )
                cu.display_name = request.form["display_name"]
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
                            "content": "Profil modifié avec succès !",
                            "is_error": False,
                        }
                    )
                    status = HTTPStatus.ACCEPTED
                
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
            user={"display_name": cu.display_name, "bio": cu.bio},
            messages=messages,
        ),
        status,
    )


def validate_password_reset_form(form_data):
    """
    Validate the password reset form data.

    Args:
        form_data (dict): The form data.
    
    Returns:
        (bool, list[str]): A tuple containing the validity of the form and a list of messages to display.
    """
    messages = []
    if form_data["new_password"] is None or form_data["new_password_repeat"] is None or form_data["old_password"] is None:
        messages.append("Mot de passe manquant.")
    elif form_data["new_password"] != form_data["new_password_repeat"]:
        messages.append("Les mots de passes ne correspondent pas.")
    elif len(form_data["new_password"]) < 8:
        messages.append("Le mot de passe est trop court. Choisissez un mot de passe d'au moins 8 caractères.")
    elif len(form_data["new_password"]) > 50:
        messages.append("Le mot de passe est trop long, il doit faire moins de 50 caractères.")
    else:
        return (True, [])
    return (False, messages)


def validate_profile_edit_form(form_data):
    """
    Validate the profile edit form data.

    Args:
        form_data (dict): The form data.

    Returns:
        (bool, list[str]): A tuple containing the validity of the form and a list of messages to display.
    """
    messages = []
    if form_data["display_name"] is None or form_data["bio"] is None:
        messages.append("Nom d'affichage ou biographie manquant.")
    elif len(form_data["display_name"]) > 50:
        messages.append("Le nom d'affichage est trop long, il doit faire moins de 50 caractères.")
    elif len(form_data["display_name"]) < 3:
        messages.append("Le nom d'affichage est trop court. Choisissez un nom d'affichage d'au moins 3 caractères.")
    elif not form_data["display_name"].isprintable():
        messages.append("Le nom d'affichage doit être affichable.")
    elif len(form_data["bio"]) > 500:
        messages.append("La biographie est trop longue, elle doit faire moins de 500 caractères.")
    else:
        return (True, [])
    return (False, messages)
