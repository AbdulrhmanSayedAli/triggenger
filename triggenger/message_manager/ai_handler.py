import openai
from triggenger.message_manager.message import Message
from abc import ABC, abstractmethod


class AIHandler(ABC):
    """
    Abstract base class for handling interactions with AI systems to categorize messages
    and extract parameters based on predefined message types.
    Subclasses must implement the `categorize_message` method.
    """

    @abstractmethod
    def categorize_message(self, message: Message, system_message: str) -> str:
        """
        Sends a message to the AI system for categorization and parameter extraction.

        Parameters:
        -----------
        message : Message
            The Message object to be categorized.
        system_message : str
            A system message that instructs the AI model on how to categorize the user message.

        Returns:
        --------
        str
            The AI's response containing the message type and extracted parameters in JSON format.

        Raises:
        -------
        Exception
            Raised if the AI system fails to process the request or returns an invalid result.
        """
        pass


class OpenAIHandler(AIHandler):
    """
    A concrete implementation of AIHandler that uses the OpenAI API to categorize messages.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initializes the OpenAIHandler with the given API key and sets up OpenAI API configuration.

        Parameters:
        -----------
        api_key : str
            The API key required to access the OpenAI API.
        model : str
            The GPT model to use when categorizing a message.
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    def categorize_message(self, message: Message, system_message: str) -> str:
        """
        Sends the given message to the OpenAI API for categorization and parameter extraction.

        Parameters:
        -----------
        message : Message
            The user Message object that needs to be categorized.
        system_message : str
            The system instruction that tells the AI model how to process and categorize the message.

        Returns:
        --------
        str
            The AI's response, which includes the message type and extracted parameters in JSON format.

        Raises:
        -------
        Exception
            Raised if the OpenAI API request fails, or if the response is not in the expected format.
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message.display()},
        ]

        try:
            response = openai.chat.completions.create(model=self.model, messages=messages, temperature=0.1)
            response_content = response.choices[0].message.content

            # Validate response format
            if isinstance(response_content, str):
                return response_content
            else:
                raise ValueError("Unexpected response format from OpenAI API.")
        except Exception as e:
            raise Exception(f"Error categorizing message: {e}")
