from flask import Flask, jsonify, Response
import retrival
import json
import awsgi

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Hello from Flask on AWS Lambda!")

def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})

# Sample change
@app.get("/population/v1")
def population(startYear, endYear, suburb):
    suburb = retrival.population(startYear, endYear, suburb)
    suburb_info = json.loads(suburb)
    if suburb_info.has_key("error"):
        return Response(
            suburb_info["error"], 
            status=suburb_info["code"]
        )
    return suburb

@app.get("/populations/v1")
def populations(startYear, endYear, sortPopBy, suburb):
    suburbs = retrival.populations(startYear, endYear, sortPopBy, suburb)
    suburb_info = json.loads(suburbs)
    if suburb_info.has_key("error"):
        return Response(
            suburb_info["error"], 
            status=suburb_info["code"]
        )
    return suburbs

@app.get("/populations/all/v1")
def populationsAll(startYear, endYear, sortPopBy):
    suburb = retrival.populationAll(startYear, endYear, sortPopBy)
    if type(suburb) == dict:
        return Response(
            suburb["error"], 
            status=suburb["code"]
        )
    years = retrival.findYears(startYear, endYear)
    ret_suburb = []
    for i in range(len(suburb)):
        ret_suburb.append(jsonify(suburb=suburb[i][0], estimates=suburb[i][1:], years=years))
    return jsonify(suburbpopulationEstimates=ret_suburb)

def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})

if __name__ == "__main__":
    app.run()
