from response_operations_ui.controllers import admin_controller
import unittest
import fakeredis


class TestAdminController(unittest.TestCase):

    def setUp(self):
        admin_controller._get_redis = fakeredis.FakeStrictRedis()

    def test_set_banner(self):
        admin_controller.set_banner("test")
        self.assertEquals("test", admin_controller.current_banner())

    def test_remove_banner(self):
        admin_controller.set_banner("test")
        admin_controller.remove_banner()
        self.assertIsNone(admin_controller.current_banner())
