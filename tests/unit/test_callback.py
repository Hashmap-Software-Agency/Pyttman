from unittest import TestCase

import pyttman


class TestCallback(TestCase):

    def get_time(self):
        print("get_time called")

    def get_area(self):
        print("get_area_called")

    def setUp(self) -> None:
        self.message = pyttman.Message()
        self.time_callback = pyttman.Callback(func=self.get_time, lead="get", trail="time")

    def test_matches(self):
        self.message.content = ["get", "time"]
        self.assertTrue(self.time_callback.matches(self.message))
        self.assertEqual(self.time_callback.func, self.get_time)
