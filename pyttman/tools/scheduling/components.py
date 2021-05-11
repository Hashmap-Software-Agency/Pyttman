import asyncio
import inspect
import time
from datetime import datetime, timedelta
from threading import Thread
from typing import Callable

import pyttman


class TimeTrigger:
    """
    TimeTrigger class

    The TimeTrigger class acts like a timed clock
    which can be wound up using different measurements
    and units of time. It can be set to trigger
    at a certain time, delay a certain amount of time
    has passed, be a recurring trigger with a defined
    interval of delay.

    """
    timeformat = "%H:%M:%S"
    day_int = {
        "day": (0, 1, 2, 3, 4, 5, 6),
        "monday": (0,),
        "tuesday": (1,),
        "wednesday": (2,),
        "thursday": (3,),
        "friday": (4,),
        "saturday": (5,),
        "sunday": (6,),
    }

    timeunits = {
        "hour": timedelta(hours=1),
        "minute": timedelta(minutes=1),
        "second": timedelta(seconds=1),
    }

    def __init__(self, at: str=None, every: str=None,
                 delay=None, exactly_at: datetime=None):
        """
        Configures the TimeTrigger object according
        to provided arguments.

        :param every: str, a day, every day or timeunit.
            Valid parameters:
                "day", "monday", "tuesday", "wednesday"
                "thursday", "friday", "saturday"
                "sunday", "hour", "minute", "second"

        :param at: str, time of scheduling.
                  Valid in HH:MM:SS format or HH:MM format.
                  Example: "10:00" or "10:00:22". Seconds (SS)
                  defaults to 00 if not specified.
        :param exactly_at: datetime object which will be set to
                           self.next_trigger if present, bypassing
                           the other parameters every, at, and delay.
                           Useful for scenarios when a datetime
                           object is created outside by the creator
                           for a specific day and time when the job
                           is to be run.
        """
        self.amount_of_runs = 0
        self.next_trigger: datetime = datetime.now()
        self.last_trigger: datetime = None
        self.reoccurring: bool = False
        self.timedelta_interval: timedelta = None
        self.days_to_run: tuple[int] = None
        self.delay = None

        if exactly_at:
            self.next_trigger = exactly_at
        if at:
            at = self.__validate_timestring(at)
            parsed_time = datetime.strptime(at, self.timeformat)
            self.next_trigger = self.next_trigger.replace(
                hour=parsed_time.hour,
                minute=parsed_time.minute,
                second=parsed_time.second)
        elif delay:
            delay = self.__validate_timestring(delay)
            parsed_time = datetime.strptime(delay, self.timeformat)
            self.delay = timedelta(hours=parsed_time.hour,
                                   minutes=parsed_time.minute,
                                   seconds=parsed_time.second)
        if every:
            self.reoccurring = True
            if not (_repeat_every := self.day_int.get(every)):
                if not (_repeat_every := self.timeunits.get(every)):
                    raise ValueError(
                        f"'{every}' is an invalid value for 'every'")
            if isinstance(_repeat_every, tuple):
                # It's a day of week, or every day in the week
                self.days_to_run = _repeat_every
            elif isinstance(_repeat_every, timedelta):
                # It's every minute, hour or second
                self.timedelta_interval = _repeat_every

        if not any((at, every, delay, exactly_at)):
            raise AttributeError("TimeTrigger needs at least one rule "
                                 "for scheduling: 'every', 'at', 'delay', "
                                 "'exactly_at'")

        self.reset()

    def __repr__(self):
        return f"TimeTrigger(" \
               f"next_trigger={self.next_trigger}, " \
               f"last_trigger={self.last_trigger}, " \
               f"amount_of_runs={self.amount_of_runs}, " \
               f"reoccuring={self.reoccurring})" \


    @staticmethod
    def __validate_timestring(timestr: str) -> str:
        if len(timestr.split(":")) < 3:
            return f"{timestr}:00"
        return timestr

    def is_pulled(self):
        if datetime.now() >= self.next_trigger:
            if self.reoccurring:
                self.reset()
            self.amount_of_runs += 1
            self.last_trigger = datetime.now()
            return True
        return False

    def reset(self) -> None:
        """
        Reset itself to a future point in time,
        based on the rules provided at instantiation.

        If for example it is configured to run
        every day, the next day in line will
        be assigned to the datetime object in
        self.next_trigger.

        If a timedelta is the configured interval,
        the self.next_trigger will be mutated with
        this value.
        :returns: None
        """
        if self.days_to_run:
            if datetime.now() >= self.next_trigger:
                self.next_trigger += timedelta(days=1)
            while not self.next_trigger.weekday() in self.days_to_run:
                self.next_trigger += timedelta(days=1)
        elif self.timedelta_interval:
            self.next_trigger += self.timedelta_interval
        if self.delay:
            self.next_trigger += self.delay


