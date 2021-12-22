
import logging
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
        handler = logging.FileHandler(filename=self.log_file_name,
                                      encoding="utf-8",
                                      mode="w")
        handler.setFormatter(logging.Formatter(self.settings.LOG_FORMAT))
        logger = logging.getLogger("PyttmanTestLogger")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        pyttman.logger.LOG_INSTANCE = logger

    def test_logger_as_class(self):
        expected_output_in_file = "DEBUG:PyttmanTestLogger:This is a log message"
        pyttman.logger.log("This is a log message")
        self.logfile_meets_expectation(expected_output_in_file)

    def test_logger_as_decorator(self):
        expected_output_in_file = 'raise Exception("This is a log message")'

        self.assertRaises(Exception, some_func)
        self.assertTrue(Path(self.log_file_name).exists())
        self.logfile_meets_expectation(expected_output_in_file)

    def logfile_meets_expectation(self, expected_output_in_file):
        self.assertTrue(Path(self.log_file_name).exists())
        with open(self.log_file_name, "r") as file:
            match = False
            for line in file.readlines():
                if line.strip() == expected_output_in_file:
                    match = True
        self.assertTrue(match)
