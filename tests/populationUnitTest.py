import unittest
import json
from retrival.py import population

class populationUnitTest(unittest.TestCase):
    def validYearRangeQuery(self):
        jsonResult = population(2026, 2028, "Ryde")
        result = json.loads(jsonResult)
        estArray = result["suburbPopulationEstimate"]
        yearArray = result["year"]
        self.assertEqual(len(estArray), 3)
        self.assertListEqual([2026, 2027, 2028], yearArray)
    
    def singleYearQuery(self):
        jsonResult = population(2022, 2022, "Burwood")
        result = json.loads(jsonResult)
        estArray = result["suburbPopulationEstimate"]
        yearArray = result["year"]
        self.assertEqual(len(estArray), 1)
        self.assertListEqual([2022], yearArray)
    
    def invalidEndYear(self):
        jsonResult = population(2021, 2088, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid end year", err)
    
    def invalidStartYear(self):
        jsonResult = population(1999, 2023, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid start year", err)

    def invalidYearRange(self):
        jsonResult = population(2026, 2040, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid year range", err)
    
    def invalidSuburb(self):
        jsonResult = population(2021, 2022, "Auburn")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("DB does not have data for all suburbs", err)
    
    def emptySuburb(self):
        jsonResult = population(2021, 2022, "")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("No suburb found", err)

if __name__ == '__main__':
    unittest.main()