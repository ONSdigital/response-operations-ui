import datetime
import json
import unittest

import responses

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.controllers import collection_exercise_controllers
from response_operations_ui.exceptions.exceptions import ApiError

ce_id = "4a084bc0-130f-4aee-ae48-1a9f9e50178f"
ce_events_by_id_url = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{ce_id}/events'

with open('tests/test_data/collection_exercise/ce_events_by_id.json') as fp:
    ce_events = json.load(fp)


class TestCollectionExerciseController(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

    def test_get_ce_events_by_id_all_events(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, ce_events_by_id_url, json=ce_events, status=200, content_type='applicaton/json')

            collection_exercise = collection_exercise_controllers.get_collection_exercise_events_by_id(ce_id)

            self.assertIn('mps', collection_exercise[0]['tag'], 'MPS not in collection exercise events')
            self.assertIn('go_live', collection_exercise[1]['tag'], 'Go live not in collection exercise events')
            self.assertIn('return_by', collection_exercise[2]['tag'], 'Return by not in collection exercise events')
            self.assertIn('exercise_end', collection_exercise[3]['tag'],
                          'Exercise end not in collection exercise events')

    def test_get_ce_events_by_id_no_events(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, ce_events_by_id_url, json=[], status=200, content_type='applicaton/json')

            collection_exercise = collection_exercise_controllers.get_collection_exercise_events_by_id(ce_id)

            self.assertEqual(len(collection_exercise), 0, 'Unexpected collection exercise event returned.')

    def test_get_ce_events_by_id_http_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, ce_events_by_id_url, status=400)

            self.assertRaises(ApiError, collection_exercise_controllers.get_collection_exercise_events_by_id, ce_id)

    def test_create_ce_event_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ce_events_by_id_url, status=200)

            timestamp = datetime.datetime.strptime(''.join("2020-01-27 07:00:00+00:00".rsplit(':', 1)),
                                                   "%Y-%m-%d %H:%M:%S%z")

            raised = False
            try:
                collection_exercise_controllers.create_collection_exercise_event(ce_id, 'mps', timestamp)
            except ApiError:
                raised = True

            self.assertFalse(raised, 'Exception raised')

    def test_create_ce_event_http_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ce_events_by_id_url, status=400)

            timestamp = datetime.datetime.strptime(''.join("2020-01-27 07:00:00+00:00".rsplit(':', 1)),
                                                   "%Y-%m-%d %H:%M:%S%z")

            self.assertRaises(ApiError, collection_exercise_controllers.create_collection_exercise_event,
                              ce_id, 'mps', timestamp)
