class PyttmanProjectInvalidException(BaseException):
    """
    Exception class for internal use.
    Raise this exception in situations when a user
    project is incorrectly configured in whatever way.
    """
    pass


class TypeConversionFailed(BaseException):
    """
    Exception class for internal use.
    Raise this exception when a type conversion fails.
    """
    def __init__(self, from_type, to_type):
        message = f"Type '{from_type}' could not be converted to '{to_type}'."
        super().__init__(message)


class InvalidPyttmanObjectException(BaseException):
    """
    This error is raised when a user-implementation of a component within
    the Pyttman API is not correctly configured by the developer.
    """
    def __init__(self, message):
        super().__init__(message)


class ClientImproperlyConfiguredError(BaseException):
    """
    This error is raised when a Client is misconfigured in settings.py
    for a pyttman project.
    """
    def __init__(self, message):
        super().__init__(message)

