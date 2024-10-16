from typing import Union, Callable
from imapclient.response_parser import defaultdict, _ParseFetchResponseInnerDict
from triggenger.message_manager.message import Message


MessageData = Union[dict, defaultdict[int, _ParseFetchResponseInnerDict]]

OnEmailReceivedCallable = Callable[
    [
        Message,
        MessageData,
        int,
    ],
    None,
]
