import psycopg
import math
import os
import json
from dotenv import load_dotenv
import requests
import datetime

load_dotenv()

# Helper function to establish connection to postgres DB.
def db_connect(host, port, user, password, db):
    if host and port and user and password and db:
        conn = psycopg.connect(
            "host="
            + host
            + " port="
            + port
            + " dbname="
            + db
            + " user="
            + user
            + " password="
            + password
            + " connect_timeout=4"
        )
        conn.autocommit = True  # ???
        return conn
    return None


def valid_year(year):
    if year <= 2066 and year >= 2021:
        return True
    else:
        return False

def testYearsSimple(startYear, endYear):
    if not valid_year(startYear):
        return {"error": "Invalid start year", "code": 400}
    elif not valid_year(endYear):
        return {"error": "Invalid end year", "code": 400}
    elif startYear > endYear:
        return {"error": "Start year is greater than end year", "code": 400}
    
# Returns the indices of the years in the database
# Returns False if the years are invalid
# Returns None if the years are out of range
def testYears(startYear, endYear):
    test = testYearsSimple(startYear, endYear)
    if test:
        return test
    elif startYear > 2031 and endYear - startYear < 4:
        # check if there is a valid year between start and end
        if (endYear - (endYear - 1) % 5) < startYear:
            return {"error": "Invalid year range", "code": 400}

    startDiff = startYear - 2021
    endDiff = endYear - 2021
    startIndex = (
        startDiff + 1 if startDiff <= 10 else 11 + math.ceil((startDiff - 10) / 5)
    )
    lastIndex = endDiff + 2 if endDiff <= 10 else 12 + math.floor((endDiff - 10) / 5)

    return [startIndex, lastIndex]


# Assumes that the years are valid before using testYears
def findYears(startYear, endYear):
    years = []
    indices = testYears(startYear, endYear)
    if isinstance(indices, dict) and indices.get('error'):
        return indices
    for i in range(indices[0], indices[1]):
        if i <= 11:
            years.append(2020 + i)
        else:
            years.append(2031 + 5 * (i - 11))
    return years

def findMissingYears(startYear, endYear):
    years = []
    for i in range(startYear, endYear + 1):
        if i > 2031 and (i - 1) % 5 != 0:
            years.append(i)
    return years

def findAllYears(startYear, endYear):
    return [year for year in range(startYear, endYear + 1)]

# Returns the indices of the years in the database
def dbQuery(query, suburbs):
    conn = db_connect(
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("PASSWORD"),
        db=os.getenv("DB"),
    )
    if conn is None:
        return {"error": "Unable to connect to database", "code": 500}
    curs = conn.cursor()

    if suburbs:
        curs.execute(query, (suburbs,))
    else:
        curs.execute(query)
    res = curs.fetchall()
    curs.close()
    conn.close()
    return res

def pop_all_years(suburbs):
    db_population_query = """SELECT *
        FROM population 
        WHERE lga = ANY (%s)
        ORDER BY lga ASC"""
    res = dbQuery(db_population_query, suburbs)
    if isinstance(res, dict) and res.get("error"):
        return res
    return res

def population_helper(startYear, endYear, suburbs, sortPopBy="lga", version="v1"):
    if suburbs == "":
        return {"error": "No suburb found", "code": 400}
    if not isinstance(suburbs, list):
        suburbs = [suburbs]
    if version == "v2":
        err = testYearsSimple(startYear, endYear)
        if err:
            return err
        
        full_suburbs = predict_population(startYear, endYear, suburbs)
        if isinstance(full_suburbs, dict) and full_suburbs.get("error"):
            return full_suburbs
        return full_suburbs
    
    indices = testYears(startYear, endYear)
    if isinstance(indices, dict):
        return indices
    if indices[0] == indices[1]:
        return {"error": "Invalid start year", "code": 400}

    res = pop_all_years(suburbs)
    if isinstance(res, dict) and res.get("error"):
        return res
    
    res_suburbs = []
    for i in range(len(res)):
        res_suburbs.append([res[i][0]] + list(res[i][indices[0] : indices[1]]))

    # Ensure that data is correct
    if len(res_suburbs) == 0:
        return {"error": "No suburb found", "code": 400}
    elif len(res_suburbs) != len(suburbs):
        return {"error": "DB does not have data for all suburbs", "code": 400}
    
    if version == "v1":
        return res_suburbs
    return res_suburbs

