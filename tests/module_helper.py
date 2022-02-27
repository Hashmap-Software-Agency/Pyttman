import pyttman
import logging
from pathlib import Path
from unittest import TestCase

from core.internals import Settings


class PyttmanInternalBaseTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        settings = Settings()
        settings.LOG_FILE_DIR = Path(__file__).parent

        log_file_name = Path(settings.LOG_FILE_DIR) / "pyttman_tests.log"
        settings.APP_NAME = "PyttmanTests"
        settings.LOG_FORMAT = logging.BASIC_FORMAT

        file_handler = logging.FileHandler(filename=log_file_name,
                                           encoding="utf-8",
                                           mode="w")
        file_handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        logger = logging.getLogger("PyttmanTestLogger")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        pyttman.settings = settings
        pyttman.logger.LOG_INSTANCE = logger
        pyttman.is_configured = True
        super().__init__(*args, **kwargs)
