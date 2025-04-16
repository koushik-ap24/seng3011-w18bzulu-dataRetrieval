import json
import sys
import os
import pytest

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

try:
    from retrieval import populations
except ImportError:
    # Skip tests if retrieval.py or populations() don't exist
    pytest.skip(reason="could not import populations", allow_module_level=True)


class TestPopulations():
    def helperValidQuery(self, start, end, suburbs, expectedEst, expectedYears):
        jsonResult = populations(start, end, "ERP", suburbs, version="v2")
        result = json.loads(jsonResult)
        resultArr = result["suburbsPopulationEstimates"]
        assert len(resultArr) == len(suburbs)
        for suburb in resultArr:
            assert len(suburb["estimates"]) == expectedEst
            assert suburb["years"] == expectedYears
            assert suburb["suburb"] in suburbs

    def helperInvalidQuery(self, start, end, suburbs, errMsg):
        jsonResult = populations(start, end, "ERP", suburbs, version="v2")
        result = json.loads(jsonResult)
        assert errMsg == result["error"]

    def testValidYearRangeQuery(self):
        suburbs = ["Ryde", "Albury", "Strathfield"]
        self.helperValidQuery(2021, 2025, suburbs, 5, [2021, 2022, 2023, 2024, 2025])
    
    def testSingleYearQuery(self):
        suburbs = ["Burwood", "Ryde", "Albury", "Strathfield"]
        self.helperValidQuery(2022, 2022, suburbs, 1, [2022])
    
    def testValidMissingYearsQuery(self):
        suburbs = ["Burwood", "Strathfield"]
        years = list(range(2055, 2062))
        self.helperValidQuery(2055, 2061, suburbs, len(years), years)
    
    def testValidMissingAllYearsQuery(self):
        suburbs = ["Burwood", "Strathfield", "Randwick"]
        years = list(range(2021, 2067))
        self.helperValidQuery(2021, 2066, suburbs, len(years), years)