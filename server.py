from flask import Flask, redirect, request, render_template, session
from jinja2 import StrictUndefined


app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload = True

# Required to use Flask sessions
app.secret_key = "DEV"

# The top melons at Ubermleon
MOST_LOVED_MELONS = {
    "cren": {
        "img": "http://www.rareseeds.com/assets/1/14/DimRegular/crenshaw.jpg",
        "name": "Crenshaw",
        "num_loves": 584,
    },
    "jubi": {
        "img": "http://www.rareseeds.com/assets/1/14/DimThumbnail/Jubilee-Watermelon-web.jpg",
        "name": "Jubilee Watermelon",
        "num_loves": 601,
    },
    "sugb": {
        "img": "http://www.rareseeds.com/assets/1/14/DimThumbnail/Sugar-Baby-Watermelon-web.jpg",
        "name": "Sugar Baby Watermelon",
        "num_loves": 587,
    },
    "texb": {
        "img": "http://www.rareseeds.com/assets/1/14/DimThumbnail/Texas-Golden-2-Watermelon-web.jpg",
        "name": "Texas Golden Watermelon",
        "num_loves": 598,
    },
}


@app.route('/top-melons')
def show_top_melons():
    # shows the top-melons template
    if "current_user" in session and session['current_user'] != "":
        return render_template("top-melons.html", melons = MOST_LOVED_MELONS)
    else:
        return redirect('/')


@app.route('/')
def homepage():
 
    if "current_user" in session and session['current_user'] != "":
        return redirect('/top-melons')
    else:
         # shows the homepage template
        return render_template("homepage.html")

@app.route('/get-name')
def get_name():
    # gets name from user
    username = request.args.get("name")
    session['current_user'] = username

    return redirect('/top-melons')

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        use_reloader=True,
        use_debugger=True,
    )
