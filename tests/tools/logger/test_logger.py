
import logging
import os
import sys
from pathlib import Path
from unittest import TestCase

import pyttman
from pyttman.core.internals import Settings


@pyttman.logger.loggedmethod
def some_func():
    raise Exception("This is a log message")


class TestPyttmanLogger(TestCase):

    settings = Settings()
    settings.LOG_FILE_DIR = Path(__file__).parent

    log_file_name = Path(settings.LOG_FILE_DIR) / "pyttman_tests.log"
    settings.APP_NAME = "PyttmanTests"
    settings.LOG_FORMAT = logging.BASIC_FORMAT
    pyttman.settings = settings
    pyttman.is_configured = True

    def setUp(self) -> None:
        self.file_handler = logging.FileHandler(filename=self.log_file_name,
                                                encoding="utf-8",
                                                mode="w")
        self.file_handler.setFormatter(logging.Formatter(
            self.settings.LOG_FORMAT))
        self.logger = logging.getLogger("PyttmanTestLogger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.file_handler)

        pyttman.logger.LOG_INSTANCE = self.logger

    def tearDown(self) -> None:
        self.file_handler.close()
        if Path(self.log_file_name).exists():
            os.remove(self.log_file_name)

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

