import os
import json
from dotenv import load_dotenv
from retrieval import db_connect

load_dotenv()

def dbQuery(query):
    # Returns the results of the given query in the database
    conn = db_connect(
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("PASSWORD"),
        db=os.getenv("DB"),
    )
    curs = conn.cursor()
    curs.execute(query)
    res = curs.fetchall()
    curs.close()
    conn.close()
    return res

def map_mode_data(data):
    """
    Given an array of data for one transport mode, converts the array into a
    dict object with a unique key for each data type.
    """
    mode_keys = [
        "mode", "numTrips", "pctOfTotal", "tripAvgDistance", "tripAvgTime"
    ]
    return dict(zip(mode_keys, data))

def travel_helper(suburbs):
    # Validity checks
    if suburbs == "":
        return {"error": "No suburbs entered", "code": 400}

    formatted_suburbs = ', '.join(f"'{s}'" for s in suburbs)
    db_travel_query = f"""
        SELECT hh_lga_name, travel_mode, trips_by_mode, pct_of_total_trips, trip_avg_distance, trip_avg_time
        FROM transport_mode
        WHERE hh_lga_name IN ({formatted_suburbs})
        AND financial_year = '2022/23'
        """
    res = dbQuery(db_travel_query)

    suburbs_result = []
    suburb_data = {}

    # Extract data from each row of the query result
    for i in range(len(res)):
        suburb_name = res[i][0]
        prev_suburb_name = suburb_data.get("suburb")

        # If finished compiling all data for a suburb, append to results
        if suburb_name != prev_suburb_name:
            if prev_suburb_name != None:
                suburbs_result.append(suburb_data.copy())
            # Overwrite existing dict to store data for a new suburb
            suburb_data["suburb"] = suburb_name
            suburb_data["travelModes"] = []

        # Extract travel mode statistics
        suburb_data["travelModes"].append(map_mode_data(res[i][1:]))

    suburbs_result.append(suburb_data)  # Append final suburb to results
    return suburbs_result


def suburbs_travel_modes(suburbs):
    """
    Returns statistics about each mode of transport for each of the given
    suburbs.
    """
    res = travel_helper(suburbs)
    return json.dumps({"suburbsTravelModes": res})
