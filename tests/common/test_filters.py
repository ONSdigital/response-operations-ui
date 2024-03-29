import json
import os
import unittest

from freezegun import freeze_time

from response_operations_ui.common.filters import (
    get_current_collection_exercise,
    get_nearest_future_key_date,
)

project_root = os.path.dirname(os.path.dirname(__file__))


class TestFilters(unittest.TestCase):
    def test_get_nearest_future_key_date_empty_list(self):
        """Tests a  survey with no collection exercises will return an empty list.  This can occur when only the survey
        has been created but no collection exercises created for it yet."""
        function_input = []
        expected_output = {}
        output = get_nearest_future_key_date(function_input)
        self.assertEqual(output, expected_output)

    def test_get_nearest_future_key_date_with_blank_collection_exercise(self):
        """Tests a survey with a collection exercise that's in its most empty state will return an empty
        dict."""
        with open(
            f"{project_root}/test_data/collection_exercise/single_new_collection_exercise_for_survey.json"
        ) as json_data:
            collection_exercise_list = json.load(json_data)

        expected_output = {}
        output = get_nearest_future_key_date(collection_exercise_list[0]["events"])
        self.assertEqual(output, expected_output)

    @freeze_time("2020-05-01")
    def test_get_nearest_future_key_date_future_dates_only(self):
        """Tests that given set of events with only future dates, the closest future event to 'today'
        will be picked"""
        with open(f"{project_root}/test_data/collection_exercise/closest_future_collection_exercise.json") as json_data:
            collection_exercise = json.load(json_data)

        expected_output = {
            "id": "573e60ce-4041-4cd6-8d09-9048457db0af",
            "collectionExerciseId": "aec41b04-a177-4994-b385-a16136242d05",
            "tag": "mps",
            "timestamp": "2020-07-01T06:00:00.000Z",
            "eventStatus": "PROCESSED",
        }
        output = get_nearest_future_key_date(collection_exercise["events"])
        self.assertEqual(output, expected_output)

    @freeze_time("2020-05-01")
    def test_get_nearest_future_key_date_past_dates_only(self):
        """Tests that given set of events with only past dates, the function will return an empty dict as it only
        works for events in the future"""
        with open(f"{project_root}/test_data/collection_exercise/closest_past_collection_exercise.json") as json_data:
            collection_exercise = json.load(json_data)

        expected_output = {}
        output = get_nearest_future_key_date(collection_exercise["events"])
        self.assertEqual(output, expected_output)

    def test_get_current_collection_exercise_empty_list(self):
        """Tests a survey with no collection exercises will return an empty list.  This can occur when only the survey
        has been created but no collection exercises created for it yet."""
        function_input = {}
        expected_output = {}
        output = get_current_collection_exercise(function_input)
        self.assertEqual(output, expected_output)

    def test_get_current_collection_exercise_with_blank_collection_exercise(self):
        """Tests a survey with a collection exercise that's in its most empty state will return an empty
        dict."""
        with open(
            f"{project_root}/test_data/collection_exercise/single_new_collection_exercise_for_survey.json"
        ) as json_data:
            collection_exercise_list = json.load(json_data)

        expected_output = {}
        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

    @freeze_time("2020-05-01")
    def test_get_current_collection_exercise_future_dates_only(self):
        """Tests that given set of collection exercises with only future dates, the closest date to 'today'
        will be picked"""
        with open(f"{project_root}/test_data/collection_exercise/only_future_collection_exercises.json") as json_data:
            collection_exercise_list = json.load(json_data)

        with open(f"{project_root}/test_data/collection_exercise/closest_future_collection_exercise.json") as json_data:
            expected_output = json.load(json_data)

        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

    @freeze_time("2020-05-01")
    def test_get_current_collection_exercise_past_dates_only(self):
        """Tests that given set of collection exercises with only past dates, the closest date to 'today'
        will be picked"""
        with open(f"{project_root}/test_data/collection_exercise/only_past_collection_exercises.json") as json_data:
            collection_exercise_list = json.load(json_data)

        expected_output = {}

        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

    @freeze_time("2020-05-01")
    def test_get_current_collection_exercise_past_and_future_dates(self):
        """Tests that given set of collection exercises with past and future dates, the closest date to 'today'
        will be picked"""
        with open(
            f"{project_root}/test_data/collection_exercise/mixed_past_and_future_collection_exercises.json"
        ) as json_data:
            collection_exercise_list = json.load(json_data)

        with open(f"{project_root}/test_data/collection_exercise/closest_future_collection_exercise.json") as json_data:
            expected_output = json.load(json_data)

        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

    @freeze_time("2020-05-01")
    def test_get_current_collection_exercise_duplicate_start_dates(self):
        """Tests that when there are two collection exercises with the same start date, the one that was seen first
        will be the one returned."""
        with open(
            f"{project_root}/test_data/collection_exercise/multiple_same_start_collection_exercises.json"
        ) as json_data:
            collection_exercise_list = json.load(json_data)

        with open(f"{project_root}/test_data/collection_exercise/closest_future_collection_exercise.json") as json_data:
            expected_output = json.load(json_data)

        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)
