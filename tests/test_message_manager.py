import pytest
from unittest.mock import Mock, patch
from triggenger.message_manager.message import Message
from triggenger.message_manager.trigger import Trigger
from triggenger.message_manager.ai_handler import AIHandler
from triggenger.message_manager.message_manager import MessageManager


# Fixture to create a mock Trigger object
@pytest.fixture
def mock_trigger():
    trigger = Mock(spec=Trigger)
    trigger.displayActions.return_value = ["Action 1", "Action 2"]
    trigger.actions = [Mock(), Mock()]  # Mock actions
    trigger.onMessageMatched = Mock()
    trigger.onMessageNotMatched = Mock()
    trigger.onMessageError = Mock()
    return trigger


# Fixture to create a mock AIHandler object
@pytest.fixture
def mock_ai_handler():
    ai_handler = Mock(spec=AIHandler)
    return ai_handler


# Fixture to create a mock Message object
@pytest.fixture
def mock_message():
    return Mock(spec=Message)


# Test the system message generation
def test_generate_system_message(mock_trigger, mock_ai_handler):
    message_manager = MessageManager(mock_trigger, mock_ai_handler)

    system_message = message_manager.generate_system_message()

    expected_message = {
        "purpose": message_manager.system_message_template["purpose"],
        "instructions": message_manager.system_message_template["instructions"],
        "message_types": ["Action 1", "Action 2"],
    }

    # Convert expected message to JSON format to match the method output
    import json

    expected_system_message = json.dumps(expected_message)

    assert system_message == expected_system_message


# Test successful message processing with matched action
def test_process_message_matched(mock_trigger, mock_ai_handler, mock_message):
    message_manager = MessageManager(mock_trigger, mock_ai_handler)

    # Mock the AI handler to return a valid response
    mock_ai_handler.categorize_message.return_value = '{"type": "1", "params": {"param1": "value1"}}'

    # Call process_message
    message_manager.process_message(mock_message)

    # Check if onMessageMatched was called with correct parameters
    mock_trigger.onMessageMatched.assert_called_once_with(
        mock_message, mock_trigger.actions[0], {"param1": "value1"}  # Action corresponding to type 1
    )


# Test message processing when no message is matched (type 0)
def test_process_message_not_matched(mock_trigger, mock_ai_handler, mock_message):
    message_manager = MessageManager(mock_trigger, mock_ai_handler)

    # Mock the AI handler to return a type 0 response
    mock_ai_handler.categorize_message.return_value = '{"type": "0", "params": {}}'

    # Call process_message
    message_manager.process_message(mock_message)

    # Check if onMessageNotMatched was called
    mock_trigger.onMessageNotMatched.assert_called_once_with(mock_message)


# Test JSON parsing error in process_message
def test_process_message_json_error(mock_trigger, mock_ai_handler, mock_message):
    message_manager = MessageManager(mock_trigger, mock_ai_handler)

    # Mock the AI handler to return an invalid JSON
    mock_ai_handler.categorize_message.return_value = "invalid json"

    # Call process_message
    message_manager.process_message(mock_message)

    # Check if onMessageError was called due to JSON parsing error
    mock_trigger.onMessageError.assert_called_once_with(
        mock_message, "JSON parsing error: Expecting value: line 1 column 1 (char 0)"
    )


# Test unexpected message type in process_message
def test_process_message_unexpected_type(mock_trigger, mock_ai_handler, mock_message):
    message_manager = MessageManager(mock_trigger, mock_ai_handler)

    # Mock the AI handler to return a response with an unexpected type
    mock_ai_handler.categorize_message.return_value = '{"type": "-1", "params": {}}'

    # Call process_message
    message_manager.process_message(mock_message)

    # Check if onMessageError was called due to unexpected message type
    mock_trigger.onMessageError.assert_called_once_with(
        mock_message, "Error processing message: Unexpected message type: -1"
    )


# Test missing key error in process_message
def test_process_message_missing_key(mock_trigger, mock_ai_handler, mock_message):
    message_manager = MessageManager(mock_trigger, mock_ai_handler)

    # Mock the AI handler to return a response with a missing key
    mock_ai_handler.categorize_message.return_value = '{"params": {}}'  # 'type' key is missing

    # Call process_message
    message_manager.process_message(mock_message)

    # Check if onMessageError was called due to missing 'type' key
    mock_trigger.onMessageError.assert_called_once_with(mock_message, "Missing key in response: 'type'")
