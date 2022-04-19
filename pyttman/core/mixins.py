import pathlib


class PrettyReprMixin:
    """
    Mixin providing a common interface for
    __repr__ methods which represents classes
    in a very readable way.

    - How to use:
    Define which fields to include when printing the
    class or calling repr(some_object), by adding their
    names to the '__repr_fields__' tuple.

    This is just too handy!
    """
    __repr_fields__ = ()

    def __repr__(self):
        name = self.__class__.__name__
        attrs = [f"{i}={getattr(self, str(i))}" for i in self.__repr_fields__]
        return f"{name}({', '.join(attrs)})"


class PyttmanCliComplainerMixin:
    """
    Provides implementation classes a set of methods commonly
    used to complain to users when criteria aren't met
    """
    @staticmethod
    def complain_app_not_found(app_name: str | None) -> str | None:
        if app_name is None:
            return "Please provide a name for your app."
        if not pathlib.Path(app_name).exists():
            return f"- App '{app_name}' was not found here, " \
                   f"verify that a Pyttman app directory " \
                   f"named '{app_name}' exists."
