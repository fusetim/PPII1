from db import db
from sqlalchemy import String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.types import Uuid
import datetime
from argon2 import PasswordHasher


class User(db.Model):
    """
    User data model.

    Attributes:
        user_uid (UUID): The user unique identifier.
        username (String): The user name.
        display_name (String): The user display name.
        password (String): The user hashed password (argon2id hash).
        bio (String): The user bio.
        creation_date (DateTime): The date of the account creation.
        deletion_date (DateTime): The date of the account deletion. If NULL the account is active.
        session_uid (UUID): The session id of the user. It is used to identify the user's session, and
            allows to log in automatically and log out from every device.
        avatar_uid (UUID): The upload unique identifier to use as an avatar.
    """

    __tablename__ = "users"
    user_uid: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(length=50), nullable=False, unique=True
    )
    display_name: Mapped[str] = mapped_column(
        String(length=50), nullable=True
    )
    password: Mapped[str] = mapped_column(String(length=256), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    creation_date: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    deletion_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    session_uid: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), unique=True, default=uuid.uuid4
    )
    avatar_uid: Mapped[Uuid] = mapped_column(Uuid(as_uuid=True), nullable=True)

    recipes: Mapped[list["Recipe"]] = relationship(
        "Recipe",
        back_populates="author_account",
        cascade="all, delete",
        passive_deletes=True,
    )

    uploads: Mapped[list["Upload"]] = relationship(
        "Upload",
        back_populates="author",
        cascade="all, delete",
        passive_deletes=True
    )
    def hash_password(password: str):
        """
        Hash a password using argon2id.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        ph = PasswordHasher()
        return ph.hash(password)

    def verify_password(user, password: str):
        """
        Verify a password against the user's password.
        If the password is correct, it might rehash it if the
        hash parameters changed.

        Args:
            user (User): The user to verify the password against.
            password (str): The password to verify.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        ph = PasswordHasher()
        try:
            ph.verify(user.password, password)
            if ph.check_needs_rehash(user.password):
                user.password = ph.hash(password)
                db.session.commit()
            return True
        except:
            return False
