import unittest
import json
from backend.optimizer.data_parse import extract_A, extract_ED, extract_EE
import unittest
import json
from backend.optimizer.data_parse import extract_A, extract_ED, extract_EE

class TestDataParse(unittest.TestCase):
    def test_extract_A_simple_dict(self):
        sample = {'emp1': {'2025-10-01': {'morning': 'O', 'evening': 'X'}}}
        res = extract_A(sample)
        self.assertIsInstance(res, list)
        self.assertTrue(any(r[0] == 'emp1' for r in res))

    def test_extract_ED_simple(self):
        ed_sample = {0: {'emp1': [{'shift': 0, 'willingness': 0.5}], 'emp2': [{'shift': 1, 'willingness': -0.2}]}}
        res = extract_ED(ed_sample)
        self.assertIsInstance(res, list)
        self.assertTrue(any(r[0] == 'emp1' for r in res))

    def test_extract_EE_simple(self):
        ee_sample = {'EMP1': {'EMP2': 0.1}, 'EMP2': {'EMP1': 0.1}}
        res = extract_EE(ee_sample)
        self.assertIsInstance(res, list)
        self.assertTrue(['EMP1', 'EMP2', 0.1] in res or ['EMP2', 'EMP1', 0.1] in res)

if __name__ == '__main__':
    unittest.main()
