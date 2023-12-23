
import functools
import traceback

import pyttman


class PyttmanLogger:
    """
    Wrapper class designed to work as a method
    decorator, making logging of output and caught
    errors easier.

    Begin with creating the logging instance of
    choice, configuring it the way you want, then
    pass it to the logger.set_logger method.

    @pyttman.logger
    def myfunc(self, *args, **kwargs):
        ...

    log (method):
        If you want to manually log custom messages in your code,
        you can call this method. See method docstring / help
        for parameters and how to use it.
    """

    LOG_INSTANCE = None

    def __call__(self, func):
        """
        Wrapper method for providing logging functionality.
        Use @logger to implement this method where logging
        of methods are desired.
        """
        def inner(*args, log_level="debug", log_exception=True, **kwargs):
            """
            Inner method, executing the func parameter function,
            as well as executing the logger.
            :returns:
                Output from executed function in parameter func
            """
            PyttmanLogger._verify_config_complete()
            try:
                results = func(*args, **kwargs)
                message = f"Return value from '{func.__name__}': '{results}'"
                self.log(message=message, level=log_level)
                return results
            except Exception as e:
                if log_exception:
                    message = (f"Exception occurred in {func.__name__}. "
                               f"Traceback: {traceback.format_exc()} {e}")
                    self.log(message=message, level="error")
                raise e
        return inner

    @staticmethod
    def _verify_config_complete():
        if pyttman.logger.LOG_INSTANCE is None:
            raise RuntimeError('Internal Pyttman Error: '
                               'No Logger instance set.\r\n')

    def loggedmethod(self, func: callable):
        """
        Backward compatibility only; use @logger
        """
        def inner(*args, **kwargs):
            return self.__call__(func)(*args, **kwargs)
        return inner

    def log(self, message: str, level="debug") -> None:
        """
        Allow for manual logging during runtime.
        """
        PyttmanLogger._verify_config_complete()
        log_levels = {"info": self.LOG_INSTANCE.info,
                      "debug": self.LOG_INSTANCE.debug,
                      "error": self.LOG_INSTANCE.error}
        try:
            log_levels[level](message)
        except KeyError:
            log_levels["debug"](message)
