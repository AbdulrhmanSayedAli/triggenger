from datetime import datetime
from typing import Optional


class Message:
    """
    A class representing a message with sender, source, date, subject, and body attributes.

    Attributes:
    -----------
    sender : str
        The sender of the message.
    source : str
        The source from which the message was received.
    date : datetime
        The date and time the message was sent.
    subject : str
        The subject of the message.
    body : str
        The main content of the message.
    """

    def __init__(
        self,
        sender: str,
        subject: str,
        body: str,
        source: Optional[str] = "unknown",
        date: Optional[datetime] = None,
    ) -> None:
        """
        Initializes the Message object.

        Parameters:
        -----------
        sender : str
            The sender of the message.
        source : str
            The source from which the message was received.
        date : datetime
            The date and time the message was sent.
        subject : str
            The subject of the message.
        body : str
            The main content of the message.
        """
        self.sender = sender
        self.subject = subject
        self.body = body
        self.source = source
        self.date = date if date else datetime.now()  # Default to current date if not provided

    def display(self) -> str:
        """
        Returns a structured string representing the message's content in a format
        that is easy to read and AI-friendly.

        Returns:
        --------
        str
            A formatted string with message details including sender, source, date,
            subject, and the body.
        """
        details = (
            f"Message Details:\n"
            f"----------------\n"
            f"From: {self.sender}\n"
            f"Source: {self.source}\n"
            f"Date: {self.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Subject: {self.subject}\n"
            f"----------------\n"
            f"Body:\n{self.body}\n"
        )
        return details.strip()

    def __str__(self) -> str:
        return f"Message from {self.sender} with subject: {self.subject}"

    def __repr__(self) -> str:
        return f"Message(sender={self.sender}, source={self.source}, " f"date={self.date}, subject={self.subject})"
