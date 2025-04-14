from flask import Flask, jsonify, Response, request
import retrieval
import json
import awsgi
import boto3
from flask_cors import CORS
import os

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


@app.get("/populations/all/v1")
def populationsAll(startYear, endYear, sortPopBy):
    suburb = retrieval.populationAll(startYear, endYear, sortPopBy)
    suburb_info = json.loads(suburb)
    if "error" in suburb_info:
        return Response(suburb["error"], status=suburb["code"])
    return suburb

# AWS Cognito config
USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID', 'your-user-pool-id')
CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID', 'your-client-id')
REGION = os.environ.get('AWS_REGION', 'your-region')

cognito = boto3.client('cognito-idp', region_name=REGION)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    try:
        cognito.sign_up(
            ClientId=CLIENT_ID,
            Username=data['username'],
            Password=data['password'],
            UserAttributes=[
                {'Name': 'email', 'Value': data['email']}
            ]
        )
        return jsonify({'message': 'User registered. Please check your email to confirm.', "help": data}), 200
    except cognito.exceptions.UsernameExistsException:
        return jsonify({'error': 'User already exists.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    try:
        cognito.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=data['username'],
            ConfirmationCode=data['code']
        )
        return jsonify({'message': 'User confirmed.'}), 200
    except cognito.exceptions.CodeMismatchException:
        return jsonify({'error': 'Invalid code.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        response = cognito.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': data['username'],
                'PASSWORD': data['password']
            }
        )
        return jsonify({
            'access_token': response['AuthenticationResult']['AccessToken'],
            'id_token': response['AuthenticationResult']['IdToken'],
            'refresh_token': response['AuthenticationResult']['RefreshToken']
        }), 200
    except cognito.exceptions.NotAuthorizedException:
        return jsonify({'error': 'Incorrect username or password'}), 401
    except cognito.exceptions.UserNotConfirmedException:
        return jsonify({'error': 'User not confirmed'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run()
