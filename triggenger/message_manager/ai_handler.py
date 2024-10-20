import openai
from triggenger.message_manager.message import Message


class AIHandler:
    """
    A class to handle interactions with the OpenAI API for categorizing messages
    and extracting parameters based on predefined message types.

    Attributes:
    -----------
    api_key : str
        The API key for authenticating requests to the OpenAI API.
    """

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
            response = openai.chat.completions.create(model="gpt-4o", messages=messages)
            response_content = response.choices[0].message.content

            # Validate response format
            if isinstance(response_content, str):
                return response_content
            else:
                raise ValueError("Unexpected response format from OpenAI API.")
        except Exception as e:
            raise Exception(f"Error categorizing message: {e}")
