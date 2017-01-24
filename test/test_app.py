from os import path
import unittest
import comp62521

class TestApp(unittest.TestCase):

    def setUp(self):
        dir, _ = path.split(__file__)
        data = "dblp_curated_sample.xml"
        comp62521.app.config['TESTING'] = True
        comp62521.app.config['DATASET'] = data
        comp62521.app.config['DATABASE'] = path.join(dir, "..", "data", data)
        self.app = comp62521.app.test_client()

    def test_home(self):
        r = self.app.get("/")
        self.assertEqual(200, r.status_code, "Status code was not 'OK'.")

if __name__ == '__main__':
    unittest.main()
