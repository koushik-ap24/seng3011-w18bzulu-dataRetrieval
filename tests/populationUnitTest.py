import unittest
from retrival.py import population

class populationUnitTest(unittest.TestCase):
    def validYearRangeQuery(self):
        result = population(2026, 2028, "Ryde")
        self.assertEqual(len(result), 3)
    
    def singleYearQuery(self):
        result = population(2022, 2022, "Burwood")
        self.assertEqual(len(result), 1)
    
    def invalidYearRangeQuery(self):
        result = population(2026, 2021, "Albury")
        self.assertRaises(Exception)
    
    def invalidYearQuery(self):
        result = population(1999, 2021, "Albury")
        self.assertRaises(Exception)

if __name__ == '__main__':
    unittest.main()