import psycopg
import math
import constants
import os
import json
from dotenv import load_dotenv

load_dotenv()

def db_connect(host, port, user, password, db):
    conn = psycopg.connect("host=" + host + " port=" + port + " dbname=" + db + " user=" + user + " password=" + password + " connect_timeout=10")
    conn.autocommit = True # ???

    return conn

def valid_year(year):
    if year <= 2066 and year >= 2021:
        return True
    else:
        return False

# Returns the indices of the years in the database
# Returns False if the years are invalid
# Returns None if the years are out of range
def testYears(startYear, endYear):
    if not valid_year(startYear):
        return {"Error": "Invalid start year", "Code": 400}
    elif not valid_year(endYear):
        return {"Error": "Invalid end year", "Code": 400}
    elif startYear > endYear:
        return {"Error": "Start year is greater than end year", "Code": 400}
    elif startYear > 2031 and endYear - startYear < 4:
        # check if there is a valid year between start and end
        if (endYear - (endYear - 1) % 5) < startYear:
            return {"Error": "Invalid year range", "Code": 400}
    
    startDiff = startYear - 2021
    endDiff = endYear - 2021
    startIndex = startDiff + 1 if startDiff <= 10 else 11 + math.ceil((startDiff - 10) / 5)
    lastIndex = endDiff + 2 if endDiff <= 10 else 12 + math.ceil((endDiff - 10) / 5)

    return [startIndex, lastIndex]

# Assumes that the years are valid before using testYears
def findYears(startYear, endYear):
    years = []
    indices = testYears(startYear, endYear)
    for i in range(indices[0], indices[1]):
        if i <= 11:
            years.append(2020 + i)
        else:
            years.append(2021 + 5 * (i - 11))
    return years

# Returns the indices of the years in the database
def dbQuery(query, suburbs, indices):
    conn = db_connect(
        host=os.environ['host'], 
        port=os.environ['port'], 
        user=os.environ['user'], 
        password=os.environ['password'], 
        db=os.environ['db']
    )
    curs = conn.cursor()
    cols = [constants.COLUMN_NAMES[0]] + constants.COLUMN_NAMES[indices[0]:indices[1]]
    cols = ', '.join(cols)
    if suburbs:
        curs.execute(query % (cols, '%s'), (suburbs,))
    else:
        curs.execute(query, (cols,))
    res = curs.fetchall()
    conn.close()
    return res

def population_helper(startYear, endYear, suburbs, sortPopBy="lga"):
    indices = testYears(startYear, endYear)
    if isinstance(indices, dict):
        return indices
    if indices[0] == indices[1]:
        return {"Error": "Invalid start year", "Code": 400}
    if suburbs == "":
        return {"Error": "No suburb found", "Code": 400}
    if not isinstance(suburbs, list):
        suburbs = [suburbs]

    db_population_query = """SELECT %s 
        FROM population 
        WHERE lga IN %s
        ORDER BY lga ASC"""
    suburbs = str(suburbs).replace("[", "(").replace("]", ")")
    res_suburbs = dbQuery(db_population_query, suburbs, indices)

    # Ensure that data is correct
    if len(res_suburbs) == 0:
        return {"Error": "No suburb found", "Code": 400}
    elif len(res_suburbs) != len(suburbs):
        return {"Error": "DB does not have data for all suburbs", "Code": 400}
    return res_suburbs

def population(startYear, endYear, suburb):
    suburb = population_helper(startYear, endYear, suburb)
    if isinstance(suburb, dict):
        return json.dump(
            suburb["Error"], 
            status=suburb["Code"]
        )
    return json.dump(suburbPopulationEstimate=suburb[1:], years=findYears(startYear, endYear))

def populations(startYear, endYear, sortPopBy, suburbs):
    suburb = population_helper(startYear, endYear, suburbs, sortPopBy)
    if isinstance(suburb, dict):
        return json(
            suburb["Error"], 
            status=suburb["Code"]
        )
    years = findYears(startYear, endYear)
    ret_suburb = [] 
    for i in range(len(suburb)):
        ret_suburb.append(json.dump(suburb=suburb[i][0], estimate=suburb[i][1:], years=years))
    return json.dump(suburbpopulationEstimate=ret_suburb)

def populationAll(startYear, endYear):
    indices = testYears(startYear, endYear)
    if not indices:
        return None
    
    db_population_query = """SELECT %s 
        FROM population
        ORDER BY lga ASC"""

    res_suburbs = dbQuery(db_population_query, None, indices)

    if len(res_suburbs) == 0:
        return {"Error": "No suburb found", "Code": 400}
    
    return res_suburbs