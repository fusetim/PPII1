from db import db
from sqlalchemy import String, Float, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Recipe(db.Model):
    """
    Recipe data model.

    Attributes:
        recipe_uid: The recipe unique identifier.
        name: The recipe name.
        normalized_name: The normalized recipe name.
        short_description: A short description of the recipe, displayed when browsing recipes.
        description: A longer description of the recipe, displayed when viewing the recipe. It must include
            the actual recipe instructions.
        type: The type of recipe. This is a string that can be used to categorize recipes.
        author: The author of the recipe. This is a UUID that can be used to link to the author's profile.
        duration: The preparation time required by this recipe in minutes.
        illustration: A URI to an image that illustrates the recipe. The format of this one is `/assets/filename.ext`.
    """

    __tablename__ = "recipes"
    recipe_uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_name: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(length=30))
    author: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_uid", ondelete="CASCADE"),
        nullable=True,
    )
    duration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    illustration: Mapped[str] = mapped_column(Text, nullable=False)

    ingredients = relationship("IngredientLink", back_populates="recipe")
    tags: Mapped[list["RecipeTag"]] = relationship(
        secondary="recipe_tag_links", back_populates="recipes"
    )
    author_account = relationship("User", back_populates="recipes")

    def to_dict(self):
        rv = dict()
        rv["type"] = "recipe"
        rv["recipe_uid"] = self.recipe_uid
        rv["name"] = self.name
        rv["short_description"] = self.short_description
        rv["description"] = self.description
        rv["type"] = self.type
        rv["author"] = self.author
        rv["duration"] = self.duration
        rv["illustration"] = self.illustration
        return rv
