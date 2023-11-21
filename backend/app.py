from api import api
from flask import Flask

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")


# By default, Flask already routes the static directory :)
# No need for a dedicated route.


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"