from flask import Flask, jsonify, Response, request
import retrieval
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
def pop(version):
    suburb = request.args.get("suburb")
    startYear = int(request.args.get("startYear"))
    endYear = int(request.args.get("endYear"))
    suburb = retrieval.population(startYear, endYear, suburb, version=version)
    suburb_info = json.loads(suburb)
    if "error" in suburb_info:
        return Response(suburb_info["error"], status=suburb_info["code"])
    return suburb

@app.get("/population/v1")
def population():
    pop("v1")

@app.get("/population/v2")
def population():
    pop("v2")

def pops(version):
    suburbs = request.args.get("suburbs")[1:-1].split(",")
    startYear = int(request.args.get("startYear"))
    endYear = int(request.args.get("endYear"))
    sortPopBy = request.args.get("sortPopBy")
    
    suburbs = retrieval.populations(startYear, endYear, sortPopBy, suburbs, version)
    suburb_info = json.loads(suburbs)
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
def populationsAll(startYear, endYear, sortPopBy):
    suburb = retrieval.populationAll(startYear, endYear, sortPopBy)
    suburb_info = json.loads(suburb)
    if "error" in suburb_info:
        return Response(suburb["error"], status=suburb["code"])
    return suburb


if __name__ == "__main__":
    app.run()
