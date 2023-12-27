from flask import Blueprint, jsonify
from sqlalchemy import select, text
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.ingredient_link import IngredientLink
from models.quantity_type import QuantityType
from db import db

from recipes import RecipeNotFound, not_found

# Creates the recipes "router" (aka blueprint in Flask)
bp = Blueprint("recipes", __name__)


@bp.route("/delete/<uuid:id>", methods=["DELETE"])
def delete_recipe(id):
    """
    Delete recipe with uuid = id. Associated ingredient
    links will be deleted too.
    """
    recipe_to_delete = Recipe.query.get(id)
    if recipe is None:
        raise RecipeNotFound(context="Not in DB.", payload={"code": id})

    db.session.delete(recipe_to_delete)
    db.session.commit()
