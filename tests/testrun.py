import unittest
import sys
import os

sys.path.append(os.path.abspath('lib'))
import rf_utils

class TestUtils(unittest.TestCase):

    def un_pickle(self, file_path):
        import pickle
        with open(file_path, 'r') as f:
            data = pickle.load(f)
            return data

    def setUp(self):
        self.test_dir = os.path.abspath(os.path.dirname(__file__))
        self.test_data = os.path.join(self.test_dir, 'data')

    def test_get_code(self):
        test_file = self.test_data + '/plot.dump'
        data = self.un_pickle(test_file)
        code = rf_utils.get_code(data[0], data[1])
        self.assertEqual(
            '0123010123012323232301010123230123232323010101010123230101012301232',
            code
        )
        
if __name__ == '__main__':
    unittest.main()