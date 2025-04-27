from flask import Flask, jsonify, Response, request
import retrieval
import json
import awsgi

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(message="Hello from AWS Lambda (dev)!")


def lambda_handler(event, context):
    if "httpMethod" not in event:
        if "requestContext" in event and "http" in event["requestContext"]:
            # Convert API Gateway v2 format to the format awsgi expects
            return awsgi.response(
                app,
                convert_v2_to_v1(event),
                context,
                base64_content_types={"image/png"},
            )
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "This endpoint should be accessed through API Gateway"}
            ),
        }
    return awsgi.response(app, event, context, base64_content_types={"image/png"})


def convert_v2_to_v1(event):
    v1_event = {
        "httpMethod": event["requestContext"]["http"]["method"],
        "path": event["requestContext"]["http"]["path"],
        "headers": event["headers"],
        "queryStringParameters": event.get("queryStringParameters", {}),
        "body": event.get("body", ""),
        "isBase64Encoded": event.get("isBase64Encoded", False),
    }
    return v1_event


# Sample change
def pop(version):
    suburb = request.args.get("suburb")
    startYearStr = request.args.get("startYear")
    endYearStr = request.args.get("endYear")
    if startYearStr and endYearStr:
        startYear = int(startYearStr)
        endYear = int(endYearStr)
    else:
        return Response("Invalid start or end year", status=400)
    ret_suburb = retrieval.population(startYear, endYear, suburb, version=version)
    suburb_info = json.loads(ret_suburb)
    if "error" in suburb_info:
        return Response(suburb_info["error"], status=suburb_info["code"])
    return suburb
    

@app.get("/population/v1")
def population_v1():
    return pop("v1")


@app.get("/population/v2")
def population_v2():
    return pop("v2")


def pops(version):
    suburbsStr = request.args.get("suburbs")
    if suburbsStr == "" or suburbsStr is None:
        return Response("No suburb found", status=400)
    elif len(suburbsStr) > 1:
        suburbs = suburbsStr[1:-1].split(",")
    startYearStr = request.args.get("startYear")
    endYearStr = request.args.get("endYear")
    if startYearStr and endYearStr:
        startYear = int(startYearStr)
        endYear = int(endYearStr)
    else:
        return Response("Invalid start or end year", status=400)
    sortPopBy = request.args.get("sortPopBy")

    new_suburbs = retrieval.populations(startYear, endYear, sortPopBy, suburbs, version)
    suburb_info = json.loads(new_suburbs)
    if "error" in suburb_info:
        return Response(suburb_info["error"], status=suburb_info["code"])
    return suburbs


@app.get("/populations/v1")
def populations_v1():
    return pops("v1")


@app.get("/populations/v2")
def populations_v2():
    return pops("v2")


@app.get("/populations/all/v1")
def populationsAll():
    startYearStr = request.args.get("startYear")
    endYearStr = request.args.get("endYear")
    if startYearStr and endYearStr:
        startYear = int(startYearStr)
        endYear = int(endYearStr)
    else:
        return Response("Invalid start or end year", status=400)
    suburb = retrieval.populationAll(startYear, endYear)
    suburb_info = json.loads(suburb)
    if "error" in suburb_info:
        return Response(suburb["error"], status=suburb["code"])
    return suburb


if __name__ == "__main__":
    app.run()
