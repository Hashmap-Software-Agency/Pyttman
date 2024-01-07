import traceback

import pyttman
from pyttman.core import exceptions
from pyttman.core.containers import Message
from pyttman.core.plugins.base import PyttmanPlugin

if __name__ != "__main__":
    try:
        import certifi
        import mongoengine
    except ImportError:
        message = (
            "\nMongoEnginePlugin: In order to use the Mongo Engine "
            "Plugin with Pyttman, you must install mongoengine and "
            "certifi.\n\n <pip install mongoengine, certifi>\n")
        print(message)
        exit(0)


class MongoEnginePlugin(PyttmanPlugin):
    """
    The MongoEnginePlugin offers a one-stop object for a
    Pyttman application to work with MongoEngine -
    a comprehensive ORM developed by the team at MongoDB.

    An application-wide connection is configured, making the use of
    mongoengine simple.

    When using this plugin, you can start develop Models and start
    using them in your application right away.

    If 'user_table_name' is provided, the 'message.author' object
    will be set as the matching User object in the mongodb database,
    matching the original author reference.

    In order to use this plugin, 'mongoengine' from pip, must be
    installed in the application.

    Tip! This plugin is accessible as `app.loaded_plugins.MongoEnginePlugin`
    in your application.
    """

    class MessageUserBinding:
        """
        Configure how the MongoEnginePlugin can prepare Message objects
        by setting a matching User as the `message.user` attribute (if any),
        on messages as they're routed to Intent classes.

        Provide the model class you use in your application for users,
        and which column to use when trying to identify a matching user
        based on the primary ID in the foreign user class*.

        * By foreign user*, we mean the message.author object which is
          different depending on which platform you are connecting your
          Pyttman app with. In Discord for example, it's an Author object.
          In this case, the Author.id property is used to try and match
          with your model.
        """
        user_model_class: type = None
        """ Define the Model class for Users in the application, i.e. MyUserModel """
        column_for_matching_user_to_author: str = None
        """ Define which column to match your user model with the 'Message.author' 
            object, i.e. "my_column_name"
        """
        custom_queryset_method_name: str = None
        """ Optionally, you can provide the name of a method on the QuerySet for 
            your model here which can return a matching User object provided a 
            message.author.id 
        """

        def __init__(self,
                     user_model_class: type = None,
                     column_for_matching_user_to_author: str = None,
                     custom_queryset_method_name: str = None):
            if user_model_class is None:
                raise exceptions.PyttmanPluginException(
                    "You must define your user model class in the user binding. "
                    "Example: `user_model_class=MyUserClass`")
            elif column_for_matching_user_to_author and custom_queryset_method_name:
                raise exceptions.PyttmanPluginException(
                    "You have defined an ambiguous configuration for user matching: "
                    "Both an attribute and a method is provided for matching. "
                    "Please choose either to define a column for direct matching "
                    "Author.id, or provide the name of a method in the QuerySet "
                    "for your model to call, when matching. ")

            self.user_model_class = user_model_class
            self.column_for_matching_user_to_author = column_for_matching_user_to_author
            self.custom_queryset_method_name = custom_queryset_method_name

    def __init__(self,
                 db_name: str,
                 host: str,
                 port: int | str,
                 user_binding: MessageUserBinding = None,
                 username: str = None,
                 password: str = None):
        self.user_binding = user_binding
        self.db_name = db_name
        self.host = host
        self.port = int(port)
        self._username = username
        self._password = password

    def before_app_start(self, app):
        """
        Set up a connection with MongoDB using mongoengine
        with provided credentials.
        """
        pyttman.logger.log("Mongoengine connecting...")
        mongoengine.connect(
            tlsCAFile=certifi.where(),
            db=self.db_name,
            host=self.host,
            username=self._username,
            password=self._password,
            port=self.port)
        del self._password
        del self._username

    def after_app_stops(self, app):
        pyttman.logger.log("Mongoengine disconnecting...")
        mongoengine.disconnect_all()

    def before_intent(self, message: Message):
        if self.user_binding is None:
            return
        model = self.user_binding.user_model_class

        try:
            if custom_method := self.user_binding.custom_queryset_method_name:
                method = getattr(model.objects, custom_method)
                user = method(message.author.id)
            else:
                local_column = self.user_binding.column_for_matching_user_to_author
                query = {f"{local_column}__exact": message.author.id}
                user = model.objects.get(**query)
        except Exception:
            pyttman.logger.log(
                level="error",
                message="MongoEnginePlugin was unable to perform user "
                        f"matching. Author: {message.author}, traceback: "
                        f"{traceback.format_exc()}")
            user = None
        message.user = user
