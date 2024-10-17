import queue
from imapclient import IMAPClient
from triggenger.email_manager.email_listener import EmailListener
from triggenger.email_manager.email_processor import EmailProcessor
from triggenger.email_manager.utils import setup_logging, clone_imap_client
from triggenger.email_manager.types import OnEmailReceivedCallable, MessageData
from triggenger.message_manager.message import Message
from typing import Optional
import logging


class EmailManager:
    """
    Manages email operations such as listening for and processing emails.

    Args:
        username (str): The email account username.
        password (str): The email account password.
        mailbox (str): The mailbox to listen to (e.g., 'INBOX').
        host (str): IMAP server host.
        port (int): IMAP server port.
        ssl (bool): Whether to use SSL for the IMAP connection.
        on_email_received_callback (Optional[OnEmailReceivedCallable]):
            A callback function invoked when a new email is received.
    """

    def __init__(
        self,
        client: IMAPClient,
        username: str,
        password: str,
        mailbox: str,
        on_email_received_callback: Optional[OnEmailReceivedCallable] = None,
    ):
        """Initializes the EmailManager with IMAP server details and mailbox information."""
        self.username = username
        self.password = password
        self.mailbox = mailbox
        self.client = client
        self.task_queue = queue.Queue()
        self.on_email_received_callback = on_email_received_callback or self.default_email_callback

        self.email_processor = EmailProcessor(
            clone_imap_client(client),
            self.username,
            self.password,
            self.mailbox,
            self.task_queue,
            self.on_email_received_callback,
        )

        self.email_listener = EmailListener(
            clone_imap_client(client),
            username,
            password,
            mailbox,
            self.task_queue,
            email_processor=self.email_processor,
        )

        setup_logging()

    @staticmethod
    def default_email_callback(
        message: Message,
        msg_data: MessageData,
        msg_id: int,
    ):
        """Default callback if none is provided, simply logs the received email."""
        print(f"New email received: {message.display()}")

    def start(self):
        """Starts the email listener and processor."""

        logging.info("Starting email processing...")
        self.email_processor.start()

        logging.info("Starting email listening...")
        self.email_listener.listen()
