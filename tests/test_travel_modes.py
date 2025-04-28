import json
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from hts_retrieval import suburbs_travel_modes  # noqa: E402

class TestTravelModes:
    # HELPER FUNCTIONS
    def assert_valid_mode_format(self, mode_obj):
        # Assert that the given mode object is in the expected format
        expected_keys = [
            "mode", "numTrips", "pctOfTotal", "tripAvgDistance", "tripAvgTime"
        ]
        assert list(mode_obj.keys()) == expected_keys

    def assert_valid_suburb_format(self, suburb_obj):
        # Assert that the given suburb data object is in the expected format
        expected_keys = ["suburb", "travelModes"]
        assert list(suburb_obj.keys()) == expected_keys
        # Test validity of each mode data object in suburb
        modes_array = suburb_obj["travelModes"]
        for i in range(len(modes_array)):
            self.assert_valid_mode_format(modes_array[i])

    def assert_valid(self, suburbs, expected_result):
        # Assert suburbs_travel_modes() returns expected result
        result = json.loads(suburbs_travel_modes(suburbs))
        print(f"test result:\n{result}", end="\n\n")
        assert len(result["suburbsTravelModes"]) == len(expected_result["suburbsTravelModes"])
    
        # Test validity of each suburb data object
        suburbs_array = result["suburbsTravelModes"]
        for i in range(len(suburbs_array)):
            self.assert_valid_suburb_format(suburbs_array[i])

    def assert_invalid(self, suburbs, expected_error):
        # Assert that invalid inputs return the expected error message
        jsonResult = suburbs_travel_modes(suburbs)
        result = json.loads(jsonResult)
        print(f"test result:\n{result}", end="\n\n")
        assert expected_error == result["error"]


    # TEST CASES
    def test_valid_suburb(self):
        suburbs = ["Parramatta"]
        expected_result = {"suburbsTravelModes": suburbs}  # TODO: enter the actual expected result
        self.assert_valid(suburbs, expected_result)
    
    def test_valid_suburb_caret(self):
        # Test query for a suburb that has trailing characters in original DB
        suburbs = ["Waverley"]
        expected_result = {"suburbsTravelModes": suburbs}
        self.assert_valid(suburbs, expected_result)

    def test_valid_suburbs(self):
        suburbs = ["Parramatta", "Wollongong"]
        expected_result = {"suburbsTravelModes": suburbs}
        self.assert_valid(suburbs, expected_result)

    def test_missing_suburb(self):
        suburbs = ["Parramatta", "Wollongongggg"]
        self.assert_invalid(suburbs, "Data is not available for some requested suburbs")

    def test_invalid_suburbs(self):
        suburbs = ["A", "B", "C"]
        self.assert_invalid(suburbs, "No data is available for these suburbs")
