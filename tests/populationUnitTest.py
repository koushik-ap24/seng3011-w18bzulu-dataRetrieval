import unittest
from population.py import getPopulation

class populationUnitTest(unittest.TestCase):
    def validYearRangeQuery(self):
        result = getPopulation(2026, 2028, "Ryde")
        self.assertGreater(len(result), 3)
    
    def singleYearQuery(self):
        result = getPopulation(2022, 2022, "Burwood")
    
    def invalidYearRangeQuery(self):
        result = getPopulation(2026, 2021, "Albury")
        self.assertRaises(Exception)
    
    def invalidYearQuery(self):
        result = getPopulation(1999, 2021, "Albury")
        self.assertRaises(Exception)

if __name__ == '__main__':
    unittest.main()