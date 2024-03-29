from flask import Blueprint
from . import ingredients, recipes, uploads, admin

# Creates the API "router" (aka blueprint in Flask)
api = Blueprint("api", __name__)
# Registers the ingredients blueprint, with a prefix of /ingredients.
# All requests to "/ingredients" will be redirected to the ingredients blueprint.
api.register_blueprint(ingredients.bp, url_prefix="/ingredients")
# same thing for recipes, uploads, admin etc.
api.register_blueprint(recipes.bp, url_prefix="/recipes")
api.register_blueprint(admin.bp, url_prefix="/admin")
api.register_blueprint(uploads.bp, url_prefix="/uploads")

# This route handles the root of the API router (in our case, "[root]/api")
@api.route("/")
def api_hello():
    return {
        "version": "1",
        "message": "HELO",
    }