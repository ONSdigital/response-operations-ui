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
        admin_controller.set_banner("test")
        self.assertEqual("test", admin_controller.current_banner())

    def test_remove_banner(self):
        admin_controller.set_banner("test")
        admin_controller.remove_banner()
        self.assertIsNone(admin_controller.current_banner())
