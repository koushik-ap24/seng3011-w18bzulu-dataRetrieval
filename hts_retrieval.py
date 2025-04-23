import os
import json
from dotenv import load_dotenv
from retrieval import db_connect

load_dotenv()

# Constants
MODE_OPTIONS = [
    "vehicle driver",
    "vehicle passenger",
    "public transport",
    "walk linked",
    "walk only",
    "other"
]

PURPOSE_OPTIONS = [
    "commute",
    "work related business",
    "education/childcare",
    "shopping",
    "social/recreation",
    "personal business",
    "serve passenger",
    "other"
]

def db_query(query):
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

def map_category_data(data, category):
    """
    Given a tuple of data for one transport mode or travel purpose, converts
    the tuple into a dict object with a unique key for each data type.
    """
    data_keys = [
        category, "numTrips", "pctOfTotal", "tripAvgDistance", "tripAvgTime"
    ]
    data_arr = list(data)
    data_arr[0] = data[0].rstrip("*")  # Clean up mode/purpose trailing chars
    return dict(zip(data_keys, data_arr))

def suburbs_data_helper(suburbs, category):
    # Validity checks
    if suburbs == "":
        return {"error": "No suburbs entered", "code": 400}

    formatted_suburbs = ', '.join(f"'{s}', '{s}^'" for s in suburbs)

    # Formulate query based on which category of travel data was requested
    if category == "mode":
        db_table = "transport_mode"
        select_cols = "travel_mode, trips_by_mode, pct_of_total_trips, trip_avg_distance, trip_avg_time"
        category_key = "travelModes"
    elif category == "purpose":
        db_table = "transport_reason"
        select_cols = "travel_purpose, journeys_by_purpose, pct_of_total_journeys, journey_avg_distance, journey_avg_time"
        category_key = "travelPurposes"
    else:
        return {
            "error": "Category must be either 'mode' or 'purpose", "code": 400
        }

    db_travel_query = f"""
        SELECT hh_lga_name, {select_cols}
        FROM {db_table}
        WHERE hh_lga_name IN ({formatted_suburbs})
        AND financial_year = '2022/23'
        """
    res = db_query(db_travel_query)
    print(f"query result:\n{res}", end="\n\n")

    # Error check
    if len(res) == 0:
        return {"error": "No data is available for these suburbs", "code": 400}

    suburbs_result = []
    suburb_data = {}

    # Extract data from each row of the query result
    for i in range(len(res)):
        suburb_name = res[i][0].rstrip("^")
        prev_suburb_name = suburb_data.get("suburb")

        # If finished compiling all data for a suburb, append to results
        if suburb_name != prev_suburb_name:
            if prev_suburb_name != None:
                suburbs_result.append(suburb_data.copy())
            # Overwrite existing dict to store data for a new suburb
            suburb_data["suburb"] = suburb_name
            suburb_data[category_key] = []

        # Extract travel mode/purpose statistics
        suburb_data[category_key].append(
            map_category_data(res[i][1:], category)
        )

    suburbs_result.append(suburb_data)  # Append final suburb to results

    # Error check for missing suburb
    if len(suburbs_result) != len(suburbs):
        return {
            "error": "Data is not available for some requested suburbs",
            "code": 400
        }
    return suburbs_result

