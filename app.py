from flask import Flask, jsonify, Response
import retrival

app = Flask(__name__)

# @app.route("/")
# def home():
#     return jsonify(message="Hello from Flask on AWS Lambda!")

# Sample change
@app.get("/population/v1")
def population(startYear, endYear, suburb):
    suburb = retrival.population(startYear, endYear, suburb)
    if type(suburb) == dict:
        return Response(
            suburb["Error"], 
            status=suburb["Code"]
        )
    return jsonify(suburbPopulationEstimate=suburb[1:], years=retrival.findYears(startYear, endYear))

@app.get("/populations/v1")
def populations(startYear, endYear, suburb, sortPopBy):
    suburb = retrival.populations(startYear, endYear, suburb, sortPopBy)
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