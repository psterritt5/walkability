from flask import Flask, request, render_template, redirect, url_for
from main import run

app = Flask(__name__)

@app.route('/',methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        coordinates = request.form["coordinates"]
        return redirect(url_for('result', name=coordinates))
    return render_template('index.html')

@app.route("/result", methods=['GET', 'POST'])
def result():
    coordinates = request.form.get('coordinates')
    try:
        result = run(coordinates)
    except:
        result = "Invalid coordinates. Try again by returning to the home page."
    return render_template("result.html", result=result, coordinates = coordinates)

app.run(host="0.0.0.0", port=80)