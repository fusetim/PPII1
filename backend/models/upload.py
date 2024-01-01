from db import db
from sqlalchemy import String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.types import Uuid
import datetime

class Upload(db.Model):
    """
    User Upload data model.

    Attributes:
        upload_uid (UUID): The upload unique identifier.
        author_uid (UUID): The user unique identifier.
        original_filename (String): The original filename (and extension).
        content_id (String): The content id of the upload.
        extension (String): The extension of the upload.
        upload_date (DateTime): The date of the upload.
        deletion_date (DateTime): The date of the upload deletion. If NULL the upload is active.
    """

    __tablename__ = "user_uploads"
    upload_uid : Mapped[Uuid] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_uid : Mapped[Uuid] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_uid", ondelete="CASCADE"), nullable=False)
    original_filename : Mapped[str] = mapped_column(Text, nullable=True)
    content_id : Mapped[str] = mapped_column(Text, nullable=False)
    extension : Mapped[str] = mapped_column(String(length=10), nullable=True)
    upload_date : Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    deletion_date : Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    author = relationship("User", back_populates="uploads")