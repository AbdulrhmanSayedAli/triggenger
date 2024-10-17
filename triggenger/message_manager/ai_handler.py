import copy
import json
import openai
from triggenger.message_manager.trigger import Trigger
from triggenger.message_manager.message import Message


class AIHandler:
    """
    A class to handle interactions with the OpenAI API for categorizing messages
    and extracting parameters based on predefined message types.

    Attributes:
    -----------
    system_message_template : dict
        A template for the system message, defining the purpose and instructions
        for the AI model.
    api_key : str
        The API key for authenticating requests to the OpenAI API.
    """

    system_message_template = {
        "purpose": "Categorize incoming messages and extract parameters based on predefined message types and their descriptions.",
        "instructions": [
            "You will receive a series of messages.",
            "For each message, you will categorize it into one of the given message types.",
            "After categorizing, extract the corresponding parameters from the message and output them.",
            "Sometimes you will be asked to generate a response and add it as a param.",
            'When you categorize a message, reply in JSON format like this: {"type": "message type number", "params": "list of key value string params"}.',
            "If a message doesn't match any type, reply like it has a type equal to 0.",
        ],
    }

    def __init__(self, api_key: str):
        """
        Initializes the AIHandler with the given API key.

        Parameters:
        -----------
        api_key : str
            The API key for accessing the OpenAI API.
        """
        self.api_key = api_key
        openai.api_key = api_key

    def generate_system_message(self, trigger: Trigger) -> str:
        """
        Generates a system message for the AI model, incorporating the message types
        defined in the given Trigger.

        Parameters:
        -----------
        trigger : Trigger
            An instance of the Trigger class, used to retrieve the message types.

        Returns:
        --------
        str
            A JSON string representation of the system message, including message types.
        """
        current_system_message = copy.deepcopy(self.system_message_template)
        current_system_message["message_types"] = trigger.displayActions()
        return json.dumps(current_system_message)

    def categorize_message(self, message: Message, system_message: str) -> str:
        """
        Sends the message to the OpenAI API for categorization and parameter extraction.

        Parameters:
        -----------
        message : Message
            The Message object to be categorized.
        system_message : str
            The JSON-formatted system message instructing the AI model.

        Returns:
        --------
        str
            The AI's response containing the message type and extracted parameters in JSON format.

        Raises:
        -------
        Exception
            Raises an exception if the API request fails or returns an unexpected result.
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message.display()},
        ]

        try:
            response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
            response_content = response.choices[0].message.content

            # Validate response format
            if isinstance(response_content, str):
                return response_content
            else:
                raise ValueError("Unexpected response format from OpenAI API.")
        except Exception as e:
            raise Exception(f"Error categorizing message: {e}")
