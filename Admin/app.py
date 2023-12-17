from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/admin")
def admin_search():
    return render_template("admin_search.html")
"""
@app.route("/admin", Methods=['GET'])
def admin_search_get():
    return render_template("admin_search.html")"""

@app.route("/admin/add")
def admin_add():
    return render_template("admin_add.html")

@app.route("/admin/add", methods=['GET'])
def admin_add_get():
    return render_template("admin_add.html")

@app.route("/css_admin.css")
def CSS():
    return render_template("css_admin.css")