from flask import Flask, jsonify
from mangum import Mangum  # Required to make Flask Lambda-compatible
import awsgi
import sys
import os

# Only modify path in Lambda environment
if os.environ.get('AWS_EXECUTION_ENV') is not None:
    sys.path.append(os.path.join(os.path.dirname(__file__), "dependencies"))

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Hello from Flask on AWS Lambda!")

def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})

if __name__ == "__main__":
    app.run()