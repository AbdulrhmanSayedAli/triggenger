from typing import Callable
from triggenger.message_manager.message import Message

# Type alias for the perform callable used in actions
ActionPerformCallable = Callable[
    [
        Message,  # A Message object that contains information like sender, source, date, etc.
        list[str],  # A list of extracted parameters, each represented as a string.
    ],
    None,  # The callable does not return any value (returns None).
]
