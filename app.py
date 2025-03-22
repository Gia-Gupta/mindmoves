from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/gameView")
def gameView():
    return render_template("gameView.html")

@app.route("/typing")
def typing():
    return render_template("typing.html")

@app.route("/speed")
def speed():
    return render_template("speed.html")

@app.route("/dexterity")
def dexterity():
    return render_template("dexterity.html")

@app.route("/precision")
def precision():
    return render_template("precision.html")

if __name__ == "__main__":
    app.run(debug=True)

