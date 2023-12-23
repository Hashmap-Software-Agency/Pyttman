import logging
import os
import sys
from pathlib import Path

import pyttman
from tests.module_helper import PyttmanInternalBaseTestCase


class TestPyttmanLogger(PyttmanInternalBaseTestCase):

    cleanup_after = False

    def test_logger_as_class(self):
        expected_output_in_file = "DEBUG:PyttmanTestLogger:This is a log message"
        pyttman.logger.log("This is a log message")
        self.logfile_meets_expectation(expected_output_in_file)

    def test_logger_as_decorator(self):
        @pyttman.logger
        def broken():
            raise Exception("This is a log message")

        @pyttman.logger
        def working():
            return "I work"

        working()
        self.assertTrue(Path(self.log_file_name).exists())

        expected_output_in_file = "Return value from 'working': 'I work'"
        self.logfile_meets_expectation(expected_output_in_file)

        with self.assertRaises(Exception):
            broken()
        expected_output_in_file = 'raise Exception("This is a log message")'
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
                if expected_output_in_file in line:
                    match = True
                    break
        self.assertTrue(match)

    def cleanup(self):
        if not self.cleanup_after:
            return

        for logfile in Path().cwd().parent.parent.glob("*.log"):
            try:
                os.remove(logfile)
            except PermissionError:
                pass
