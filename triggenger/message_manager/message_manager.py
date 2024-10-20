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
        system_message_template : dict
                A template for the system message, defining the purpose and instructions
                for the AI model.
    """

    system_message_template = {
        "purpose": (
            "Classify incoming messages, extract key parameters, and generate necessary text based on predefined "
            "message types."
        ),
        "instructions": [
            "You will receive a series of messages.",
            (
                "For each message, assign it to exactly one of the predefined message types. If a message could fit "
                "multiple types, choose the most relevant one."
            ),
            (
                "Extract the required parameters for the assigned message type, following the parameter format: "
                "(param_name: description of what to extract). If a parameter is not present in the message, leave its "
                "value as an empty string."
            ),
            (
                "If a parameter requires additional information to be meaningful or complete, generate a relevant "
                "text or value based on the context of the message."
            ),
            (
                'Respond in the following JSON format: {"type": "message type number", "params": {"param1": "value1", '
                '"param2": "value2", ...}}.'
            ),
            (
                "If the message does not fit any of the predefined types, assign it to type 0, with an empty 'params' "
                "object."
            ),
            (
                "Ensure that all responses are in valid JSON format. In case of unclear or incomplete messages, do "
                "your best to classify them and provide the most relevant information."
            ),
            (
                "If the message is too ambiguous or noisy to categorize, classify it as type 0 and explain why it's "
                "uncategorizable in a comment."
            ),
            'Here is an example of a response: {"type": "2", "params": {"param1": "example value", "param2": ""}}.',
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

    def generate_system_message(self) -> str:
        """
        Generates a system message for the AI model, incorporating the message types
        defined in the given Trigger.

        Returns:
        --------
        str
            A JSON string representation of the system message, including message types.
        """
        current_system_message = copy.deepcopy(self.system_message_template)
        current_system_message["message_types"] = self.trigger.displayActions()
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
            # Step 1: Generate a system message using AI handler
            system_message = self.generate_system_message()

            # Step 2: Categorize the message and clean the response string
            response_str = self.ai_handler.categorize_message(message, system_message)
            response_str = self._clean_response_str(response_str)

            # Step 3: Parse the response into JSON
            response = json.loads(response_str)
            message_type = int(response.get("type", -1))  # Default to -1 if type is missing

            if message_type == 0:
                # Trigger action if no match is found
                self.trigger.onMessageNotMatched(message)
            elif message_type > 0:
                # Execute the matched action with provided parameters
                action = self._get_action_by_type(message_type)
                params = response.get("params", {})
                self.trigger.onMessageMatched(message, action, params)
            else:
                raise ValueError(f"Unexpected message type: {message_type}")

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            self.trigger.onMessageError(message, f"JSON parsing error: {e}")
        except KeyError as e:
            # Handle missing keys in the response dictionary
            self.trigger.onMessageError(message, f"Missing key in response: {e}")
        except Exception as e:
            # Handle all other exceptions
            self.trigger.onMessageError(message, f"Error processing message: {e}")

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
