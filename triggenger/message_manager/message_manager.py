from triggenger.message_manager.trigger import Trigger
from triggenger.message_manager.message import Message
from triggenger.message_manager.ai_handler import AIHandler
import json
import copy


class MessageManager:
    """
    Handles incoming messages by categorizing them using an AI handler
    and invoking the appropriate trigger actions based on the response.

    Attributes:
        trigger (Trigger): The trigger instance that defines actions and responses.
        ai_handler (AIHandler): The AI handler responsible for generating system messages
                                and categorizing the message content.
        system_message_categorize_template : dict
                A template for the system message, defining the purpose and instructions
                for the AI model to categorize the given message.
        system_message_categorize_template : dict
                A template for the system message, defining the purpose and instructions
                for the AI model to categorize the given message.
        system_message_perform_template : dict
                A template for the system message, defining the purpose and instructions
                for the AI model to perform a task on the given message.
    """

    system_message_categorize_template = {
        "purpose": "Classify incoming messages based on predefined message types.",
        "instructions": [
            "You will receive a series of messages.",
            (
                "For each message, assign it to exactly one of the predefined message types. If a message could fit "
                "multiple types, choose the most relevant one."
            ),
            'Respond in the following JSON format: {"type": "message type number"}.',
            (
                "If the message is too ambiguous or noisy to categorize or does not fit any of the predefined types, "
                "assign it to type 0"
            ),
            (
                "Ensure that all responses are in valid JSON format. In case of unclear or incomplete messages, do "
                "your best to classify them."
            ),
            ("Don't write any comments in the response only return the json response."),
            'Here is an example of a response: {"type": "2"}.',
        ],
    }

    system_message_perform_template = {
        "purpose": "Extract parameters and generate text based on a predefined message type.",
        "instructions": [
            "You will receive a user message that aligns with a specific, predefined message type.",
            "Perform the task specified by the message type on the received message.",
            (
                "After completing the task, extract, generate, or incorporate the task results into the parameters "
                "defined by the message type."
            ),
            (
                "Identify and extract the required parameters for the given message type, following this format: "
                "(param_name: description of the parameter to be extracted or generated). If a parameter is absent in "
                "the message, leave its value as an empty string."
            ),
            (
                "For parameters needing additional context to be meaningful, generate relevant text or values "
                "based on the message’s context."
            ),
            'Return the response in this JSON format: {"params": {"param1": "value1", "param2": "value2", ...}}.',
            "Do not include any comments or additional text in the response, only the JSON output.",
            'Example response: {"params": {"param1": "example value", "param2": ""}}.',
        ],
    }

    def __init__(self, trigger: Trigger, ai_handler: AIHandler):
        """
        Initializes the MessageManager with a trigger and an AI handler.

        Args:
            trigger (Trigger): An instance of Trigger class that defines the actions.
            ai_handler (AIHandler): An AI handler responsible for message categorization.
        """
        self.trigger = trigger
        self.ai_handler = ai_handler

    def generate_system_categorize_message(self) -> str:
        """
        Generates a system message for the AI model, incorporating the message types
        defined in the given Trigger.

        Returns:
        --------
        str
            A JSON string representation of the system message, including message types.
        """
        current_system_message = copy.deepcopy(self.system_message_categorize_template)
        current_system_message["message_types"] = self.trigger.displayActions()
        return json.dumps(current_system_message)

    def generate_system_perform_message(self) -> str:
        """
        Generates a system message for the AI model, to perform the required task on this message.

        Returns:
        --------
        str
            A JSON string representation of the system message.
        """
        current_system_message = copy.deepcopy(self.system_message_perform_template)
        return json.dumps(current_system_message)

    def process_message(self, message: Message):
        """
        Processes an incoming message by generating a system message, categorizing it,
        and executing the appropriate action or handling errors.

        Args:
            message (Message): The incoming message to be processed.

        Raises:
            ValueError: If the response cannot be parsed or if required fields are missing.
        """
        try:
            categorize_system_message = self.generate_system_categorize_message()
            response = self._send_request(message.display(), categorize_system_message)
            message_type = int(response["type"])

            if message_type == 0:
                # Trigger action if no match is found
                self.trigger.onMessageNotMatched(message)
            elif message_type > 0:
                # Execute the matched action with provided parameters
                perform_system_message = self.generate_system_perform_message()
                action = self._get_action_by_type(message_type)
                response = self._send_request(
                    f"Message Type\n:{action.display_with_task()}\n Message:\n{message.display()}",
                    perform_system_message,
                )
                params = response.get("params", {})
                self.trigger.onMessageMatched(message, action, params)
            else:
                raise ValueError(f"Unexpected message type: {message_type}")

        except json.JSONDecodeError as e:
            self.trigger.onMessageError(message, f"JSON parsing error: {e}")
        except KeyError as e:
            self.trigger.onMessageError(message, f"Missing key in response: {e}")
        except Exception as e:
            self.trigger.onMessageError(message, f"Error processing message: {e}")

    def _send_request(self, message: str, system_message: str):
        response_str = self.ai_handler.send_message(message, system_message)
        response_str = self._clean_response_str(response_str)
        return json.loads(response_str)

    def _clean_response_str(self, response_str: str) -> str:
        """
        Cleans the response string by removing formatting characters like backticks and code fences.

        Args:
            response_str (str): The raw response string from the AI handler.

        Returns:
            str: The cleaned response string.
        """
        return (
            response_str.removeprefix("```json")
            .removeprefix("```")
            .removeprefix("`")
            .removesuffix("```")
            .removesuffix("`")
        )

    def _get_action_by_type(self, message_type: int):
        """
        Retrieves the corresponding action based on the message type.

        Args:
            message_type (int): The type of the message, which maps to an action.

        Returns:
            action (callable): The action that corresponds to the message type.

        Raises:
            ValueError: If the message type does not match any available actions.
        """
        if 0 < message_type <= len(self.trigger.actions):
            return self.trigger.actions[message_type - 1]
        else:
            raise ValueError(f"Invalid action type: {message_type}")
