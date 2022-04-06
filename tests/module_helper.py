import logging
import os
from pathlib import Path
from unittest import TestCase

import pyttman
from pyttman.core.internals import Settings


class PyttmanInternalBaseTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        filename_incrementer = 0
        self.settings = Settings()
        self.settings.FATAL_EXCEPTION_AUTO_REPLY = "Critical errors occurred"
        self.settings.LOG_FILE_DIR = Path(__file__).parent

        while True:
            self.log_file_name = Path(self.settings.LOG_FILE_DIR) / \
                                 f"pyttman_tests_{filename_incrementer}.log"
            if Path(self.log_file_name).exists() is False:
                break
            else:
                filename_incrementer += 1

        self.settings.APP_NAME = "PyttmanTests"
        self.settings.LOG_FORMAT = logging.BASIC_FORMAT

        self.file_handler = logging.FileHandler(filename=self.log_file_name,
                                                encoding="utf-8",
                                                mode="w")
        self.file_handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))

        logger = logging.getLogger("PyttmanTestLogger")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.file_handler)

        pyttman.settings = self.settings
        pyttman.logger.LOG_INSTANCE = logger
        pyttman.is_configured = True
        self.logger = logger
        super().__init__(*args, **kwargs)

    def cleanup(self):
        """
        Optional hook to execute after test completes (tearDown is
        already overloaded)
        """
        pass

    def tearDown(self) -> None:
        self.file_handler.close()
        if Path(self.log_file_name).exists():
            os.remove(self.log_file_name)
        self.cleanup()
