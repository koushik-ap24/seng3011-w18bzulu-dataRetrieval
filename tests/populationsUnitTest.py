import unittest
from retrival.py import populations

class populationUnitTest(unittest.TestCase):
    def validYearRangeQuery(self):
        result = populations(2021, 2030, "ERP", True, ["Ryde", "Albury", "Strathfield"])
        self.assertEqual(len(result), 3)
        for suburb in result:
            self.assertEqual(len(suburb["populationEstimates"]), 10)
    
    def singleYearQuery(self):
        result = populations(2022, 2022, "ERP", True, ["Burwood", "Ryde", "Albury", "Strathfield"])
        self.assertEqual(len(result), 4)
        for suburb in result:
            self.assertEqual(suburb["populationEstimates"], 1)
    
    def descendingOrderQuery(self):
        result = populations(2022, 2023, "ERP", False, ["Burwood", "Strathfield"])
        self.assertGreater(len(result), 2)
        for suburb in result:
            self.assertEqual(len(suburb["populationEstimates"]), 2)
        
    def invalidYearRangeQuery(self):
        result = populations(2027, 2026, "ERP", True, ["Ryde", "Albury", "Strathfield"])
        self.assertEqual(None)
    
    def invalidYearQuery(self):
        result = populations(1899, 2021, "ERP", True, ["Ryde", "Albury", "Strathfield"])
        self.assertEqual(None)

if __name__ == '__main__':
    unittest.main()