from flask_login import LoginManager, UserMixin
from models.user import User
from db import db

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_uid):
    """
    Internal function used by the login manager to load a user.

    Args:
        user_uid (UUID): The user unique identifier.
    """
    return LoggedUser(user_uid)

class LoggedUser(UserMixin):
    """
    Representing a logged user.

    Attributes:
        user_uid (UUID): The user unique identifier.
        is_anonymous (bool): True if the user is anonymous, False otherwise.
        is_active (bool): True if the user is active, False otherwise.
        is_authenticated (bool): True if the user is authenticated, False otherwise.
    """
    is_anonymous = False
    is_active = False
    is_authenticated = False

    def __init__(self, user_uid):
        """
        Initialize a logged user.

        Args:
            user_uid (UUID): The user unique identifier. If None, the 
                user is anonymous.
        """
        self.user_uid = user_uid
        user = db.session.get(User, self.user_uid)
        if user is not None:
            self.is_active = user.deletion_date is None
            self.is_authenticated = True
        else:
            self.is_anonymous = True

    def get_id(self):
        if self.is_anonymous:
            return None
        return str(self.user_uid)

    def get_user(self):
        """
        Get the user object from the database.

        Returns:
            User: The user object, if it exists, None otherwise.
        """
        if self.is_anonymous:
            return None
        return db.session.get(User, self.user_uid)