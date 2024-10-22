from datetime import datetime
from triggenger.message_manager.message import Message


# Test Message initialization with all parameters
def test_message_initialization_all_params():
    sender = "John Doe"
    subject = "Meeting Reminder"
    body = "Don't forget about the meeting tomorrow at 10 AM."
    source = "email"
    date = datetime(2023, 10, 21, 14, 30, 0)  # Fixed date for testing

    message = Message(sender, subject, body, source, date)

    assert message.sender == sender
    assert message.subject == subject
    assert message.body == body
    assert message.source == source
    assert message.date == date


# Test Message initialization with default source and date
def test_message_initialization_defaults():
    sender = "Jane Doe"
    subject = "Hello!"
    body = "Just wanted to say hi."

    # Don't pass source and date to test defaults
    message = Message(sender, subject, body)

    assert message.sender == sender
    assert message.subject == subject
    assert message.body == body
    assert message.source == "unknown"

    # Check that the default date is set to the current time (within a small time window)
    assert (datetime.now() - message.date).total_seconds() < 1  # Test for current date default


# Test the display method
def test_message_display():
    sender = "John Doe"
    subject = "Important Update"
    body = "Here is the latest update on the project."
    source = "slack"
    date = datetime(2023, 10, 21, 14, 30, 0)  # Fixed date for testing

    message = Message(sender, subject, body, source, date)

    expected_output = (
        "Message Details:\n"
        "----------------\n"
        "From: John Doe\n"
        "Source: slack\n"
        "Date: 2023-10-21 14:30:00\n"
        "Subject: Important Update\n"
        "----------------\n"
        "Body:\nHere is the latest update on the project."
    )

    assert message.display() == expected_output
