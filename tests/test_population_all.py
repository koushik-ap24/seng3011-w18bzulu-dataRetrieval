# import json
# import sys
# import os
# import pytest

# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# sys.path.append(parent_dir)

# try:
#     from retrieval import populationAll
# except ImportError:
#     # Skip tests if retrieval.py or populationAll() don't exist
#     pytest.skip(reason="could not import populationAll", allow_module_level=True)

# class TestPopulationAll():
#     def helperValidQuery(self, start, end, expectedEst, expectedYears):
#         jsonResult = populationAll(start, end)
#         result = json.loads(jsonResult)
#         resultArr = result["suburbsPopulationEstimates"]
#         assert len(resultArr) == 129
#         for suburb in resultArr:
#             assert len(suburb["estimates"]) == expectedEst
#             assert suburb["years"] == expectedYears

#     def helperInvalidQuery(self, start, end, errMsg):
#         jsonResult = populationAll(start, end)
#         result = json.loads(jsonResult)
#         assert errMsg == result["error"]

#     def testValidYearRangeQuery(self):
#         self.helperValidQuery(2021, 2024, 4, [2021, 2022, 2023, 2024])
    
#     def testSingleYearQuery(self):
#         self.helperValidQuery(2030, 2030, 1, [2030])
    
#     def testValidMissingYearsQuery(self):
#         self.helperValidQuery(2041, 2046, 2, [2041, 2046])
        
#     def testInvalidStartYear(self):
#         self.helperInvalidQuery(1899, 2029, "Invalid start year")

#     def testInvalidEndYear(self):
#         self.helperInvalidQuery(2040, 7890, "Invalid end year")

#     def testInvalidYearOrder(self):
#         self.helperInvalidQuery(2031, 2025, "Start year is greater than end year")
    
#     def testInvalidYearRange(self):
#         self.helperInvalidQuery(2049, 2050, "Invalid year range")
