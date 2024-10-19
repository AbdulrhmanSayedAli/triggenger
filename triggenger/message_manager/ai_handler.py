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
        {
            "purpose": "Classify incoming messages, extract key parameters, and generate necessary text based on predefined message types.",
            "instructions": [
                "You will receive a series of messages.",
                "For each message, assign it to exactly one of the predefined message types. If a message could fit multiple types, choose the most relevant one.",
                "Extract the required parameters for the assigned message type, following the parameter format: (param_name: description of what to extract). If a parameter is not present in the message, leave its value as an empty string.",
                "If a parameter requires additional information to be meaningful or complete, generate a relevant text or value based on the context of the message.",
                'Respond in the following JSON format: {"type": "message type number", "params": {"param1": "value1", "param2": "value2", ...}}.',
                "If the message does not fit any of the predefined types, assign it to type 0, with an empty 'params' object.",
                "Ensure that all responses are in valid JSON format. In case of unclear or incomplete messages, do your best to classify them and provide the most relevant information.",
                "If the message is too ambiguous or noisy to categorize, classify it as type 0 and explain why it's uncategorizable in a comment.",
                'Here is an example of a response: {"type": "2", "params": {"param1": "example value", "param2": ""}}.',
            ],
        }
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
            response = openai.chat.completions.create(model="gpt-4", messages=messages)
            response_content = response.choices[0].message.content

            # Validate response format
            if isinstance(response_content, str):
                return response_content
            else:
                raise ValueError("Unexpected response format from OpenAI API.")
        except Exception as e:
            raise Exception(f"Error categorizing message: {e}")
