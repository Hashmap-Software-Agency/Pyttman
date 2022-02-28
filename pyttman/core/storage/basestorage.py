"""
This module defines the base class for the Storage API
in Pyttman.
"""
import abc
from abc import ABC
from collections import UserDict
from typing import Any


class AbstractStorage(UserDict, abc.ABC):
    """
    Abstract storage class.
    Do not subclass this class for custom
    storage classes - subclass the 'Storage'
    class instead.
    """

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __contains__(self, item):
        pass

    @abc.abstractmethod
    def __getitem__(self, item):
        pass

    @abc.abstractmethod
    def put(self, key: Any, item: Any):
        pass

    @abc.abstractmethod
    def get(self, key) -> Any:
        pass

    @abc.abstractmethod
    def dump(self):
        pass

    @abc.abstractmethod
    def synchronize(self):
        pass


class BaseStorage(AbstractStorage, ABC):
    """
    Base Storage class for cache based storage in
    the Pyttman framework.

    The API implements the dictionary interface
    for ease of use, and also provides the 'put'
    method for semantic improvements.

    Subclasses can easily integrate a file or
    database storage backend by implementing
    the 'synchronize' method.
    """
    def __repr__(self):
        return f"{self.__class__.__name__}(keys={self.data.keys()})"

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, item):
        """
        Behaves just like dict.__getitem__.
        :param item: Any, key for requested object
        :return: Any
        :raises: KeyError if key not present in self.data
        """
        try:
            return self.data[item]
        except KeyError:
            raise KeyError("Pyttman.Storage: No item stored "
                           f"under key which matches '{item}'")

    def put(self, key: Any, item: Any):
        """
        Store an object in the Storage object, equivalent to
        `my_dict[key] = value"
        :param key: Any, key for the stored object
        :param item: Any, the actual object to store
        :return: None
        """
        self.data[key] = item

    def get(self, key) -> Any:
        """
        Get a stored object by provided key.
        This method does not raise an error
        like __getitem__ in dict, but behaves
        just like .get on dict objects.
        :param key: Any, key for requested object
        :return: Any
        """
        return self.data.get(key)


class Storage(BaseStorage):
    def dump(self):
        """
        Dump the storage to set backend type.
        Different backend types are available
        in storage.engines
        :return:
        """
        raise NotImplementedError("Dumping the Storage object is not "
                                  "implemented in this version of Pyttman, "
                                  "but will be available in a future release.")

    def synchronize(self):
        """
        Synchronize the storage object with set
        storage engine. In case of the SqlEngine,
        this would synchronize the Storage object
        with an SQL database.
        :return:
        """
        raise NotImplementedError("Synchronizing is not implemented "
                                  "in this version of Pyttman, but will "
                                  "be available in a future release.")
