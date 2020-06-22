import json
import unittest

from response_operations_ui.common.mappers import convert_event_list_to_dictionary


class TestMappers(unittest.TestCase):
    def test_convert_event_list_to_dictionary(self):
        file_paths = ['test_data/closest_future_collection_exercise.json',
                      'tests/test_data/collection_exercise/closest_future_collection_exercise.json']
        collection_exercise = self.load_file(file_paths)
        function_input = collection_exercise['events']
        expected_output = {
            "mps": "2020-07-01T06:00:00.000Z",
            "go_live": "2020-07-02T06:00:00.000Z",
            "return_by": "2020-07-20T06:00:00.000Z",
            "reminder": "2020-07-21T06:00:00.000Z",
            "exercise_end": "2020-07-30T06:00:00.000Z",
            "ref_period_start": "2020-06-01T06:00:00.000Z",
            "ref_period_end": "2020-06-30T06:00:00.000Z"
        }
        output = convert_event_list_to_dictionary(function_input)
        self.assertEqual(output, expected_output)

    def test_convert_event_list_to_dictionary_empty_list(self):
        function_input = []
        expected_output = {}
        output = convert_event_list_to_dictionary(function_input)
        self.assertEqual(output, expected_output)

    def test_convert_event_list_to_dictionary_malformed_events(self):
        """Tests that a KeyError is raised if the events are malformed (missing either tag or timestamp)"""
        function_input = [
            {
                "id": "cd3fdc36-f060-41e4-bc75-624f6f31e111",
                "collectionExerciseId": "6327160f-d7a8-4fcc-8551-a69c50b33e5f",
                "tag": "mps",
            },
            {
                "id": "d950c192-e58d-4dcb-9a38-76658dbea6dc",
                "collectionExerciseId": "6327160f-d7a8-4fcc-8551-a69c50b33e5f",
                "tag": "go_live",
                "timestamp": "2020-03-01T06:00:00.000Z"
            },
        ]
        with self.assertRaises(KeyError):
            convert_event_list_to_dictionary(function_input)

    @staticmethod
    def load_file(file_paths):
        """
        Facilitates running the tests either as a whole with run_tests.py or individually.  Both ways of running the
        tests start from a different place so relative paths don't work.  Currently only accepts lists of 2.
        :param file_paths: A list of file paths to test
        :return: The contents of the file
        """
        try:
            with open(file_paths[0]) as fp:
                file_data = json.load(fp)
        except FileNotFoundError:
            with open(file_paths[1]) as fp:
                file_data = json.load(fp)
        return file_data
