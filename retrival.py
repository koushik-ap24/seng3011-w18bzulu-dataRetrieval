import psycopg
import math
import secret

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

def population(startYear, endYear, suburb):
    indices = testYears(startYear, endYear)
    if not indices:
        return None
    
    # TODO: ADD DB CONNECTION
    conn = db_connect(secret.host, secret.port, secret.user, secret.password, secret.db)
    
    db_population_query = " SELECT * FROM population WHERE lga = %s"
    curs = conn.cursor()
    # colnames = [desc[0] for desc in curs.description]
    curs.execute(db_population_query, (suburb,))
    suburbs = curs.fetchall()
    conn.close()

    # Ensure that data is correct
    if len(suburbs) == 0:
        # TODO: add error message
        print("Suburb not found")
        return None
    elif len(suburbs) > 1:
        # TODO: add error meessage
        print("ERROR: DB has the suburb more than once")
        return None
    
    suburb_info = suburbs[0]
    suburb = suburb_info[indices[0]:indices[1]]

    return suburb