class Job(Thread):
    """
    Threaded job, scheduled for a specific
    interval and / or time of execution.

    The Job class is runnable as a separate
    thread, thus leaving any function that it's
    calling non-blocking.

    The Job can run both async and sync functions
    both as the main callable and recipients.

    Users can provide which loop to schedule an async task
    in, but it is not mandatory - this may cause problems
    however in context managed async tasks which requires
    access to the loop to retrieve tasks themselves.

    TL;DR - if problems occur when 'async_loop' argument
    is omitted - provide the loop for where to schedule
    the recipient coroutine.
    """

    def __init__(self, func: Callable,
                 is_async: bool,
                 trigger: TimeTrigger,
                 recipient: Callable,
                 func_name: str,
                 async_loop = None,
                 return_self: bool = False):
        super().__init__()
        self.kwargs = None
        self.func = func
        self.is_async = is_async
        self.func_name = func_name
        self.trigger = trigger
        self.recipient = recipient
        self.return_self = return_self
        self.time_to_die = False
        self.error = None
        self.result = None
        self.async_loop = async_loop
        self._running = False

    def __repr__(self):
        return f"Job(" \
               f"func_name={self.func_name}, " \
               f"is_async={self.is_async}, " \
               f"running={self.running}, " \
               f"recipient={self.recipient.__name__}, " \
               f"native_id={self.native_id}, " \
               f"trigger={self.trigger}, " \
               f"result='{self.result}', " \
               f"error={f'{type(self.error).__name__}({self.error})' if self.error else None}" \
               f")"

    def run(self) -> None:
        """
        Thread overloaded method
        Await the TimeTrigger object to fire on
        it's point in time, and call the callable
        passed as self.func.
        """
        self._running = True
        loop = asyncio.new_event_loop() if not self.async_loop else self.async_loop

        while True:
            if self.time_to_die:
                pyttman.logger.log(
                    f"Job '{self.native_id}' got a "
                    f"graceful kill signal, shutting "
                    f"down.")
                break

            # Evaluate if self.func and / or recipient is async or not
            if self.trigger.is_pulled():
                try:
                    # Evaluate whether main callable and/or recipient is async
                    if self.is_async:
                        loop.create_task(self.func())
                    else:
                        self.result = self.func()
                except Exception as e:
                    pyttman.logger.log(f"The schedule job '{self.name}' "
                                      f"raised {type(e).__name__}('{str(e)}') "
                                      f"upon executing it", level="error")
                    self.error = e
                    break

                # Call the recipient function with the job output
                output = self if self.return_self else self.result

                try:
                    if inspect.iscoroutinefunction(self.recipient):
                        loop.create_task(self.recipient(output))
                    else:
                        self.recipient(output)
                except Exception as e:
                    pyttman.logger.log(f"The schedule job '{self.name}' "
                                       f"ran OK but the recipient function "
                                       f"{self.recipient} raised {type(e).__name__}"
                                       f"('{str(e)}') ", level="error")
                    break
            if not self.trigger.reoccurring and self.trigger.amount_of_runs > 0:
                break
            time.sleep(0.01)
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def kill_gracefully(self) -> None:
        """
        Provices a method to set the self.time_to_die
        to True to signal it's time to check out
        """
        self.time_to_die = True
