from db import db
from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
import datetime
from argon2 import PasswordHasher

class User(db.Model):
    """
    User data model.

    Attributes:
        user_uid (UUID): The user unique identifier.
        username (String): The user name.
        password (String): The user hashed password (argon2id hash).
        bio (String): The user bio.
        creation_date (DateTime): The date of the account creation.
        deletion_date (DateTime): The date of the account deletion. If NULL the account is active.
    """
    __tablename__ = "users"
    user_uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(length=50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(length=256), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    creation_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    deletion_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    

    recipes : Mapped[list["Recipe"]] = relationship("Recipe", back_populates="author_account", cascade="all, delete", passive_deletes=True)


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


    def verify_password(self, password: str):
        """
        Verify a password against the user's password.
        If the password is correct, it might rehash it if the
        hash parameters changed.

        Args:
            password (str): The password to verify.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        ph = PasswordHasher()
        try:
            ph.verify(self.password, password)
            if ph.check_needs_rehash(self.password):
                self.password = ph.hash(password)
                db.session.commit()
            return True
        except:
            return False
