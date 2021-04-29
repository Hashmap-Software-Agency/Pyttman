import os.path
from pathlib import Path
import logging
import pytz
from datetime import datetime
from dataclasses import dataclass

import pytman

"""
Details:
    2020-07-05
    
    pytman framework internal source file

Module details:
    
    data containers and functions used by objects in
    the pytman package.
"""


def is_dst(timezone: str):
    """
    method for returning a bool whether or not a timezone
    currently is in daylight savings time, useful for servers
    that run systems outside of the user timezone.
    :param timezone:
        string, timezone to give pytz for the dst query.
        look up available timezones at this url:
        https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz
        -timezones
    :returns:
        bool
    """
    timezone = pytz.timezone(timezone)
    timezone_aware_date = timezone.localize(datetime.now(), is_dst=None)
    return timezone_aware_date.tzinfo._dst.seconds != 0


@dataclass
class _cim:
    """
    This class is only used as a namespace
    for internal messages used by exceptions
    or elsewhere by pytman classes
    and functions. Not for instantiating.
    """
    deprecated_warn: str = "pytman DEPRECATED WARNING"
    warn: str = "Pytman WARNING"
    err: str = "Pytman ERROR"


def load_settings(settings):
    pytman.settings = settings
    if pytman.settings is None:
        raise NotImplementedError("Import settings in your project "
                                  "and assign pytman.settings = settings "
                                  "before calling this function")
    app_name = pytman.settings.APP_NAME
    if pytman.settings.APPEND_LOG_FILES:
        file_name = Path(f"{app_name}.log")
    else:
        file_name = Path(f"{app_name}-{datetime.now().strftime('%y%m%d-%H-%M-%S')}.log")

    log_file_name = Path(pytman.settings.LOG_FILE_DIR) / file_name
    logging_handle = logging.FileHandler(filename=log_file_name, encoding="utf-8",
                                         mode="a+" if pytman.settings.APPEND_LOG_FILES else "w")

    logging_handle.setFormatter(logging.Formatter("%(asctime)s:%(levelname)"
                                                  "s:%(name)s: %(message)s"))
    _logger = logging.getLogger("Pytman logger")
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(logging_handle)
    pytman.logger.set_logger(_logger)
    pytman.logger.log(f" -- App {app_name} started: {datetime.now()} -- ")