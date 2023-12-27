from flask import Blueprint, jsonify
from sqlalchemy import select
from models.ingredient import Ingredient
from db import db
from search_table import get_ingredient_table
from lsh import normalize_str

# Creates the ingredients "router" (aka blueprint in Flask)
bp = Blueprint("ingredients", __name__)


@bp.route("/")
def all_ingredients():
    """
    test route: return all ingredients (json)
    """
    ingredients = Ingredient.query.all()
    ing_list = [ing.to_dict() for ing in ingredients]
    return jsonify(ing_list)


# Probably the most useful route of this router.
# It handles the lookup of an ingredient based on its unique identifier (code).
@bp.route("/<string:code>")
def get_ingredient(code):
    """Get an ingredient data from its code."""
    ingredient = db.session.get(Ingredient, code)
    if ingredient is None:
        raise IngredientNotFound(context="Not in DB.", payload={"code": code})
    return jsonify(ingredient.to_dict())


@bp.route("/search/<string:query>")
def search_ingredient(query):
    """Search for an ingredient based on a query string."""
    table = get_ingredient_table()
    normalized_query = normalize_str(query)
    codes = table.get(normalized_query, 10)
    results = []
    code_set = set()
    for code in codes:
        ingredient = db.session.get(Ingredient, code)
        if ingredient is not None:
            data = ingredient.to_dict()
            data["origin"] = "lsh-search"
            results.append(data)
            code_set.add(code)
    for ingredient in (
        db.session.execute(
            select(Ingredient)
            .where(Ingredient.normalized_name.like(f"%{normalized_query}%"))
            .limit(min(10, 10 - len(results)))
        )
        .scalars()
        .all()
    ):
        if ingredient.code not in code_set:
            data = ingredient.to_dict()
            data["origin"] = "db-search"
            results.append(data)
            code_set.add(ingredient.code)
    return jsonify(results)


class IngredientNotFound(Exception):
    """
    Exception raised when an ingredient is not found in the database.
    """

    status_code = 404

    def __init__(self, context, status_code=None, payload=None):
        super().__init__()
        self.context = context
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv[
            "reason"
        ] = "Ingredient not found, it might not be in the database, or been deleted."
        rv["context"] = self.context
        return rv


@bp.errorhandler(IngredientNotFound)
def not_found(e):
    """Route handling the IngredientNotFound exception."""
    return jsonify(e.to_dict()), e.status_code
