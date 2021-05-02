import functools
import inspect
from datetime import datetime
from queue import Queue
from typing import Dict, Generator, Any, Callable, Tuple

from multidict import MultiDict

from pyttman.core.decorators import Logger
from pyttman.tools.scheduling.components import Job, TimeTrigger


# noinspection PyPep8Naming
class schedule:
    """
    Namespacing static class to schedule
    function calls, using TimeTrigger and Job
    objects.

    Works as a decorator using the
    'method' method as @Schedule.method,
    or by calling Schedule.run() withr
    provided args.
    """
    id_job_map: Dict[int, Job] = {}
    name_job_map: MultiDict[str, Job] = MultiDict()
    outputs: Queue[Job] = Queue()

    @staticmethod
    def method(func, at: str=None, every: str=None,
               delay=None, exactly_at: datetime=None,
               recipient: Callable=None, start_now=True,
               **kwargs):
        """
        Registers a new schedule Job.

        @param func: Callable to be scheduled - unbound or bound, sync or async
        @param at: str, Timestamp for execution, "HH:MM" ("HH:MM:SS optionally)
        @param every: str Options: monday -> friday, day, hour, minute, second
        @param delay: str, Delay execution, "HH:MM:SS" ("HH:MM:SS optionally)
        @param exactly_at: datetime object, Exact point in time for execution
        @param recipient: callable to which the job output will be passed to
        @param start_now: Start the job now, default: True. If not,
                          see schedule.unstarted
        @param kwargs: kwargs, passed to the function in 'func' when creating
                       the partial function which is then passed to the Job
        @return: None
        """

        return_self = False

        # Create a TimeTrigger for the Job
        trigger = TimeTrigger(every=every, at=at,
                              delay=delay,
                              exactly_at=exactly_at)

        if not (recipient := recipient):
            recipient = schedule.schedule_default_catcher
            return_self = True

        job = Job(func=functools.partial(func, **kwargs),
                  is_async=inspect.iscoroutinefunction(func),
                  trigger=trigger,
                  recipient=recipient,
                  func_name=func.__name__,
                  return_self=return_self)

        # Map job in schedule and start it
        Logger.log(f"Scheduler created job {job}", level="info")
        schedule.name_job_map.add(job.func_name, job)
        schedule.id_job_map[job.native_id] = job

        # Start the job, or add it to unstarted for later starts
        if start_now:
            job.start()

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
    def start_job(name: str) -> bool:
        """
        Start the scheudling of a given method,
        if a Job with the name is found
        @param name: Name of the job to start (may start multiple)
        @return: bool, jobs were or were not started
        """
        return bool([job.start() for job in list(schedule.get_jobs(name))])

