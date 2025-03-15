import unittest
import json
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from retrival import population

class populationUnitTest(unittest.TestCase):
    def testValidYearRangeQuery(self):
        jsonResult = population(2026, 2028, "Ryde")
        result = json.loads(jsonResult)
        estArray = result["suburbPopulationEstimate"]
        yearArray = result["year"]
        self.assertEqual(len(estArray), 3)
        self.assertListEqual([2026, 2027, 2028], yearArray)
    
    def testSingleYearQuery(self):
        jsonResult = population(2022, 2022, "Burwood")
        result = json.loads(jsonResult)
        estArray = result["suburbPopulationEstimate"]
        yearArray = result["year"]
        self.assertEqual(len(estArray), 1)
        self.assertListEqual([2022], yearArray)

    def testValidMissingYearsQuery(self):
        jsonResult = population(2033, 2041, "Burwood")
        result = json.loads(jsonResult)
        estArray = result["suburbPopulationEstimate"]
        yearArray = result["year"]
        self.assertEqual(len(estArray), 2)
        self.assertListEqual([2036, 2041], yearArray)
    
    def testInvalidEndYear(self):
        jsonResult = population(2021, 2088, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid end year", err)
    
    def testInvalidStartYear(self):
        jsonResult = population(1999, 2023, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid start year", err)

    def testInvalidYearRange(self):
        jsonResult = population(2042, 2044, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid year range", err)

    def testInvalidYearOrder(self):
        jsonResult = population(2030, 2021, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Start year is greater than end year", err)
    
    def testInvalidSuburb(self):
        jsonResult = population(2021, 2022, "A")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("No suburb found", err)
    
    def testEmptySuburb(self):
        jsonResult = population(2021, 2022, "")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("No suburb found", err)

if __name__ == '__main__':
    unittest.main()