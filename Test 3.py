import unittest
import importlib

class TestMyCode(unittest.TestCase):
    def test_main(self):
        main = importlib.import_module("main")

        def test_download_data(self):
            main = importlib.import_module("main")
            response = main.download_data("https://api.gios.gov.pl/pjp-api/rest/station/findAll")
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()

