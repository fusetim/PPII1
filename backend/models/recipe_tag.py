from db import db
from sqlalchemy import String, Text, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid
import uuid


class RecipeTag(db.Model):
    """
    RecipeTag data model.
    Modelize a tag that can be associated to a recipe.

    Attributes:
        recipe_tag_uid (UUID): The recipe tag unique identifier.
        name (str): The recipe tag name.
        normalized_name (str): The normalized recipe tag name.
    """

    __tablename__ = "recipe_tags"
    recipe_tag_uid: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(length=30), nullable=False)
    normalized_name: Mapped[str] = mapped_column(Text, nullable=False)

    recipes: Mapped[list["Recipe"]] = relationship(
        secondary="recipe_tag_links", back_populates="tags"
    )

    def to_dict(self):
        rv = {
            "type": "recipe_tag",
            "recipe_tag_uid": self.recipe_tag_uid,
            "name": self.name,
            "normalized_name": self.normalized_name,
        }
        return rv


# Association table between recipes and tags
recipe_tag_association = Table(
    "recipe_tag_links",
    db.metadata,
    Column(
        "recipe_uid",
        Uuid(as_uuid=True),
        ForeignKey("recipes.recipe_uid", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "recipe_tag_uid",
        Uuid(as_uuid=True),
        ForeignKey("recipe_tags.recipe_tag_uid", ondelete="CASCADE"),
        primary_key=True,
    ),
)
