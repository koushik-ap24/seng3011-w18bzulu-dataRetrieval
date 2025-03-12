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
    if not valid_year(startYear) or not valid_year(endYear) or startYear > endYear:
        return False
    if startYear > 2031 and endYear - startYear < 4:
        # check if there is a valid year between start and end
        if (endYear - (endYear - 1) % 5) < startYear:
            return False
    startDiff = startYear - 2021
    endDiff = endYear - 2021
    startIndex = startDiff + 1 if startDiff <= 10 else 11 + math.ceil((startDiff - 10) / 5)
    lastIndex = endDiff + 2 if endDiff <= 10 else 12 + math.ceil((endDiff - 10) / 5)
    return [startIndex, lastIndex]

# Returns the indices of the years in the database
def dbQuery(query, conn, suburbs, indices, sortByStart=True):
    curs = conn.cursor()
    cols = [constants.COLUMN_NAMES[0]] + constants.COLUMN_NAMES[indices[0]:indices[1]]
    cols = str(cols).replace("[", "").replace("]", "")
    if sortByStart:
        curs.execute(query, (cols, suburbs, constants.COLUMN_NAMES[indices[0]]))
    elif not sortByStart:
        curs.execute(query, (cols, suburbs, constants.COLUMN_NAMES[indices[1] - 1]))
    res = curs.fetchall()
    conn.close()
    return res

def population(startYear, endYear, suburbs, sortPopBy=None, sortByStart=True):
    indices = testYears(startYear, endYear)
    if not indices:
        return None
    
    if type(suburbs) != list:
        suburbs = [suburbs]
    
    # TODO: ADD DB CONNECTION
    conn = db_connect(secret.host, secret.port, secret.user, secret.password, secret.db)
    
    db_population_query = """SELECT %s 
        FROM population 
        WHERE lga IN %s
        ORDER BY %s"""
    suburbs = str(suburbs).replace("[", "(").replace("]", ")")
    res_suburbs = dbQuery(db_population_query, conn, suburbs, indices, sortByStart)

    # Ensure that data is correct
    if len(res_suburbs) == 0:
        # TODO: add error message
        print("Suburb not found")
        return None
    elif len(res_suburbs) != indices[1] - indices[0] + 1:
        # TODO: add error message
        print("ERROR: DB does not have data for all suburbs")
        return None

    return res_suburbs

def populationAll(startYear, endYear, sortPopBy=None, sortByStart=True):
    indices = testYears(startYear, endYear)
    if not indices:
        return None
    
    conn = db_connect(secret.host, secret.port, secret.user, secret.password, secret.db)
    
    db_population_query = """SELECT %s 
        FROM population
        ORDER BY %s"""
    suburbs = "ANY"

    res_suburbs = dbQuery(db_population_query, conn, suburbs, sortByStart, indices)

    return res_suburbs