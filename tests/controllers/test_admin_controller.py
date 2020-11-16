from response_operations_ui.controllers import admin_controller
import unittest
import fakeredis

server = fakeredis.FakeServer()


def get_fake_redis():
    return fakeredis.FakeStrictRedis(server=server, decode_responses=True)


class TestAdminController(unittest.TestCase):

    def setUp(self):
        admin_controller._get_redis = get_fake_redis

    def test_set_banner(self):
        admin_controller.set_banner_and_time('test', '16th November 2020 at 15:12')
        self.assertEqual("test", admin_controller.current_banner())

    def test_remove_banner(self):
        admin_controller.set_banner_and_time("test", '16th November 2020 at 15:12')
        admin_controller.remove_banner()
        self.assertIsNone(admin_controller.current_banner())

    def test_current_time_set(self):
        admin_controller.set_banner_and_time("test", '16th November 2020 at 15:12')
        self.assertEqual("16th November 2020 at 15:12", admin_controller.banner_time_get())

    # Placeholder test pending implementation of banner message storage:
    def test_get_alert_list(self):
        test_dict = admin_controller.get_alert_list()
        self.assertIn("Unexpected outage", test_dict.keys())
        self.assertIn("The Quarterly Vacancy Survey is unavailable until Tuesday 7 July 2020,"
                      " as we are currently experiencing some technical difficulties.",
                      test_dict.values())
