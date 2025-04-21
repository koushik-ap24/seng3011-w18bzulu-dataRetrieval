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

def travel_helper(suburb):
    # Validity checks
    if suburb == "":
        return {"error": "No suburbs entered", "code": 400}
    db_travel_query = f"""
        SELECT travel_mode, trips_by_mode, pct_of_total_trips, trip_avg_distance, trip_avg_time
        FROM transport_mode 
        WHERE hh_lga_name ILIKE '{suburb}'
        AND financial_year = '2022/23'
        ORDER BY travel_mode ASC
        """
    res = dbQuery(db_travel_query)
    print(f"query result:\n{res}", end="\n\n")
    return res

def travel_modes(suburb):
    """
    Returns statistics related to various modes of transport in the given
    suburb.
    """
    modes_data = []
    mode_keys = [
        "mode", "numTrips", "pctOfTotal", "tripAvgDistance", "tripAvgTime"
    ]
    res = travel_helper(suburb)

    for i in range(len(res)):
        # Create dict object containing info for a particular transport mode
        modes_data.append(dict(zip(mode_keys, res[i])))

    return json.dumps({"suburbTravelModes": modes_data})
