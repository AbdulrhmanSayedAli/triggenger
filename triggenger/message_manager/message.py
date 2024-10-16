from datetime import datetime
from typing import Optional


class Message:
    def __init__(
        self,
        sender: str,
        subject: str,
        body: str,
        source: Optional[str],
        date: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a new message instance.

        :param sender: The sender of the message (required).
        :param subject: The subject of the message (required).
        :param body: The body content of the message (required).
        :param source: The source from which the message was received (optional).
        :param date: The date the message was sent (optional). Defaults to now if not provided.
        """
        self.sender = sender
        self.subject = subject
        self.body = body
        self.source = source
        self.date = date if date else datetime.now()  # Default to current date if not provided

    def display(self) -> str:
        """Display the message content."""
        return (
            f"From: {self.sender}\n"
            f"Source: {self.source}\n"
            f"Date: {self.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Subject: {self.subject}\n\n"
            f"{self.body}"
        )

    def __str__(self) -> str:
        """String representation of the message."""
        return f"Message from {self.sender} with subject: {self.subject}"

    def __repr__(self) -> str:
        """Official string representation of the message."""
        return f"Message(sender={self.sender}, source={self.source}, " f"date={self.date}, subject={self.subject})"
