import abc


class BaseClient(abc.ABC):
    """
    Baseclass for Clients, for interfacing
    with users directly or through an API.
    """

    def __init__(self, router):
        self.router = router

    @abc.abstractmethod
    def run(self):
        pass
