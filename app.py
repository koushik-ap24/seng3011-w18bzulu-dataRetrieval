from flask import Flask, jsonify, Response
import retrival
import json

app = Flask(__name__)

# @app.route("/")
# def home():
#     return jsonify(message="Hello from Flask on AWS Lambda!")

# Sample change
@app.get("/population/v1")
def population(startYear, endYear, suburb):
    suburb = retrival.population(startYear, endYear, suburb)
    suburb_info = json.loads(suburb)
    if suburb_info["Error"]:
        return Response(
            suburb_info["Error"], 
            status=suburb_info["Code"]
        )
    return suburb

@app.get("/populations/v1")
def populations(startYear, endYear, sortPopBy, suburb):
    suburbs = retrival.populations(startYear, endYear, sortPopBy, suburb)
    suburb_info = json.loads(suburbs)
    if suburb_info["Error"]:
        return Response(
            suburb_info["Error"], 
            status=suburb_info["Code"]
        )
    return suburbs

@app.get("/populations/all/v1")
def populationsAll(startYear, endYear, sortPopBy):
    suburb = retrival.populationAll(startYear, endYear, sortPopBy)
    if type(suburb) == dict:
        return Response(
            suburb["Error"], 
            status=suburb["Code"]
        )
    years = retrival.findYears(startYear, endYear)
    ret_suburb = []
    for i in range(len(suburb)):
        ret_suburb.append(jsonify(suburb=suburb[i][0], estimate=suburb[i][1:], years=years))
    return jsonify(suburbpopulationEstimate=ret_suburb)