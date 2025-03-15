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

    def validMissingYearsQuery(self):
        jsonResult = population(2033, 2041, "Burwood")
        result = json.loads(jsonResult)
        estArray = result["suburbPopulationEstimate"]
        yearArray = result["year"]
        self.assertEqual(len(estArray), 2)
        self.assertListEqual([2036, 2041], yearArray)
    
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
        jsonResult = population(2042, 2044, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Invalid year range", err)

    def invalidYearOrder(self):
        jsonResult = population(2030, 2021, "Albury")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("Start year is greater than end year", err)
    
    def invalidSuburb(self):
        jsonResult = population(2021, 2022, "A")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("No suburb found", err)
    
    def emptySuburb(self):
        jsonResult = population(2021, 2022, "")
        result = json.loads(jsonResult)
        err = result["Error"]
        self.assertEquals("No suburb found", err)

if __name__ == '__main__':
    unittest.main()