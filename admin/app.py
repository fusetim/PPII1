from flask import Flask, request
from flask import render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/test_post", methods=["GET", "POST"])
def test_post():
    if request.method == "GET":
        return "get"
    elif request.method == "POST":
        return request.form


@app.route("/admin", methods=["GET", "POST"])
def admin_search():
    return render_template("admin_search.html")


@app.route("/admin/add", methods=["GET"])
def admin_add():
    if request.method == "GET":
        return render_template("admin_add.html")


@app.route("/css_admin.css")
def CSS():
    return render_template("css_admin.css")
