from flask import Blueprint
from . import recipes

# Creates the subrouter for the admin API routes
bp = Blueprint("admin", __name__)

# Registers the subblueprints
bp.register_blueprint(recipes.bp, url_prefix="/recipes")