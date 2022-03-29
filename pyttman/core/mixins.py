class PrettyReprMixin:
    """
    Mixin providing a common interface for
    __repr__ methods which represents classes
    in a very readable way.

    - How to use:
    Define which fields to include when printing the
    class or calling repr(some_object), by adding their
    names to the 'repr_fields' tuple.
    """
    __repr_fields__ = ()

    def __repr__(self):
        name = self.__class__.__name__
        attrs = [f"{i}={getattr(self, str(i))}" for i in self.__repr_fields__]
        return f"{name}({', '.join(attrs)})"
