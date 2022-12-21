import json
import os
import unittest

from response_operations_ui.common.mappers import (
    convert_event_list_to_dictionary,
    get_display_text_for_event,
    get_event_name,
)

project_root = os.path.dirname(os.path.dirname(__file__))


class TestMappers(unittest.TestCase):
    def test_convert_event_list_to_dictionary(self):
        with open(
            f"{project_root}/test_data/collection_exercise/" f"closest_future_collection_exercise.json"
        ) as json_data:
            collection_exercise = json.load(json_data)
        function_input = collection_exercise["events"]
        expected_output = {
            "mps": "2020-07-01T06:00:00.000Z",
            "go_live": "2020-07-02T06:00:00.000Z",
            "return_by": "2020-07-20T06:00:00.000Z",
            "reminder": "2020-07-21T06:00:00.000Z",
            "exercise_end": "2020-07-30T06:00:00.000Z",
            "ref_period_start": "2020-06-01T06:00:00.000Z",
            "ref_period_end": "2020-06-30T06:00:00.000Z",
        }
        output = convert_event_list_to_dictionary(function_input)
        self.assertEqual(output, expected_output)

    def test_convert_event_list_to_dictionary_empty_list(self):
        function_input = []
        expected_output = {}
        output = convert_event_list_to_dictionary(function_input)
        self.assertEqual(output, expected_output)

    def test_convert_event_list_to_dictionary_none_input(self):
        function_input = None
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
                "timestamp": "2020-03-01T06:00:00.000Z",
            },
        ]
        with self.assertRaises(KeyError):
            convert_event_list_to_dictionary(function_input)

    def test_get_display_text_for_event(self):
        tests = [
            ["mps", "MPS (Main print selection)"],
            ["go_live", "Go live"],
            ["return_by", "Return by"],
            ["reminder", "First reminder"],
            ["fake_event", "fake_event"],
            ["", ""],
            [None, None],
            [1, 1],
        ]
        for test in tests:
            output = get_display_text_for_event(test[0])
            expected_output = test[1]
            self.assertEqual(output, expected_output)

    def test_get_event_name(self):
        tests = [
            ["mps", "Main print selection"],
            ["go_live", "Go Live"],
            ["return_by", "Return by"],
            ["reminder", "First reminder"],
            ["reminder2", "Second reminder"],
            ["nudge_email_0", "Schedule nudge email"],
            ["nudge_email_1", "Schedule nudge email"],
            ["fake_event", None],
            ["", None],
            [None, None],
        ]
        for test in tests:
            output = get_event_name(test[0])
            expected_output = test[1]
            self.assertEqual(output, expected_output)
