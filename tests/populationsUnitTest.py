import unittest
import json
from retrival.py import populations

class populationsUnitTest(unittest.TestCase):
    def validYearRangeQuery(self):
        jsonResult = populations(2021, 2030, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        resultArr = result["suburbsPopulationEstimates"]
        self.assertEqual(len(resultArr), 3)
        for suburb in resultArr:
            self.assertEqual(len(suburb["estimates"]), 10)
    
    def singleYearQuery(self):
        jsonResult = populations(2022, 2022, "ERP", ["Burwood", "Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        resultArr = result["suburbsPopulationEstimates"]
        self.assertEqual(len(resultArr), 4)
        for suburb in resultArr:
            self.assertEqual(len(suburb["estimates"]), 1)
    
    def validMissingYearsQuery(self):
        jsonResult = populations(2055, 2057, "ERP", ["Burwood", "Strathfield"])
        result = json.loads(jsonResult)
        resultArr = result["suburbsPopulationEstimates"]
        self.assertEqual(len(resultArr), 2)
        for suburb in resultArr:
            self.assertEqual(len(suburb["estimates"]), 1)
        
    def invalidStartYear(self):
        jsonResult = populations(1998, 2026, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid start year", err)

    def invalidEndYear(self):
        jsonResult = populations(2025, 2191, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid end year", err)

    def invalidYearOrder(self):
        jsonResult = populations(2027, 2025, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Start year is greater than end year", err)
    
    def invalidYearRange(self):
        jsonResult = populations(2033, 2034, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid year range", err)

    def invalidSuburbs(self):
        jsonResult = populations(2023, 2027, "ERP", ["A", "B", "C"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("No suburb found", err)

    def missingSuburb(self):
        jsonResult = populations(2023, 2027, "ERP", ["Albury", "B"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("DB does not have data for all suburbs", err)

if __name__ == '__main__':
    unittest.main()