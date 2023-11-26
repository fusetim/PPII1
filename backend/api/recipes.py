from flask import Blueprint, jsonify
from sqlalchemy import select
from models.recipe import Recipe
from db import db
from search_table import get_recipe_table, normalize_str

# Creates the recipes "router" (aka blueprint in Flask)
bp = Blueprint("recipes", __name__)


@bp.route("/search/<string:query>")
def search_recipe(query):
    """Search for a recipe based on a query string."""
    table = get_recipe_table()
    normalized_query = normalize_str(query)
    uids = table.get(normalized_query, 10)
    results = []
    uid_set = set()
    for recipe_uid in uids:
        recipe = db.session.get(Recipe, recipe_uid)
        if recipe is not None:
            data = recipe.to_dict()
            data["origin"] = "lsh-search"
            results.append(data)
            uid_set.add(recipe_uid)
    for recipe in (
        db.session.execute(
            select(Recipe)
            .where(Recipe.normalized_name.like(f"%{normalized_query}%"))
            .limit(min(10, 10 - len(results)))
        )
        .scalars()
        .all()
    ):
        if recipe.recipe_uid not in uid_set:
            data = recipe.to_dict()
            data["origin"] = "db-search"
            results.append(data)
            uid_set.add(recipe.recipe_uid)
    return jsonify(results)
