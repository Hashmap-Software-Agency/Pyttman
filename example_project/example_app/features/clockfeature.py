from datetime import datetime

from pytman import Feature, Callback


# noinspection PyMethodMayBeStatic
class ClockFeature(Feature):
    """
    A basic, simple feature which
    answers what time it is.
    """

    def configure(self):
        self.callbacks = Callback(func=self.get_time,
                                  lead="what", trail="time")

    def get_time(self, message):
        return f"the time is currently {datetime.now().strftime('%H:%M')}"
