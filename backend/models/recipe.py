from db import db
from sqlalchemy import String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Recipe(db.Model):
    """
    Recipe data model.

    Attributes:
        code: The ingredient unique identifier.
        name: The ingredient name.
        co2: The equivalent Co2 emission per kilogram.
    """
    __tablename__ = "recipes"
    recipe_uid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    short_description : Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(length = 30))
    author: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)


    def to_dict(self):
        rv = dict()
        rv['type'] = 'recipe'
        rv['recipe_uid'] = self.recipe_uid 
        rv['name'] = self.name 
        rv['short_description'] = self.short_description
        rv['description'] = self.description
        rv['type'] = self.type
        rv['author'] = self.author
        return rv

