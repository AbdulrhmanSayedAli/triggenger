import pytest
from unittest.mock import patch, Mock
from triggenger.message_manager.message import Message
from triggenger.message_manager.ai_handler import OpenAIHandler


# Mock Message object for testing
@pytest.fixture
def mock_message():
    message = Mock(spec=Message)
    message.display.return_value = "This is a test message"
    return message


# Test OpenAIHandler initialization
def test_openai_handler_initialization():
    handler = OpenAIHandler(api_key="test_api_key", model="gpt-4o-mini")

    assert handler.api_key == "test_api_key"
    assert handler.model == "gpt-4o-mini"


# Test OpenAIHandler categorize_message method with a successful response
@patch("openai.chat.completions.create")
def test_categorize_message_success(mock_openai_create, mock_message):
    # Mock the response from OpenAI API
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='{"message_type": "1", "params": {}}'))]
    mock_openai_create.return_value = mock_response

    handler = OpenAIHandler(api_key="test_api_key", model="gpt-4o-mini")
    system_message = "Categorize the following message."

    response = handler.categorize_message(mock_message, system_message)

    # Verify the call to OpenAI API
    mock_openai_create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": "This is a test message"},
        ],
        temperature=0.1,
    )

    # Check the returned response
    assert response == '{"message_type": "1", "params": {}}'


# Test OpenAIHandler categorize_message method with an error from OpenAI API
@patch("openai.chat.completions.create")
def test_categorize_message_api_error(mock_openai_create, mock_message):
    # Mock the API to raise an exception
    mock_openai_create.side_effect = Exception("OpenAI API error")

    handler = OpenAIHandler(api_key="test_api_key", model="gpt-4o-mini")
    system_message = "Categorize the following message."

    with pytest.raises(Exception) as exc_info:
        handler.categorize_message(mock_message, system_message)

    # Verify that the exception message is correct
    assert str(exc_info.value) == "Error categorizing message: OpenAI API error"


# Test OpenAIHandler categorize_message method with an unexpected response format
@patch("openai.chat.completions.create")
def test_categorize_message_unexpected_response(mock_openai_create, mock_message):
    # Mock the API response with an unexpected format
    mock_response = Mock(choices=[Mock(message=Mock(content=None))])
    mock_openai_create.return_value = mock_response

    handler = OpenAIHandler(api_key="test_api_key", model="gpt-4o-mini")
    system_message = "Some system message."

    print(mock_response.choices[0].message.content)

    with pytest.raises(Exception) as exc_info:
        handler.categorize_message(mock_message, system_message)

    # Verify that the exception message is correct
    assert str(exc_info.value) == "Error categorizing message: Unexpected response format from OpenAI API."
