from pyttman import Feature, Callback, schedule


# noinspection PyMethodMayBeStatic
class SchedulingFeature(Feature):
    """
    A demo Feature to manipulate and view
    Pyttman's built in Schedule API
    """
    def configure(self):
        self.callbacks = (Callback(func=self.list_all_running_jobs,
                                   lead=("list", "running"),
                                   trail=("scheduled", "job", "jobs")),
                          Callback(func=self.kill_job,
                                   lead=("kill", "stop", "end")))

    def list_all_running_jobs(self, message):
        jobs = list(schedule.get_all_jobs())
        if jobs:
            return str(", ").join(jobs)
        return "There are no scheduled job at this time"

    def kill_job(self, message):
        job_name = message.content[-1]
        schedule.kill_job_gracefully(job_name=job_name)
        return f"'{job_name}' suspended."
