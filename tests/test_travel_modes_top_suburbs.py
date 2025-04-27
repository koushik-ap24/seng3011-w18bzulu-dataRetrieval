from hts_retrieval import modes_top_suburbs
import json
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

class TestTravelModesTopSuburbs():
    # HELPER FUNCTIONS
    def assert_valid(self, options, limit, expected_result):
        result = json.loads(modes_top_suburbs(options, limit))
        print(f"test result:\n{result}", end="\n\n")
        assert len(result["topSuburbs"]) == limit

    def assert_invalid(self, options, limit, expected_error):
        # Assert that invalid inputs return the expected error message
        jsonResult = modes_top_suburbs(options, limit)
        result = json.loads(jsonResult)
        print(f"test result:\n{result}", end="\n\n")
        assert expected_error == result["error"]


    # TEST CASES
    def test_valid_mode(self):
        options = ["vehicle passenger", "public transport"]
        limit = 5
        expected_result = {"topSuburbs": options}
        self.assert_valid(options, limit, expected_result)

    def test_invalid_options(self):
        options = ["A", "B", "C"]
        limit = 5
        self.assert_invalid(options, limit, "No data is available for these options")
