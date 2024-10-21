from typing import List
from triggenger.message_manager.action import Action
from triggenger.message_manager.message import Message
from typing import Optional
from triggenger.message_manager.types import (
    onMessageErrorCallable,
    onMessageMatchedCallable,
    onMessageNotMatchedCallable,
)


class Trigger:
    """
    A class to manage the actions triggered by messages. The Trigger class processes
    messages and determines which actions to execute based on whether the message matches
    specific criteria or not.

    Attributes:
    -----------
    actions : list[Action]
        A list of actions to be performed when a message matches certain conditions.
    onMessageMatched : Optional[onMessageMatchedCallable]
        A callable to be executed when a message matches an action.
    onMessageNotMatched : Optional[onMessageNotMatchedCallable]
        A callable to be executed when a message does not match any action.
    onMessageError : Optional[onMessageErrorCallable]
        A callable to be executed when an error occurs during message processing.
    """

    def __init__(
        self,
        actions: List[Action],
        onMessageMatched: Optional[onMessageMatchedCallable] = None,
        onMessageNotMatched: Optional[onMessageNotMatchedCallable] = None,
        onMessageError: Optional[onMessageErrorCallable] = None,
    ):
        """
        Initializes the Trigger object with a list of actions and optional event handlers.

        Parameters:
        -----------
        actions : list[Action]
            A list of Action objects to be associated with this Trigger. Each Action
            contains a perform function to execute when triggered.
        onMessageMatched : Optional[onMessageMatchedCallable], optional
            A callable function that is invoked when a message matches a condition.
            If not provided, a default matching function is used.
        onMessageNotMatched : Optional[onMessageNotMatchedCallable], optional
            A callable function that is invoked when a message does not match any condition.
            If not provided, a default not-matched function is used.
        onMessageError : Optional[onMessageErrorCallable], optional
            A callable function that is invoked when an error occurs during message processing.
            If not provided, a default error handler is used.
        """
        self.actions = actions
        self.onMessageMatched = onMessageMatched or self._default_onMessageMatched
        self.onMessageNotMatched = onMessageNotMatched or self._default_onMessageNotMatched
        self.onMessageError = onMessageError or self._default_onMessageError

    @staticmethod
    def _default_onMessageMatched(message: Message, action: Action, params: dict) -> None:
        """
        Executes the specified action when a message matches the trigger's conditions.

        Parameters:
        -----------
        message : Message
            The Message object that contains information about the message that matched.
        action : Action
            The Action object to be performed when the message matches.
        params : dict
            A list of parameters extracted from the message that are used in the action.

        Returns:
        --------
        None
        """
        action.perform(message, params)

    @staticmethod
    def _default_onMessageNotMatched(message: Message) -> None:
        """
        Handles the scenario where a message does not match any conditions for triggering an action.

        Parameters:
        -----------
        message : Message
            The Message object that did not match any trigger condition.

        Returns:
        --------
        None
        """
        # This method can be extended to log the message or perform any required operations.
        print(f"No action matched for message from {message.sender} with subject: {message.subject}")

    @staticmethod
    def _default_onMessageError(message: Message, error: Exception) -> None:
        """
        Handles any errors that occur during the processing of a message.

        Parameters:
        -----------
        message : Message
            The Message object that caused the error.
        error : Exception
            The exception raised during message or action processing.

        Returns:
        --------
        None
        """
        # Implement custom error handling logic, such as logging the error details.
        print(f"Error processing message from {message.sender}: {error}")

    def displayActions(self) -> str:
        """
        Returns a structured string that represents the trigger actions details: title, description,
        and parameter descriptions in a format that's easy for AI systems to read.

        Returns:
        --------
        str
            A formatted string containing the action's details in a readable format.
        """
        details = ""

        for i, action in enumerate(self.actions, 1):
            details += "{" + f"TYPE:{i}. {action.display()}" + "},"

        return details.strip()
