from flask import Flask, jsonify
import retrival

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Hello from Flask on AWS Lambda!")

# Sample change
@app.get("/population/v1")
def population(startYear, endYear, suburb):
    suburb = retrival.population(startYear, endYear, suburb)
    if not suburb:
        return "", 400
    return jsonify(suburbPopulationEstimate=suburb)
