
"""
Details:
    2020-07-05
    
    pytman framework PollCache source file

Module details:
    
    The PollCache object is developed to be a 
    man-in-the-middle object for making repeated
    calls to functions or API's and only getting
    a repsonse back when the return changed from
    the most recent one.
"""


class PollCache:
    """
    This object is designed to act as a cushion between a 
    function or other callable, and its caller, and only 
    give returns when new data from the function is identified.

    This way you can pass functions to an instance of this class
    and loop indefinitely, where only new results will be returned.

    The PollCache object will treat every function and its 
    constellation of arguments and keyword arguments as unique,
    meaning that you can use the same function or other callable
    with different parameters in a loop, and it will not be 
    overwritten in the PollCache just because the function is 
    the same, but will be treated as its own cache.

    This class uses the __call__ method as its main interface.
    Call the instance of this class as you would a function.

    The syntax is simply: 

    >>    cache = PollCache()
    >>    cache(function_name, parameter1 = val, parameter2 = val2, ...)


    :silent_first_call:
        Boolean. Set it to True if the desired behavior is to
        build up a cache, and only start returning values if 
        any of the cached method returns deviate.
        Default is that all initial calls with a new function
        or a past function with new arguments, will return 
        values. Suppress this with this parameter.
    
    ---- Example with default behavior--------------------------------------
    
    >>    cache = PollCache()
    >>    cache(function, a = 1, b = 2)   #  Will produce a return value
    >>    cache(function, a = 1, b = 2)   #  Will NOT produce a return value (identical output)
    >>    cache(function, a = 10, b = 20) #  Will produce a return value (new output)

    ----- Example with silent first call -----------------------------------
    
    >>    cache = PollCache(silent_first_call = True)
    >>    cache(function, a = 1, b = 2)   #  Will NOT produce a return value
    >>    cache(function, a = 1, b = 2)   #  Will NOT produce a return value (identical output)
    >>    cache(function, a = 10, b = 20) #  Will produce a return value (new output)
    """
    
    def __init__(self, silent_first_call = False):
        self.cached_polls = dict()
        self.silent_first_call = silent_first_call

    def __call__(self, func: 'function', *args, **kwargs):
        try:
            new_result = func(*args, **kwargs)
        except:
            raise

        if not func in self.cached_polls.keys():            
            self.cached_polls[func] = [
                {'args': args,
                 'kwargs': kwargs,
                 'result': new_result,
                 'calls': 1}]
            
            return new_result if not self.silent_first_call else None

        for call in self.cached_polls[func]:
            if call['args'] == args and call['kwargs'] == kwargs and call['result'] != new_result:
                call['result'] = new_result
                call['calls'] += 1
                return new_result
                
        if not [i for i in self.cached_polls[func] if i['args'] == args and i['kwargs'] == kwargs]:
            self.cached_polls[func].append({
                'args': args, 
                'kwargs': kwargs, 
                'result': new_result, 
                'calls': 1})
            
            return new_result if not self.silent_first_call else None

