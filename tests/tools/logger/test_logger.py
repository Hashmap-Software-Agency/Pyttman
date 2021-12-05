# MIT License
#  Copyright (c) 2021-present Simon Olofsson
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
import logging
import os
import unittest
from pathlib import Path
from unittest import TestCase, skip

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
