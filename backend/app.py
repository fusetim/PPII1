from api import api
from flask import Flask
import tomllib
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import models
from flask import g

# Entrypoint for the Flask app.
app = Flask(__name__)
# Register the `/api` routes
app.register_blueprint(api, url_prefix="/api")
# Load the config file
app.config.from_file("config.toml", load=tomllib.load, text=False)
# Initialize the database
db = SQLAlchemy(app)
# Initialize the migration engine (for database migrations)
migrate = Migrate(app, db)

with app.app_context():
    g.db = db
    g.models = models

# By default, Flask already routes the static directory :)
# No need for a dedicated route.


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
