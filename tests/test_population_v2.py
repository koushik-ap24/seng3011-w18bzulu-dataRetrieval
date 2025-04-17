import json
import sys
import os
import pytest

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

try:
    from retrieval import population
except ImportError:
    # Skip tests if retrieval.py or population() don't exist
    pytest.skip(reason="could not import population", allow_module_level=True)

class TestPopulation():
    def helperValidQuery(self, start, end, suburb, expectedEst, expectedYears):
        jsonResult = population(start, end, suburb, version="v2")
        result = json.loads(jsonResult)
        estArray = result["suburbPopulationEstimates"]
        yearArray = result["years"]
        assert expectedEst == len(estArray)
        assert yearArray == expectedYears

    def helperInvalidQuery(self, start, end, suburb, errMsg):
        jsonResult = population(start, end, suburb, version="v2")
        result = json.loads(jsonResult)
        assert errMsg == result["error"]

    def testValidYearRangeQuery(self):
       self.helperValidQuery(2026, 2028, "Ryde", 3, [2026, 2027, 2028])

    def testSingleYearQuery(self):
        self.helperValidQuery(2022, 2022, "Burwood", 1, [2022])

    def testValidPredictYearsQuery(self):
        self.helperValidQuery(2032, 2044, "Burwood", 13, list(range(2032, 2045)))
    
    def testValidPredictYearsAllQuery(self):
        self.helperValidQuery(2021, 2066, "Randwick", 46, list(range(2021, 2067)))
    
    def testInvalidEndYear(self):
        self.helperInvalidQuery(2021, 2088, "Albury", "Invalid end year")
    
    def testInvalidStartYear(self):
        self.helperInvalidQuery(1999, 2023, "Albury", "Invalid start year")

    def testInvalidYearOrder(self):
        self.helperInvalidQuery(2030, 2021, "Albury", "Start year is greater than end year")
    
    def testInvalidSuburb(self):
        self.helperInvalidQuery(2021, 2022, "A", "No suburb found")
    
    def testEmptySuburb(self):
        self.helperInvalidQuery(2021, 2022, "", "No suburb found")