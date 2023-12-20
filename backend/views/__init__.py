from flask import Blueprint
from . import accounts

# Creates the view "router" (aka blueprint in Flask)
views = Blueprint("views", __name__)
# Registers the account blueprint, with a prefix of /accounts.
views.register_blueprint(accounts.bp, url_prefix="/accounts")
