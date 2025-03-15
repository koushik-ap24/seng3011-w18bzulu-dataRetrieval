import unittest
import json
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from retrival import populations

class populationsUnitTest(unittest.TestCase):
    def testValidYearRangeQuery(self):
        suburbs = ["Ryde", "Albury", "Strathfield"]
        jsonResult = populations(2021, 2025, "ERP", suburbs)
        result = json.loads(jsonResult)
        resultArr = result["suburbsPopulationEstimates"]
        self.assertEqual(len(resultArr), 3)
        for suburb in resultArr:
            self.assertEqual(len(suburb["estimates"]), 10)
            self.assertListEqual(suburb["years"], [2021, 2022, 2023, 2024, 2025])
            self.assertIn(suburb["suburb"], suburbs)
    
    def testSingleYearQuery(self):
        suburbs = ["Burwood", "Ryde", "Albury", "Strathfield"]
        jsonResult = populations(2022, 2022, "ERP", suburbs)
        result = json.loads(jsonResult)
        resultArr = result["suburbsPopulationEstimates"]
        self.assertEqual(len(resultArr), 4)
        for suburb in resultArr:
            self.assertEqual(len(suburb["estimates"]), 1)
            self.assertListEqual(suburb["years"], [2022])
            self.assertIn(suburb["suburb"], suburbs)
    
    def testValidMissingYearsQuery(self):
        suburbs = ["Burwood", "Strathfield"]
        jsonResult = populations(2055, 2057, "ERP", suburbs)
        result = json.loads(jsonResult)
        resultArr = result["suburbsPopulationEstimates"]
        self.assertEqual(len(resultArr), 2)
        for suburb in resultArr:
            self.assertEqual(len(suburb["estimates"]), 1)
            self.assertListEqual(suburb["years"], [2056])
            self.assertIn(suburb["suburb"], suburbs)

        
    def testInvalidStartYear(self):
        jsonResult = populations(1998, 2026, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid start year", err)

    def testInvalidEndYear(self):
        jsonResult = populations(2025, 2191, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid end year", err)

    def testInvalidYearOrder(self):
        jsonResult = populations(2027, 2025, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Start year is greater than end year", err)
    
    def testInvalidYearRange(self):
        jsonResult = populations(2033, 2034, "ERP", ["Ryde", "Albury", "Strathfield"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid year range", err)

    def testInvalidSuburbs(self):
        jsonResult = populations(2023, 2027, "ERP", ["A", "B", "C"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("No suburb found", err)

    def testMissingSuburb(self):
        jsonResult = populations(2023, 2027, "ERP", ["Albury", "B"])
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("DB does not have data for all suburbs", err)

if __name__ == '__main__':
    unittest.main()