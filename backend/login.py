from flask import redirect, url_for, request, abort
from http import HTTPStatus
from flask_login import LoginManager, UserMixin
from models.user import User
from sqlalchemy import select
from uuid import UUID
from db import db

login_manager = LoginManager()
login_manager.login_view = "views.accounts.login"

@login_manager.unauthorized_handler
def unauthorized():
    if request.blueprint == 'api':
        abort(HTTPStatus.UNAUTHORIZED)
    return redirect(url_for('views.accounts.login', next=request.url))


@login_manager.user_loader
def load_user(session_uid):
    """
    Internal function used by the login manager to load a user.

    Args:
        session_uid (UUID): The session unique identifier.
    """
    return LoggedUser(session_uid=UUID(session_uid))


class LoggedUser(UserMixin):
    """
    Representing a logged user.

    Attributes:
        user_uid (UUID): The user unique identifier, identifier of the DB user.
        session_uid (UUID): The session unique identifier.
        is_anonymous (bool): True if the user is anonymous, False otherwise.
        is_active (bool): True if the user is active, False otherwise.
        is_authenticated (bool): True if the user is authenticated, False otherwise.
    """

    is_anonymous = True
    is_active = False
    is_authenticated = False
    session_uid = None
    user_uid = None

    def __init__(self, user_uid=None, session_uid=None):
        """
        Initialize a logged user.

        Args:
            user_uid (UUID): The user unique identifier.
            session_uid (UUID): The session unique identifier.

            if both are None, the user is anonymous.
        """
        user = None
        if user_uid is not None:
            user = db.session.get(User, self.user_uid)
        elif session_uid is not None:
            user = (
                db.session.execute(select(User).filter(User.session_uid == session_uid))
                .scalars()
                .first()
            )
        if user is not None:
            self.is_active = user.deletion_date is None
            self.is_authenticated = True
            self.is_anonymous = False
            self.user_uid = user.user_uid
            self.session_uid = user.session_uid
        else:
            self.is_anonymous = True

    def get_id(self):
        if self.is_anonymous:
            return None
        return str(self.session_uid)

    def get_user(self):
        """
        Get the user object from the database.

        Returns:
            User: The user object, if it exists, None otherwise.
        """
        if self.is_anonymous:
            return None
        return db.session.get(User, self.user_uid)
