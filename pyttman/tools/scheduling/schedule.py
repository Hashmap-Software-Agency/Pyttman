import asyncio
import functools
import inspect
import warnings
from datetime import datetime
from queue import Queue
from typing import Dict, Generator, Any, Callable, Tuple
from multidict import MultiDict


from pyttman.tools.scheduling.components import Job, TimeTrigger


# noinspection PyPep8Naming
class schedule:
    """
    Namespacing static class to schedule
    function calls, using TimeTrigger and Job
    objects.

    Works as a decorator using the
    'method' method as @Schedule.method,
    or by calling Schedule.run() with
    provided args.
    """
    id_job_map: Dict[int, Job] = {}
    name_job_map: MultiDict[str, Job] = MultiDict()
    outputs: Queue[Job] = Queue()

    @staticmethod
    def method(func, at: str = None, every: str = None,
               delay=None, exactly_at: datetime = None,
               recipient: Callable = None, start_now=True,
               async_loop=None, **kwargs) -> Job:
        """
        Registers a new schedule Job. Provide strings
        to define when to execute the job, if it is
        recurring and whether to pass the output to
        another callable as 'recipient'.

        example:
            schedule.method(every="day", at="10:30",
                            func=some_func,
                            some_arg="hello world")

        With defined recipient which will receive the
        output from the job as the first arg:

        example:
            schedule.method(every="day", at="10:30",
                            func=some_func,
                            some_arg="hello world",
                            recipient=print)

        Users can provide an async loop to schedule an async task
        in, but it is not mandatory - this may cause problems
        however in context managed async tasks which requires
        access to the loop to retrieve tasks themselves.
        TL;DR - if problems occur when 'async_loop' argument
        is omitted - provide the loop for where to schedule
        the recipient coroutine.

        @param func: Callable to be scheduled - unbound or bound, sync or async
        @param at: str, Timestamp for execution, "HH:MM" ("HH:MM:SS optionally)
        @param every: str Options: monday -> friday, day, hour, minute, second
        @param delay: str, Delay execution, "HH:MM:SS" ("HH:MM:SS optionally)
        @param exactly_at: datetime object, Exact point in time for execution
        @param recipient: callable to which the job output will be passed to
        @param start_now: Start the job now, default: True. If not,
                          see schedule.unstarted
        @param async_loop: optional loop to schedule job and/or recipient in
        @param kwargs: kwargs, passed to the function in 'func' when creating
                       the partial function which is then passed to the Job
        @return: Job instance

        """
        async_warn = "\nThe callable '{0}' is asynchronous but the " \
                     "'async_loop' argument was omitted, and no async " \
                     "loop is running.\nThis will cause the job to be " \
                     "executed through 'asyncio.run().'\n"
        return_self = False

        # Create a TimeTrigger for the Job
        trigger = TimeTrigger(every=every, at=at,
                              delay=delay,
                              exactly_at=exactly_at)

        if not (recipient := recipient):
            recipient = schedule.schedule_default_catcher
            return_self = True

        func_is_async = inspect.iscoroutinefunction(func)
        recipient_is_async = inspect.iscoroutinefunction(recipient)
        if func_is_async or recipient_is_async:
            if async_loop is None:
                try:
                    async_loop = asyncio.get_running_loop()
                # No loop is running, and none was provided.
                except RuntimeError:
                    warnings.warn(async_warn.format(func))

        if inspect.iscoroutinefunction(recipient) and async_loop is None:
            warnings.warn(async_warn.format(recipient))

        job = Job(func=functools.partial(func, **kwargs),
                  is_async=func_is_async,
                  trigger=trigger,
                  recipient=recipient,
                  func_name=repr(func),
                  async_loop=async_loop,
                  return_self=return_self)

        # Map job in schedule and start it
        schedule.name_job_map.add(job.func_name, job)

        # Start the job, or add it to unstarted for later starts
        if start_now:
            job.start()
            schedule.id_job_map[job.native_id] = job
        return job

    @staticmethod
    def schedule_default_catcher(job: Job) -> None:
        """
        This is the default method for return values of
        schedule jobs, if no recipient is specified
        by the creator of a schedule job.

        All Jobs without a designated recipient
        callable will have their return value end
        up in this method which maps their return
        value with themselves as source, in a dict object
        and stored in the public accessible queue "outputs".

        :param job: Job instance which has been executed
                    at least once
        """
        schedule.outputs.put(job)

    @staticmethod
    def get_jobs(job_name: str = None, job_id: int = None) -> \
            Generator[Job, Any, None]:
        """
        Returns Job instance(s) that matches provided
        args. Since many jobs can share the same name,
        multidict is used when mapping against its name.
        Their native_id is unique however, thus a regular
        dict is used for mapping jobs against their native_id.


        :param job_name: str, name of the job to return (optional)
        :param job_id: int, id of the job to return (optional
        :rtype: Job instance
        :raises: ValueError, if both name and id are None
        """
        if job_name is None and id is None:
            raise ValueError("either job_name or job_id must be specified")

        if job_name:
            try:
                for job in schedule.name_job_map.getall(job_name):
                    yield job
            except KeyError:
                yield
        elif job_id:
            try:
                yield schedule.id_job_map[int(job_id)]
            except KeyError:
                yield

    @staticmethod
    def kill_job_gracefully(job_name=None, job_id=None):
        """
        Kill jobs gracefully.
        :param job_name: str, name of the job
        :param job_id: int, id of the job
        """
        for job in schedule.get_jobs(job_name, job_id):
            job.kill_gracefully()

    @staticmethod
    def get_all_jobs() -> Generator[Job, Any, None]:
        """
        Returns all jobs, in name_job_map and id_job_map
        combined.
        :rtype: Job
        """
        for i in schedule.name_job_map.values():
            yield i

    @staticmethod
    def has_outputs() -> bool:
        """
        Returns whether there are outputs in
        the output queue 'schedule.outputs'
        """
        return bool(schedule.outputs.qsize())

    @staticmethod
    def get_latest_output():
        return schedule.outputs.get()

    @staticmethod
    def get_unstarted_jobs(name: str = None) -> Tuple[Job]:
        """
        Returns collection of all jobs that are not
        running at the moment.
        @param name: Job name (may return multiple)
        @return: Tuple with Jobs
        """
        if name:
            return tuple([i for i in schedule.get_jobs(name)
                          if i.running is False])
        return tuple([i for i in schedule.get_all_jobs()
                      if i.running is False])

    @staticmethod
    def start_job(name: str) -> None:
        """
        Start the scheduling of a given method,
        if a Job with the name is found
        @param name: Name of the job to start (may start multiple)
        @return: None
        """
        for job in schedule.get_jobs(job_name=name):
            job.start()
            schedule.id_job_map[job.native_id] = job
