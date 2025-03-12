import psycopg
import math
import secret
import constants

def db_connect(host, port, user, password, db):
    conn = psycopg.connect(
        host,
        port,
        user,
        password,
        db
    )
    conn.autocommit = True # ???

    return conn

def valid_year(year):
    if year <= 2066 and year >= 2021:
        return True

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

# Returns the indices of the years in the database
def dbQuery(query, conn, suburbs, indices):
    curs = conn.cursor()
    cols = [constants.COLUMN_NAMES[0]] + constants.COLUMN_NAMES[indices[0]:indices[1]]
    cols = str(cols).replace("[", "").replace("]", "")
    if suburbs:
        curs.execute(query, (cols, suburbs))
    else:
        curs.execute(query, (cols,))
    res = curs.fetchall()
    conn.close()
    return res

def population(startYear, endYear, suburbs):
    indices = testYears(startYear, endYear)
    if type(indices[0]) == dict:
        return indices
    
    if type(suburbs) != list:
        suburbs = [suburbs]
    
    # TODO: ADD DB CONNECTION
    conn = db_connect(secret.host, secret.port, secret.user, secret.password, secret.db)
    
    db_population_query = """SELECT %s 
        FROM population 
        WHERE lga IN %s
        ORDER BY lga ASCENDING"""
    suburbs = str(suburbs).replace("[", "(").replace("]", ")")
    res_suburbs = dbQuery(db_population_query, conn, suburbs, indices)

    # Ensure that data is correct
    if len(res_suburbs) == 0:
        return {"Error": "No suburb found", "Code": 400}
    elif len(res_suburbs) != len(suburbs):
        return {"Error": "DB does not have data for all suburbs", "Code": 400}
    return res_suburbs

def populationAll(startYear, endYear):
    indices = testYears(startYear, endYear)
    if not indices:
        return None
    
    conn = db_connect(secret.host, secret.port, secret.user, secret.password, secret.db)
    
    db_population_query = """SELECT %s 
        FROM population
        ORDER BY lga ASCENDING"""

    res_suburbs = dbQuery(db_population_query, conn, None, indices)
    
    if len(res_suburbs) == 0:
        return {"Error": "No suburb found", "Code": 400}
    
    return res_suburbs