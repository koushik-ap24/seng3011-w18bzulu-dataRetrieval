import json
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from retrival import population

class TestPopulation():
    def helperValidQuery(self, start, end, suburb, expectedEst, expectedYears):
        jsonResult = population(start, end, suburb)
        result = json.loads(jsonResult)
        estArray = result["suburbPopulationEstimates"]
        yearArray = result["years"]
        assert expectedEst == len(estArray)
        assert yearArray == expectedYears

    def helperInvalidQuery(self, start, end, suburb, errMsg):
        jsonResult = population(start, end, suburb)
        result = json.loads(jsonResult)
        assert errMsg == result["error"]

    def testValidYearRangeQuery(self):
       self.helperValidQuery(2026, 2028, "Ryde", 3, [2026, 2027, 2028])

    def testSingleYearQuery(self):
        self.helperValidQuery(2022, 2022, "Burwood", 1, [2022])

    def testValidMissingYearsQuery(self):
        self.helperValidQuery(2032, 2044, "Burwood", 2, [2036, 2041])
    
    def testInvalidEndYear(self):
        self.helperInvalidQuery(2021, 2088, "Albury", "Invalid end year")
    
    def testInvalidStartYear(self):
        self.helperInvalidQuery(1999, 2023, "Albury", "Invalid start year")

    def testInvalidYearRange(self):
        self.helperInvalidQuery(2042, 2044, "Albury", "Invalid year range")

    def testInvalidYearOrder(self):
        self.helperInvalidQuery(2030, 2021, "Albury", "Start year is greater than end year")
    
    def testInvalidSuburb(self):
        self.helperInvalidQuery(2021, 2022, "A", "No suburb found")
    
    def testEmptySuburb(self):
        self.helperInvalidQuery(2021, 2022, "", "No suburb found")