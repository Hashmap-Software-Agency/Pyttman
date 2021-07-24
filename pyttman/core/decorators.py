import sys
import functools
import pyttman

"""
Details:
    2020-07-05
    
    pyttman framework source file with decorator
    objects

    This module contains functions and classes that are
    intended for use as decorators throughout the stack.
"""


# noinspection PyPep8Naming
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
                pyttman.logger.LOG_INSTANCE.debug(
                    f'Ran method "{func.__name__}" in {func.__module__} '
                    f'with ARGS: {args} & KWARGS: {kwargs} & RETURN: {results}')
                return results
            except Exception as e:
                pyttman.logger.LOG_INSTANCE.error(
                    f'Exception occured in {func.__name__}: {e}')
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


# Deprecated since 1.3.1
def scheduledmethod(func):
    """
    Schedule method decorator. In certain applications
    the ability to automatically call functions by the
    means of a schedule in some manner, for example with
    a schedule.Scheduler() instance object, it can be 
    desired to direct messages to different channels in 
    the front end application such as a Discord or Slack
    server. If, however the method is called as per usual,
    the behavior is not altered. Add this decorator above
    a method in your stack, and then add the parameter
    'channel' when you call it through the scheduler routine.

    The returned value from this will be a dictionary where
    the function output is under the 'result' key, and the
    channel is under the 'channel' key, as seen below.
    """

    # Deprecated since 1.3.1
    raise DeprecationWarning("The scheduledmethod decorator is deprecated "
                             "since 1.3.1 and is no longer supported. "
                             "But fear not - Check out the 'schedule.method' "
                             "decorator to use the built-in scheduler in the "
                             "framework!")