from flask import Flask, request, render_template, redirect, url_for

from walkabilityApp.processor.Processor import Processor

app = Flask(__name__, template_folder="ui/templates")

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
        result = obtain_result(coordinates)
    except:
        result = "Invalid coordinates. Try again by returning to the home page."
    return render_template("result.html", result=result, coordinates = coordinates)

def obtain_result(coordinates):
    processor = Processor(gps_coordinates=coordinates)
    return processor.process_location()

app.run(host="0.0.0.0", port=80)