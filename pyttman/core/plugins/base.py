import enum

from pyttman.core.containers import MessageMixin


class PyttmanPluginIntercept(enum.StrEnum):
    """
    Enum for the different intercepts available for
    Pyttman plugins to hook into. The intercepts are
    called at different stages of the application
    runtime, allowing for custom workflows to be
    implemented.
    """
    before_app_start = "before_app_start"
    after_app_stops = "after_app_stops"
    before_router = "before_router"
    before_intent = "before_intent"
    after_intent = "after_intent"
    before_entity_extraction = "before_entity_extraction"
    after_entity_extraction = "after_entity_extraction"
    no_intent_match = "no_intent_match"

class PyttmanPlugin:
    """
    The PluginBase class offers an API for contributors to
    develop custom workflows which interact with different
    parts of a Pyttman application runtime.

    Implement methods as desired to interact with the
    various layers.

    The instance is long-lived throughout the application runtime.

    To control when the plugin is allowed to run, provide a list
    of allowed intercepts in the constructor. If no intercepts are
    provided, the plugin will never run.

    allowed_intercepts: list[PyttmanPluginIntercepts]
        A list of allowed points of intercept, where the plugin is allowed
        to intercept the application runtime. An empty list will allow
        no intercepts, effectively disabling the plugin.
    """
    def __init__(self,
                 allowed_intercepts: list[PyttmanPluginIntercept] or None = None,
                 app = None):
        self.allowed_intercepts = set(allowed_intercepts) if allowed_intercepts else set()
        self.app = app

    def on_app_start(self):
        """
        Execute code when the app starts, with the 'app' object available.
        """
        pass


    def allowed_to_intercept_at(self, intercept: PyttmanPluginIntercept):
        """
        Check if the plugin is allowed to run for the given intercept.
        """
        return intercept in self.allowed_intercepts

    def before_app_start(self, app):
        """
        Implement this method to have code execute before the app
        starts.
        """
        return app

    def after_app_stops(self, app):
        """
        Implement this method to have code execute when the
        app has exited
        """
        return app

    def before_router(self, message: MessageMixin):
        """
        Implement this method to interact with the processing
        of a message, before it's processed by the Router.
        This hook is useful to manipulate the message object
        before it's passed to the Router, affecting which
        intent it will match.
        """
        return message

    def before_intent(self, message: MessageMixin):
        """
        Implement this method to interact with the processing
        of a message, before it's processed by the matching Intent.
        """
        return message

    def after_intent(self, reply: MessageMixin):
        """
        Implement this method to interact with the Reply object
        from an Intent, before it's delivered to the Client for
        a platform response.
        """
        return reply

    def before_entity_extraction(self, message: MessageMixin):
        """
        Implement this method to interact with the processing
        of a message, before entities are parsed from the message.
        This is one way to affect the entities that are extracted
        from the message, when it's been passed to the matching intent.
        """
        return message

    def after_entity_extraction(self, message: MessageMixin):
        """
        This hook allows you to interfere with the message object
        (with associated entities on message.entities), to manipulate
        or change any entities extracted from the message before
        it's passed to the Intent.
        """
        return message

    def no_intent_match(self, message: MessageMixin):
        """
        Implement this method to interact with the message
        when no intent matches the message.
        """
        return message
