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

@app.get("/populations/v1")
def population(startYear, endYear, suburb, sortPopBy, sortByStart):
    suburb = retrival.populations(startYear, endYear, suburb, sortPopBy, sortByStart)
    if not suburb:
        return "", 400
    return jsonify(suburbPopulationEstimate=suburb)

@app.get("/populations/all/v1")
def population(startYear, endYear, sortPopBy, sortByStart):
    suburb = retrival.populationAll(startYear, endYear, sortPopBy, sortByStart)
    if not suburb:
        return "", 400
    return jsonify(suburbPopulationEstimate=suburb)