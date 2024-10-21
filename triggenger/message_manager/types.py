from typing import Callable
from triggenger.message_manager.message import Message
from triggenger.message_manager.action import Action

# Type alias for the perform callable used in actions
ActionPerformCallable = Callable[
    [
        Message,  # A Message object that contains information like sender, source, date, etc.
        dict,  # A dictionary of key-value pairs representing parameters extracted from the message.
        # The keys are parameter names (usually strings) and the values can be various types
        # depending on the action requirements.
    ],
    None,  # The callable does not return any value (returns None).
]
"""
ActionPerformCallable represents the type signature for the `perform` method in an Action.
It accepts a `Message` object and a dictionary of extracted parameters and performs an action.
This callable does not return any value.
"""

onMessageMatchedCallable = Callable[
    [
        Message,  # The Message object that matched the criteria for triggering the action.
        Action,  # The Action object that is triggered when the message matches.
        dict,  # A dictionary of parameters extracted from the message, passed to the Action.
    ],
    None,  # The callable does not return any value (returns None).
]
"""
onMessageMatchedCallable represents the type signature for the callback function invoked when
a message matches the criteria for a specific action. It receives a `Message` object, the 
`Action` object that matched, and a dictionary of extracted parameters. This callback allows 
custom handling of the matched message.
"""

onMessageNotMatchedCallable = Callable[
    [
        Message,  # The Message object that did not match any action's criteria.
    ],
    None,  # The callable does not return any value (returns None).
]
"""
onMessageNotMatchedCallable represents the type signature for the callback function invoked when 
a message does not match any action criteria. It receives the `Message` object that failed to 
match any trigger condition. This callback allows for custom handling of unmatched messages.
"""

onMessageErrorCallable = Callable[
    [
        Message,  # The Message object that was being processed when the error occurred.
        Exception,  # The Exception object representing the error that occurred during message processing.
    ],
    None,  # The callable does not return any value (returns None).
]
"""
onMessageErrorCallable represents the type signature for the callback function invoked when an error
occurs during the processing of a message. It receives the `Message` object and the `Exception` object
that caused the error. This callback allows for custom error handling during message processing.
"""
