from flask import render_template
from app.main import bp

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/gameView")
def gameView():
    return render_template("gameView.html")

@bp.route("/typing")
def typing():
    return render_template("typing.html")

@bp.route("/speed")
def speed():
    return render_template("speed.html")

@bp.route("/dexterity")
def dexterity():
    return render_template("dexterity.html")

@bp.route("/precision")
def precision():
    return render_template("precision.html") 