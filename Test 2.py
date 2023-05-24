import unittest
import json
from unittest.mock import Mock
from main import conv_data_to_json


class TestDataConversion(unittest.TestCase):
    def test_conv_data_to_json_valid_response(self):
        response = Mock()
        response.json.return_value = {
            'id': 1,
            'name': 'Test',
            'value': 10
        }

        result = conv_data_to_json(response)

        self.assertEqual(result, {
            'id': 1,
            'name': 'Test',
            'value': 10
        })

    def test_conv_data_to_json_invalid_response(self):
        response = Mock()
        response.json.side_effect = json.decoder.JSONDecodeError("Invalid JSON", "", 0)

        result = conv_data_to_json(response)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
