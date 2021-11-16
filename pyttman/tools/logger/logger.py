#     MIT License
#
#      Copyright (c) 2021-present Simon Olofsson
#
#      Permission is hereby granted, free of charge, to any person obtaining a copy
#      of this software and associated documentation files (the "Software"), to deal
#      in the Software without restriction, including without limitation the rights
#      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#      furnished to do so, subject to the following conditions:
#
#      The above copyright notice and this permission notice shall be included in all
#      copies or substantial portions of the Software.
#
#      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#      IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#      FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#      AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#      LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#      OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#      SOFTWARE.
import functools
import traceback
from logging import Logger
from pathlib import Path

import pyttman


class PyttmanLogger:
    """
    Wrapper class designed to work as a method
    decorator, making logging of output and caught
    errors easier.

    Begin with creating the logging instance of
    choice, configuring it the way you want, then
    pass it to the logger.set_logger method.

    __verify_complete (method):
        Internal use only. Used upon importing the package
        in __init__.py, to ensure the PyttmanLogger class has a
        dedicated `logger` instance to work with.

    loggedmethod (decorator method):
        This method is designed to be a decorator for bound
        and unbound methods in a software stack. The log method
        is static and has a closure method called inner, where
        the wrapped method is executed. Exceptions & return from
        the wrapped method are both logged to the log file using
        the static 'logging' instance, configured for the class.
        Simply add the decorator above your method to enable logging
        for it. Presuming you import this package as pyttman;

        @pyttman.logger.log
        def myfunc(self, *args, **kwargs):
            ...

    log (method):
        If you want to manually log custom messages in your code,
        you can call this method. See method docstring / help
        for parameters and how to use it.
    """

    LOG_INSTANCE = None

    @staticmethod
    def __verify_config_complete():
        if pyttman.logger.LOG_INSTANCE is None:
            raise RuntimeError('Internal Pyttman Error: '
                               'No Logger instance set.\r\n')

    @staticmethod
    def loggedmethod(func):
        """
        Wrapper method for providing logging functionality.
        Use @logger to implement this method where logging
        of methods are desired.
        :param func:
            method that will be wrapped
        :returns:
            function
        """
        @functools.wraps(func)
        def inner(*args, **kwargs):
            """
            Inner method, executing the func paramter function,
            as well as executing the logger.
            :returns:
                Output from executed function in parameter func
            """
            PyttmanLogger.__verify_config_complete()

            try:
                results = func(*args, **kwargs)
                return results
            except Exception as e:
                pyttman.logger.LOG_INSTANCE.error(
                    f'Exception occured in {func.__name__}. Traceback '
                    f'{traceback.format_exc()} {e}')
                raise e
        return inner

    @staticmethod
    def log(message: str, level="debug") -> None:
        """
        Allow for manual logging during runtime.
        :param message: str, message to be logged
        :param level: level for logging
        :returns:
            arbitrary
        """
        PyttmanLogger.__verify_config_complete()
        log_levels = {'info': lambda _message: pyttman.logger.LOG_INSTANCE.info(_message),
                      'debug': lambda _message: pyttman.logger.LOG_INSTANCE.debug(_message),
                      'error': lambda _message: pyttman.logger.LOG_INSTANCE.error(_message)}
        try:
            log_levels[level](message)
        except KeyError:
            log_levels['debug'](message)
