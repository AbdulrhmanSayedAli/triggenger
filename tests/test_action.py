import pytest
from unittest.mock import Mock
from triggenger import Message, Action


# Mock Message object for testing
@pytest.fixture
def mock_message():
    return Mock(spec=Message)


# Mock perform function for testing
@pytest.fixture
def mock_perform_function():
    return Mock()


# Test Action initialization
def test_action_initialization(mock_perform_function):
    action = Action(
        title="Test Action",
        description="This is a test action.",
        task="do some task",
        params_description=["param1", "param2"],
        perform=mock_perform_function,
    )

    assert action.title == "Test Action"
    assert action.description == "This is a test action."
    assert action.task == "do some task"
    assert action.params_description == ["param1", "param2"]
    assert action.perform == mock_perform_function


# Test Action perform function call
def test_action_perform(mock_message, mock_perform_function):
    action = Action(
        title="Test Action",
        description="This is a test action.",
        task="do some task",
        params_description=["param1", "param2"],
        perform=mock_perform_function,
    )

    # Simulate calling the perform function
    action.perform(mock_message, {"param1": "value1", "param2": "value2"})

    # Verify that the perform function was called with the correct arguments
    mock_perform_function.assert_called_once_with(mock_message, {"param1": "value1", "param2": "value2"})


# Test Action display method
def test_action_display(mock_perform_function):
    action = Action(
        title="Test Action",
        description="This is a test action.",
        task="do some task",
        params_description=["param1", "param2"],
        perform=mock_perform_function,
    )

    expected_display = (
        "Title: Test Action\n"
        "Description of this message type: This is a test action.\n"
        "Parameter Descriptions to be extracted or generated:\n"
        "[param1,param2]"
    )

    assert action.display() == expected_display


# Test Action display_with_task method
def test_action_display_with_task(mock_perform_function):
    action = Action(
        title="Test Action",
        description="This is a test action.",
        task="do some task",
        params_description=["param1", "param2"],
        perform=mock_perform_function,
    )

    expected_display = (
        "Title: Test Action\n"
        "Description of this message type: This is a test action.\n"
        "Parameter Descriptions to be extracted or generated:\n"
        "[param1,param2]\n"
        "Required Task: do some task"
    )

    assert action.display_with_task() == expected_display
