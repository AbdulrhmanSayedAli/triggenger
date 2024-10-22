from unittest.mock import Mock
from triggenger.message_manager.trigger import Trigger
from triggenger.message_manager.action import Action
from triggenger.message_manager.message import Message


# Test Trigger initialization and default handlers
def test_trigger_initialization_defaults():
    action1 = Mock(spec=Action)
    action2 = Mock(spec=Action)
    trigger = Trigger(actions=[action1, action2])

    # Check if the default handlers are set
    assert trigger.onMessageMatched == trigger._default_onMessageMatched
    assert trigger.onMessageNotMatched == trigger._default_onMessageNotMatched
    assert trigger.onMessageError == trigger._default_onMessageError


# Test Trigger initialization with custom handlers
def test_trigger_initialization_custom_handlers():
    action = Mock(spec=Action)
    custom_matched_handler = Mock()
    custom_not_matched_handler = Mock()
    custom_error_handler = Mock()

    trigger = Trigger(
        actions=[action],
        onMessageMatched=custom_matched_handler,
        onMessageNotMatched=custom_not_matched_handler,
        onMessageError=custom_error_handler,
    )

    # Check if the custom handlers are set
    assert trigger.onMessageMatched == custom_matched_handler
    assert trigger.onMessageNotMatched == custom_not_matched_handler
    assert trigger.onMessageError == custom_error_handler


# Test onMessageMatched with default handler
def test_trigger_default_onMessageMatched():
    action = Mock(spec=Action)
    action.perform = Mock()
    message = Mock(spec=Message)
    params = {"param1": "value1"}

    trigger = Trigger(actions=[action])
    trigger.onMessageMatched(message, action, params)

    # Check if the action's perform method was called with the correct parameters
    action.perform.assert_called_once_with(message, params)


# Test onMessageNotMatched with default handler
def test_trigger_default_onMessageNotMatched(capsys):
    message = Message(sender="test_sender", subject="test_subject", body="test_body")

    trigger = Trigger(actions=[])
    trigger.onMessageNotMatched(message)

    # Check if the appropriate message is printed when no match is found
    captured = capsys.readouterr()
    assert "No action matched for message from test_sender with subject: test_subject" in captured.out


# Test onMessageError with default handler
def test_trigger_default_onMessageError(capsys):
    message = Message(sender="test_sender", subject="test_subject", body="test_body")
    error = Exception("Test error")

    trigger = Trigger(actions=[])
    trigger.onMessageError(message, error)

    # Check if the error message is printed
    captured = capsys.readouterr()
    assert "Error processing message from test_sender: Test error" in captured.out


# Test displayActions method
def test_trigger_displayActions():
    action1 = Mock(spec=Action)
    action1.display.return_value = "Action 1: Description"

    action2 = Mock(spec=Action)
    action2.display.return_value = "Action 2: Description"

    trigger = Trigger(actions=[action1, action2])

    expected_output = "{TYPE:1. Action 1: Description},{TYPE:2. Action 2: Description},"
    assert trigger.displayActions() == expected_output


# Test action execution in the matched handler
def test_trigger_custom_onMessageMatched():
    action = Mock(spec=Action)
    message = Mock(spec=Message)
    params = {"param1": "value1"}

    custom_matched_handler = Mock()

    trigger = Trigger(actions=[action], onMessageMatched=custom_matched_handler)
    trigger.onMessageMatched(message, action, params)

    # Ensure the custom matched handler is called with the correct arguments
    custom_matched_handler.assert_called_once_with(message, action, params)
