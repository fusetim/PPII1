from db import db
from sqlalchemy import String, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .recipe import Recipe
from .ingredient import Ingredient
import uuid

class IngredientLink(db.Model):
    """
    IngredientLink data model.
    It is a symbolic reference to an ingredient in a recipe.
    It contains the quantity of the ingredient.

    Attributes:
        link_uid: The IngredientLink unique identifier.
        recipe_uid: The recipe unique identifier.
        ingredient_code: The ingredient identifier.
        quantity: The quantity of the ingredient.
        quantity_type_uid: The UUID of the type of quantity (mass, volume, etc.)
        reference_quantity: The reference quantity (always in kg), that is used to compute the
        equivalent Co2 emission. If NULL, the reference quantity should be computed using the
        quantity_type (and use a conversion mechanism) and the quantity.
    """
    __tablename__ = "ingredient_links"
    link_uid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_uid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recipes.recipe_uid"))
    ingredient_code: Mapped[str] = mapped_column(String(length=10), ForeignKey("ingredients.code"))
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_type_uid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    reference_quantity: Mapped[float] = mapped_column(Float, nullable=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=True)

    recipe = relationship("Recipe")
    ingredient = relationship("Ingredient")
