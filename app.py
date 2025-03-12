from flask import Flask, jsonify, Response
import retrival

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Hello from Flask on AWS Lambda!")

# Sample change
@app.get("/population/v1")
def population(startYear, endYear, suburb):
    suburb = retrival.population(startYear, endYear, suburb)
    if type(suburb) == dict:
        return Response(
            suburb["Error"], 
            status=suburb["Code"]
        )
    return jsonify(suburbPopulationEstimate=suburb[1:])

@app.get("/populations/v1")
def populations(startYear, endYear, suburb, sortPopBy, sortByStart):
    suburb = retrival.populations(startYear, endYear, suburb, sortPopBy, sortByStart)
    if type(suburb) == dict:
        return Response(
            suburb["Error"], 
            status=suburb["Code"]
        )
    ret_suburb = [] 
    for i in range(len(suburb)):
        ret_suburb.append(jsonify(suburb=suburb[i][0], suburbPopulationEstimate=suburb[i][1:]))
    return jsonify(suburbpopulationEstimate=ret_suburb)

@app.get("/populations/all/v1")
def populationsAll(startYear, endYear, sortPopBy, sortByStart):
    suburb = retrival.populationAll(startYear, endYear, sortPopBy, sortByStart)
    if type(suburb) == dict:
        return Response(
            suburb["Error"], 
            status=suburb["Code"]
        )
    ret_suburb = []
    for i in range(len(suburb)):
        ret_suburb.append(jsonify(suburb=suburb[i][0], populationEstimate=suburb[i][1:]))
    return jsonify(suburbpopulationEstimate=ret_suburb)