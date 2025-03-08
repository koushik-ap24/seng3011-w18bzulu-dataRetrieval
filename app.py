from flask import Flask, jsonify
#from mangum import Mangum  # Required to make Flask Lambda-compatible
import retrival

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Hello from Flask on AWS Lambda!")

#handler = Mangum(app)

# Sample change
@app.get("/population/v1")
def population(startYear, endYear, suburb):
    suburb = retrival.population(startYear, endYear, suburb)
    if not suburb:
        return "", 400
    return jsonify(suburbPopulationEstimate=suburb)

#app.run()