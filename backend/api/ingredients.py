from flask import Blueprint, request, jsonify

# Creates the ingredients "router" (aka blueprint in Flask)
bp = Blueprint("ingredients", __name__)


# Probably the most useful route of this router.
# It handles the lookup of an ingredient based on its unique identifier (code).
@bp.route("/<string:code>")
def get_ingredient(code):
    """Get an ingredient data from its code."""
    # Waiting for DB
    # Note: Tests are not implemented yet, because this solution is obviously temporary.
    if code == "tomate":
        return {
            "code": code,
            "name": "Tomate",
            "carbon_equivalent": 0.5,
        }
    elif code == "pomme-de-terre":
        return {
            "code": code,
            "name": "Pomme de Terre",
            "carbon_equivalent": 0.3,
        }
    else:
        # When all cases are exhausted, raise the NotFound exception, defined later.
        raise IngredientNotFound("Not in DB")


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
        rv['reason'] = "Ingredient not found, it might not be in the database, or been deleted."
        rv['context'] = self.context
        return rv


@bp.errorhandler(IngredientNotFound)
def not_found(e):
    """Route handling the IngredientNotFound exception."""
    return jsonify(e.to_dict()), e.status_code
