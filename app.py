from flask import Flask, jsonify, Response, request
import retrieval
import hts_retrieval
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
    # Handle population data retrieval for a single requested suburb.
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
    return suburb_info


@app.get("/population/v1")
def population_v1():
    """
    Provide the population estimate for the requested suburb in the
    requested time period.
    """
    return pop("v1")


@app.get("/population/v2")
def population_v2():
    """
    Provide the population estimate for the requested suburb in the
    requested time period. Include linear regression predictions from
    Tango API.
    """
    return pop("v2")


def pops(version):
    # Handle population data retrieval for a list of requested suburbs.
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
    return new_suburbs


@app.get("/populations/v1")
def populations_v1():
    """
    Provide the population estimate for the requested suburbs in the
    requested time period. 
    """
    return pops("v1")


@app.get("/populations/v2")
def populations_v2():
    """
    Provide the population estimate for the requested suburbs in the
    requested time period. Include linear regression predictions from
    Tango API.
    """
    return pops("v2")


@app.get("/populations/all/v1")
def populationsAll():
    """
    Provide the population estimate for all available NSW suburbs in the
    requested time period.
    """
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


@app.get("/travel/mode/suburbs/v1")
def travel_modes():
    """
    Return usage statistics about different modes of transport for each
    of the requested suburbs.
    """
    suburbsStr = request.args.get("suburbs")
    if suburbsStr == "" or suburbsStr is None:
        return Response("No suburbs entered", status=400)
    else:
        suburbs = suburbsStr[1:-1].split(",")
    suburbs_data = hts_retrieval.suburbs_travel_modes(suburbs)
    suburb_info = json.loads(suburbs_data)
    if "error" in suburb_info:
        return Response(suburb_info["error"], status=suburb_info["code"])
    return suburbs_data


@app.get("/travel/purpose/suburbs/v1")
def travel_purposes():
    """
    Return statistics about different purposes for travel for each
    of the requested suburbs.
    """
    suburbsStr = request.args.get("suburbs")
    if suburbsStr == "" or suburbsStr is None:
        return Response("No suburbs entered", status=400)
    else:
        suburbs = suburbsStr[1:-1].split(",")
    suburbs_data = hts_retrieval.suburbs_travel_purposes(suburbs)
    suburb_info = json.loads(suburbs_data)
    if "error" in suburb_info:
        return Response(suburb_info["error"], status=suburb_info["code"])
    return suburbs_data


@app.get("/travel/mode/top/v1")
def modes_top():
    """
    Return statistics for suburbs with the highest number of trips
    associated with the requested mode(s) of transport. Cap the number
    of returned suburbs at the requested limit.
    """
    modesStr = request.args.get("modes")
    limitStr = request.args.get("limit")
    if modesStr == "" or modesStr is None:
        return Response("Missing 'modes' parameter", status=400)
    else:
        modes = modesStr[1:-1].split(",")
    if limitStr is None:
        return Response("Missing 'limit' parameter", status=400)
    else:
        limit = int(limitStr)
    suburbs_data = hts_retrieval.modes_top_suburbs(modes, limit)
    suburbs_info = json.loads(suburbs_data)
    if "error" in suburbs_info:
        return Response(suburbs_info["error"], status=suburbs_info["code"])
    return suburbs_data


@app.get("/travel/purpose/top/v1")
def purposes_top():
    """
    Return statistics for suburbs with the highest number of trips
    associated with the requested travel purposes(s). Cap the number
    of returned suburbs at the requested limit.
    """
    purposesStr = request.args.get("purposes")
    limitStr = request.args.get("limit")
    if purposesStr == "" or purposesStr is None:
        return Response("Missing 'purposes' parameter", status=400)
    else:
        purposes = purposesStr[1:-1].split(",")
    if limitStr is None:
        return Response("Missing 'limit' parameter", status=400)
    else:
        limit = int(limitStr)
    suburbs_data = hts_retrieval.purposes_top_suburbs(purposes, limit)
    suburbs_info = json.loads(suburbs_data)
    if "error" in suburbs_info:
        return Response(suburbs_info["error"], status=suburbs_info["code"])
    return suburbs_data


if __name__ == "__main__":
    app.run()
