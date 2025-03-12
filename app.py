from flask import Flask, jsonify
import awsgi
import sys
import os

# Only modify path in Lambda environment
if os.environ.get('AWS_EXECUTION_ENV') is not None:
    sys.path.append("/opt")  # AWS Lambda mounts layers under /opt

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Hello from Flask on AWS Lambda!")

def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})

if __name__ == "__main__":
    app.run()