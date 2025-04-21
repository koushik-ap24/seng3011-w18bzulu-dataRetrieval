from flask import Flask, jsonify, Response, request
import retrieval
import hts_retrieval
import json
import awsgi

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(message="Hello from AWS Lambda!")


def lambda_handler(event, context):
    if 'httpMethod' not in event:
        if 'requestContext' in event and 'http' in event['requestContext']:
            # Convert API Gateway v2 format to the format awsgi expects
            return awsgi.response(app, convert_v2_to_v1(event), context, base64_content_types={"image/png"})
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'This endpoint should be accessed through API Gateway'})
        }
    return awsgi.response(app, event, context, base64_content_types={"image/png"})

def convert_v2_to_v1(event):
    v1_event = {
        'httpMethod': event['requestContext']['http']['method'],
        'path': event['requestContext']['http']['path'],
        'headers': event['headers'],
        'queryStringParameters': event.get('queryStringParameters', {}),
        'body': event.get('body', ''),
        'isBase64Encoded': event.get('isBase64Encoded', False)
    }
    return v1_event


# Sample change
@app.get("/population/v1")
def population():
    suburb = request.args.get("suburb")
    startYear = int(request.args.get("startYear"))
    endYear = int(request.args.get("endYear"))
    suburb = retrieval.population(startYear, endYear, suburb)
    suburb_info = json.loads(suburb)
    if "error" in suburb_info:
        return Response(suburb_info["error"], status=suburb_info["code"])
    return suburb


@app.get("/populations/v1")
def populations():
    suburbs = request.args.get("suburbs")[1:-1].split(",")
    startYear = int(request.args.get("startYear"))
    endYear = int(request.args.get("endYear"))
    sortPopBy = request.args.get("sortPopBy")
    suburbs = retrieval.populations(startYear, endYear, sortPopBy, suburbs)
    suburb_info = json.loads(suburbs)
    if "error" in suburb_info:
        return Response(suburb_info["error"], status=suburb_info["code"])
    return suburbs

@app.get("/travel/mode/v1")
def travel_modes():
    suburbs = request.args.get("suburbs")[1:-1].split(",")
    suburbs_data = hts_retrieval.suburbs_travel_modes(suburbs)
    suburb_info = json.loads(suburbs)
    if "error" in suburb_info:
        return Response(suburb_info["error"], status=suburb_info["code"])
    return suburbs_data

# @app.get("/populations/all/v1")
# def populationsAll(startYear, endYear, sortPopBy):
#     suburb = retrieval.populationAll(startYear, endYear, sortPopBy)
#     if isinstance(suburb, dict):
#         return Response(suburb["error"], status=suburb["code"])
#     years = retrieval.findYears(startYear, endYear)
#     ret_suburb = []
#     for i in range(len(suburb)):
#         ret_suburb.append(
#             jsonify(suburb=suburb[i][0], estimates=suburb[i][1:], years=years)
#         )
#     return jsonify(suburbpopulationEstimates=ret_suburb)


if __name__ == "__main__":
    app.run()
