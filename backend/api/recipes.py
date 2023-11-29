from flask import Blueprint, jsonify
from sqlalchemy import select
from models.recipe import Recipe
from db import db
from search_table import get_recipe_table


# Creates the recipes "router" (aka blueprint in Flask)
bp = Blueprint("recipes", __name__)


@bp.route("/recipe_info/<uuid:id>")
def recipe_info(id):
    """Return the name, the short description and the description of
    the recipe with UUID = id."""
    recipe = db.session.get(Recipe, id)
    if recipe is None:
        # raise IngredientNotFound(context="Not in DB.", payload={"code": code})
        pass
    return jsonify(
        name=recipe.name,
        short_description=recipe.short_description,
        description=recipe.description,
    )
