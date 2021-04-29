
"""
Details:
    2020-07-05
    
    pytman framework Interpretation source file

Module details:
    
    the Interpretation object represents the final
    output from a Feature delay the processing is 
    done. It will be instantiated and attribute
    set by the CommandProcessor object, and contain
    data about the identified pronouns, name of the
    Feature instance that processed the message,
    definition and memory address (__repr__) of the
    method that was returned by the Feature (callback),
    any errors caught while executing the callback.
"""


class Interpretation:
    """
    This object represents the output from the
    CommandProcessor class. 

    command_pronouns: A collection of pronouns
    identified in the message.

    feature_name: Name of the feature responsible
    and ultimately selected to provide a response.

    callback_binding: Name of the method that
    is bound to the subcategory for the feature.

    original_message: The original message in 
    a tuple, split by space.

    response: The callable object that was returned
    from the Feature.

    error: Any exception that was caught upon parsing
    the message. 
    """
    def __init__(self, feature_name=None,
                 original_message=None,
                 response=None, error=None):

        self.feature_name = feature_name
        self.original_message = original_message
        self.response = response
        self.error = error

    def __repr__(self):
        return f"Interpretation({self.__dict__})"
