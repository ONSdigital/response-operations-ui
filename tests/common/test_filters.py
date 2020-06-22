import json
import unittest

from freezegun import freeze_time

from response_operations_ui.common.filters import get_current_collection_exercise


class TestFilters(unittest.TestCase):

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
        file_paths = ['test_data/single_new_collection_exercise_for_survey.json',
                      'tests/test_data/collection_exercise/single_new_collection_exercise_for_survey.json']
        collection_exercise_list = self.load_file(file_paths)

        expected_output = {}
        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

    @freeze_time('2020-05-01')
    def test_get_current_collection_exercise_future_dates_only(self):
        """Tests that given set of collection exercises with only future dates, the closest date to 'today'
        will be picked"""
        file_paths = ['test_data/only_future_collection_exercises.json',
                      'tests/test_data/collection_exercise/only_future_collection_exercises.json']
        collection_exercise_list = self.load_file(file_paths)

        file_paths = ['test_data/closest_future_collection_exercise.json',
                      'tests/test_data/collection_exercise/closest_future_collection_exercise.json']
        expected_output = self.load_file(file_paths)

        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

    @freeze_time('2020-05-01')
    def test_get_current_collection_exercise_past_dates_only(self):
        """Tests that given set of collection exercises with only past dates, the closest date to 'today'
        will be picked"""
        file_paths = ['test_data/only_past_collection_exercises.json',
                      'tests/test_data/collection_exercise/only_past_collection_exercises.json']
        collection_exercise_list = self.load_file(file_paths)

        file_paths = ['test_data/closest_past_collection_exercise.json',
                      'tests/test_data/collection_exercise/closest_past_collection_exercise.json']
        expected_output = self.load_file(file_paths)

        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

    @freeze_time('2020-05-01')
    def test_get_current_collection_exercise_past_and_future_dates(self):
        """Tests that given set of collection exercises with past and future dates, the closest date to 'today'
        will be picked"""
        file_paths = ['test_data/mixed_past_and_future_collection_exercises.json',
                      'tests/test_data/collection_exercise/mixed_past_and_future_collection_exercises.json']
        collection_exercise_list = self.load_file(file_paths)

        file_paths = ['test_data/closest_past_collection_exercise.json',
                      'tests/test_data/collection_exercise/closest_past_collection_exercise.json']
        expected_output = self.load_file(file_paths)

        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

    @freeze_time('2020-05-01')
    def test_get_current_collection_exercise_duplicate_start_dates(self):
        """Tests that when there are two collection exercises with the same start date, the one that was seen first
        will be the one returned."""
        file_paths = ['test_data/multiple_same_start_collection_exercises.json',
                      'tests/test_data/collection_exercise/multiple_same_start_collection_exercises.json']
        collection_exercise_list = self.load_file(file_paths)

        file_paths = ['test_data/closest_past_collection_exercise.json',
                      'tests/test_data/collection_exercise/closest_past_collection_exercise.json']
        expected_output = self.load_file(file_paths)

        output = get_current_collection_exercise(collection_exercise_list)
        self.assertEqual(output, expected_output)

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
