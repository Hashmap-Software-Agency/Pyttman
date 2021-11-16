"""
Details:
    2020-07-05
    
    pyttman framework source file with decorator
    objects

    This module contains functions and classes that are
    intended for use as decorators throughout the stack.
"""


# noinspection PyPep8Naming


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