def top_suburbs_helper(options, category, limit):
    # TODO: check that all given categories are valid
    if limit <= 0 or limit > 25:
        return {
            "error": "Limit must not be less than 1 or greater than 25",
            "code": 400
        }

    # Formulate query based on which category of travel data was requested
    if category == "mode":
        db_table = "transport_mode"
        category_key = "travel_mode"
        numtrips_key = "trips_by_mode"
        pcttrips_key = "pct_of_total_trips"
    elif category == "purpose":
        db_table = "transport_reason"
        category_key = "travel_purpose"
        numtrips_key = "journeys_by_purpose"
        pcttrips_key = "pct_of_total_journeys"
    else:
        return {
            "error": "Category must be either 'mode' or 'purpose", "code": 400
        }

    # If category options list is empty, search for all options by default
    if options == "":
        options = MODE_OPTIONS if category == "mode" else PURPOSE_OPTIONS
    formatted_options = list(s.capitalize() for s in options)
    print(formatted_options)
    formatted_options = ', '.join(f"'{s}', '{s}*', '{s}**'" for s in formatted_options)
    print(formatted_options)
    db_travel_query = f"""
        SELECT hh_lga_name,
        SUM({numtrips_key}) AS sum_num_trips,
        SUM({pcttrips_key}),
        STRING_AGG({category_key}, ', '),
        STRING_AGG(CAST({numtrips_key} AS varchar), ', '),
        STRING_AGG(CAST({pcttrips_key} AS varchar), ', ')
    FROM {db_table}
    WHERE {category_key} IN ({formatted_options})
    AND financial_year = '2022/23'
    GROUP BY hh_lga_name
    ORDER BY sum_num_trips DESC
    LIMIT {limit}
    """
    # db_travel_query = f"""
    #     SELECT hh_lga_name,
    #     SUM(journeys_by_purpose) AS sum_num_trips,
    #     SUM(pct_of_total_journeys),
    #     STRING_AGG(travel_purpose, ', '),
    #     STRING_AGG(CAST(journeys_by_purpose AS varchar), ', '),
    #     STRING_AGG(CAST(pct_of_total_journeys AS varchar), ', ')
    # FROM {db_table}
    # WHERE financial_year = '2022/23'
    # GROUP BY hh_lga_name
    # ORDER BY sum_num_trips DESC
    # LIMIT {limit}
    # """
    print(f"query:\n{db_travel_query}", end="\n\n")
    res = db_query(db_travel_query)
    print(f"query result:\n{res}", end="\n\n")

    # Error check
    if len(res) == 0:
        return {"error": "No data is available for these options", "code": 400}

    top_suburbs_result = []

    # Extract data from each row of the query result
    for i in range(len(res)):
        row = res[i]
        suburb_name = row[0].rstrip("^")
        sum_num_trips = row[1]
        sum_pct_trips = row[2]

        # Convert string lists of values into actual lists
        res_options = row[3].split(", ")
        num_trips_by_option = row[4].split(", ")
        pct_trips_by_option = row[5].split(", ")
        # TODO: check that all lists are the same length

        # Create list of all modes/purposes for the suburb
        options_stats = []
        for n in range(len(res_options)):
            option = res_options[n].rstrip("*")
            num_trips = num_trips_by_option[n]
            pct_trips = pct_trips_by_option[n]
            options_stats.append({
                f"{category}": option,
                "numTrips": num_trips,
                "pctOfTotal": pct_trips
            })

        # Create dictionary to store suburb data, then append to results
        top_suburbs_result.append(
            {
                "suburb": suburb_name,
                "rank": i + 1,
                "sumStats": {
                    "numTrips": sum_num_trips,
                    "pctOfTotal": sum_pct_trips
                },
                f"{category}Stats": options_stats
            }
        )

    """
    {"topSuburbs": [
        {
        "suburb": suburb,
        "rank": integer,
        "sumStats": {
            "numTrips": integer,
            "pctOfTotal": float
        },
        "purposeStats: [{
            "purpose": purpose,
            "numTrips": integer,
            "pctOfTotal": float
        }]
      }
    ]}
    """
    return top_suburbs_result


def suburbs_travel_modes(suburbs):
    """
    Returns statistics about each mode of transport for each of the given
    suburbs.
    """
    res = suburbs_data_helper(suburbs, "mode")
    # Check if result is an error (returned as a dict object)
    if isinstance(res, dict):
        return json.dumps(res)
    return json.dumps({"suburbsTravelModes": res})

def suburbs_travel_purposes(suburbs):
    """
    Returns statistics about various travel purposes in each of the
    given suburbs.
    """
    res = suburbs_data_helper(suburbs, "purpose")
    # Check if result is an error (returned as a dict object)
    if isinstance(res, dict):
        return json.dumps(res)
    return json.dumps({"suburbsTravelPurposes": res})

def modes_top_suburbs(modes, limit):
    """
    Returns statistics for suburbs with the highest number of trips associated
    with the given mode(s). Suburbs are returned in sorted order from
    highest to lowest counts.
    """
    res = top_suburbs_helper(modes, "mode", limit)
    # Check if result is an error (returned as a dict object)
    if isinstance(res, dict):
        return json.dumps(res)
    return json.dumps({"topSuburbs": res})

def purposes_top_suburbs(purposes, limit):
    """
    Returns statistics for suburbs with the highest number of trips associated
    with the given purpose(s). Suburbs are returned in sorted order from
    highest to lowest counts.
    """
    res = top_suburbs_helper(purposes, "purpose", limit)
    # Check if result is an error (returned as a dict object)
    if isinstance(res, dict):
        return json.dumps(res)
    return json.dumps({"topSuburbs": res})
