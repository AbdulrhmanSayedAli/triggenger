from typing import Callable
from triggenger.message_manager.message import Message

# Type alias for the perform callable used in actions
ActionPerformCallable = Callable[
    [
        Message,  # A Message object that contains information like sender, source, date, etc.
        dict,  # A dict of key value extracted parameters, each represented as a string.
    ],
    None,  # The callable does not return any value (returns None).
]
