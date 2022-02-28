
import logging
import sys
from pathlib import Path

import pyttman
from tests.module_helper import PyttmanInternalBaseTestCase


@pyttman.logger.loggedmethod
def some_func():
    raise Exception("This is a log message")


class TestPyttmanLogger(PyttmanInternalBaseTestCase):

    def test_logger_as_class(self):
        expected_output_in_file = "DEBUG:PyttmanTestLogger:This is a log message"
        pyttman.logger.log("This is a log message")
        self.logfile_meets_expectation(expected_output_in_file)

    def test_logger_as_decorator(self):
        expected_output_in_file = 'raise Exception("This is a log message")'

        self.assertRaises(Exception, some_func)
        self.assertTrue(Path(self.log_file_name).exists())
        self.logfile_meets_expectation(expected_output_in_file)

    def test_shell_handler(self):
        shell_handler = logging.StreamHandler(sys.stdout)
        self.settings.LOG_TO_STDOUT = True
        if self.settings.LOG_TO_STDOUT:
            self.logger.addHandler(shell_handler)
        pyttman.logger.log("This is a shell output")

    def logfile_meets_expectation(self, expected_output_in_file):
        self.assertTrue(Path(self.log_file_name).exists())
        with open(self.log_file_name, "r") as file:
            match = False
            for line in file.readlines():
                if line.strip() == expected_output_in_file:
                    match = True
        self.assertTrue(match)

