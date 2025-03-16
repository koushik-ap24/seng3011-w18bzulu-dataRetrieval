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
        jsonResult = populations(start, end, "ERP", suburbs)
        result = json.loads(jsonResult)
        resultArr = result["suburbsPopulationEstimates"]
        assert len(resultArr) == len(suburbs)
        for suburb in resultArr:
            assert len(suburb["estimates"]) == expectedEst
            assert suburb["years"] == expectedYears
            assert suburb["suburb"] in suburbs

    def helperInvalidQuery(self, start, end, suburbs, errMsg):
        jsonResult = populations(start, end, "ERP", suburbs)
        result = json.loads(jsonResult)
        assert errMsg == result["error"]

    def testValidYearRangeQuery(self):
        suburbs = ["Ryde", "Albury", "Strathfield"]
        self.helperValidQuery(2021, 2025, suburbs, 10, [2021, 2022, 2023, 2024, 2025])
    
    def testSingleYearQuery(self):
        suburbs = ["Burwood", "Ryde", "Albury", "Strathfield"]
        self.helperValidQuery(2022, 2022, suburbs, 1, [2022])
    
    def testValidMissingYearsQuery(self):
        suburbs = ["Burwood", "Strathfield"]
        self.helperValidQuery(2055, 2057, suburbs, 1, [2056])
        
    def testInvalidStartYear(self):
        suburbs = ["Ryde", "Albury", "Strathfield"]
        self.helperInvalidQuery(1999, 2025, suburbs, "Invalid start year")

    def testInvalidEndYear(self):
        suburbs = ["Ryde", "Albury", "Strathfield"]
        self.helperInvalidQuery(2023, 2099, suburbs, "Invalid end year")

    def testInvalidYearOrder(self):
        suburbs = ["Ryde", "Albury", "Strathfield"]
        self.helperInvalidQuery(2027, 2025, suburbs, "Start year is greater than end year")
    
    def testInvalidYearRange(self):
        suburbs = ["Ryde", "Albury", "Strathfield"]
        self.helperInvalidQuery(2033, 2034, suburbs, "Invalid year range")

    def testInvalidSuburbs(self):
        suburbs = ["A", "B", "C"]
        self.helperInvalidQuery(2023, 2027, suburbs, "No suburb found")

    def testMissingSuburbs(self):
        suburbs = ["Albury", "B"]
        self.helperInvalidQuery(2023, 2027, suburbs, "DB does not have data for all suburbs")
