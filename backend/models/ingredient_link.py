from db import db
from sqlalchemy import String, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid
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
        reference_quantity: The reference quantity (always in kg), that is used
            to compute the equivalent Co2 emission. If NULL, the reference
            quantity should be computed using the quantity_type (and use a
            conversion mechanism) and the quantity.
        display_name: The name of the ingredient as it should be displayed on
            the recipe page.
    """

    __tablename__ = "ingredient_links"
    link_uid: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recipe_uid: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("recipes.recipe_uid", ondelete="CASCADE")
    )
    ingredient_code: Mapped[str] = mapped_column(
        String(length=10), ForeignKey("ingredients.code")
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_type_uid: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("quantity_types.quantity_type_uid"),
        nullable=False,
    )
    reference_quantity: Mapped[float] = mapped_column(Float, nullable=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=True)

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient")
    quantity_type = relationship("QuantityType")

    def to_dict(self):
        rv = dict()
        rv["type"] = "ingredient_link"
        rv["link_uid"] = self.link_uid
        rv["recipe_uid"] = self.recipe_uid
        rv["ingredient_code"] = self.ingredient_code
        rv["quantity"] = self.quantity
        rv["quantity_type_uid"] = self.quantity_type_uid
        rv["reference_quantity"] = self.reference_quantity
        return rv
