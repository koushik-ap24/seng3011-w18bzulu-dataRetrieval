from flask import Flask, jsonify
from mangum import Mangum  # Required to make Flask Lambda-compatible

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Hello from Flask on AWS Lambda!")

handler = Mangum(app)

# Sample change 2