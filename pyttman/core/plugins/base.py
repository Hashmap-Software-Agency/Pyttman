from pyttman.core.containers import MessageMixin


class PyttmanPlugin:
    """
    The PluginBase class offers an API for contributors to
    develop custom workflows which interact with different
    parts of a Pyttman application runtime.

    Implement methods as desired to interact with the
    various layers.

    The instance is long-lived throughout the application runtime.
    """

    def before_app_start(self, app):
        """
        Implement this method to have code execute before the app
        starts.
        """
        pass

    def after_app_stops(self, app):
        """
        Implement this method to have code execute when the
        app has exited
        """

    def before_intent(self, message: MessageMixin):
        """
        Implement this method to interact with the processing
        of a message, before it's processed by the matching Intent.
        """
        pass

    def after_intent(self, reply: MessageMixin):
        """
        Implement this method to interact with the Reply object
        from an Intent, before it's delivered to the Client for
        a platform response.
        """
        pass