def predict_population(start, end, suburbs):
    start_year = 2021
    end_year = 2066
    data = pop_all_years(suburbs)
    if isinstance(data, dict) and data.get("error"):
        return data
    if len(data) == 0:
        return {"error": "No suburb found", "code": 400}
    elif len(data) != len(suburbs):
        return {"error": "DB does not have data for all suburbs", "code": 400}
    
    years = findYears(start_year, end_year)
    if isinstance(years, dict) and years.get("error"):
        return years
    data_dict = {}
    for i in range(len(data)):
        temp_dict = {}
        for j in range(len(years)):
            temp_dict[str(years[j])] = data[i][j + 1]
        data_dict[data[i][0]] = temp_dict
    predicted_years = findMissingYears(start_year, end_year)
    
    # Transform data to match the expected format for tango prediction
    for i in range(len(data)):
        suburb = data[i]
        suburb_data = {"data": [
            {"time_object": 
             {"timestamp": datetime.date(years[k], 1, 1).isoformat()},
             "event_type": "population",
             "attribute": {
                 "year": suburb[k + 1]
             }
            } for k in range(len(years))
        ], "value_attribute": "year", "time_points": predicted_years}
        res = tango_helper(suburb_data)
        if res.status_code != 200:
            return {"error": "Error in prediction: " + res.reason, "code": 500}
        predicted_data = res.json()
        data_dict[suburb[0]] = data_dict[suburb[0]] | predicted_data["predicted_values"]
    
    ret_data = []
    for i in range(len(data)):
        suburb = data[i][0]
        suburb_data = [suburb]
        for year in range(start, end + 1):
            suburb_data.append(data_dict[suburb][str(year)])
        ret_data.append(suburb_data)
    return ret_data

def tango_helper(data):
    res = requests.post("http://analyticsnew-370734319.ap-southeast-2.elb.amazonaws.com/predict-future-values", json=data)
    return res

def population(startYear, endYear, suburb, version="v1"):
    suburb = population_helper(startYear, endYear, suburb, version=version)
    if version == "v1":
        years = findYears(startYear, endYear)
    else:
        years = findAllYears(startYear, endYear)
    if isinstance(suburb, dict) and suburb.get("error"):
        return json.dumps({"error": suburb["error"], "code": suburb["code"]})
    suburb = suburb[0]
    return json.dumps(
        {
            "suburbPopulationEstimates": suburb[1:],
            "years": years,
        }
    )

def populations(startYear, endYear, sortPopBy, suburbs, version="v1"):
    suburb = population_helper(startYear, endYear, suburbs, sortPopBy, version=version)
    if isinstance(suburb, dict) and suburb.get("error"):
        return json.dumps({"error": suburb["error"], "code": suburb["code"]})
    years = findAllYears(startYear, endYear) if len(findYears(startYear, endYear)) > 1 else findYears(startYear, endYear)
    ret_suburb = []
    for i in range(len(suburb)):
        ret_suburb.append(
            {"suburb": suburb[i][0], "estimates": suburb[i][1:], "years": years}
        )
    return json.dumps({"suburbsPopulationEstimates": ret_suburb})

def populationAll(startYear, endYear):
    indices = testYears(startYear, endYear)
    if not indices:
        return None

    db_population_query = """SELECT * 
        FROM population
        ORDER BY lga ASC"""

    res_suburbs = dbQuery(db_population_query, None)

    for i in range(0, len(res_suburbs)):
        res_suburbs[i] = [res_suburbs[i][0]] + res_suburbs[i][startYear - 2020: endYear - 2019]

    if len(res_suburbs) == 0:
        return {"error": "No suburb found", "code": 400}

    return json.dumps({"suburbsPopulationEstimates": res_suburbs})
