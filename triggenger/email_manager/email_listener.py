import logging
from imapclient import IMAPClient
import queue
from triggenger.email_manager.email_processor import EmailProcessor

# Constants for idle timeouts
IDLE_CHECK_TIMEOUT = 2  # Interval between checks for new emails in IDLE mode (seconds)
IDLE_COMMAND_TIMEOUT = 15 * 60  # Max uptime for a single IDLE command (seconds)


class EmailListener:
    """A class to listen for new emails using IMAP IDLE commands.

    Attributes:
        client (IMAPClient): The IMAP client for connecting to the email server.
        username (str): The email account username.
        password (str): The email account password.
        mailbox (str): The mailbox to listen to (e.g., 'INBOX').
        task_queue (queue.Queue): A queue for processing new emails.
        idle_uptime (int): The accumulated time spent in IDLE mode.
    """

    def __init__(
        self,
        client: IMAPClient,
        username: str,
        password: str,
        mailbox: str,
        task_queue: queue.Queue,
        email_processor: EmailProcessor,
    ):
        """Initializes the EmailListener with required parameters.

        Args:
            client (IMAPClient): An instance of IMAPClient.
            username (str): Username for the email account.
            password (str): Password for the email account.
            mailbox (str): Mailbox to listen to.
            task_queue (queue.Queue): Queue to store new emails.

        Raises:
            ValueError: If username, password, or mailbox are empty.
        """
        if not username or not password or not mailbox:
            raise ValueError("Username, password, and mailbox must not be empty.")

        self.client = client
        self.username = username
        self.password = password
        self.mailbox = mailbox
        self.task_queue = task_queue
        self.email_processor = email_processor
        self.idle_uptime = 0

    def process_responses(self, responses: list):
        """Processes responses from the IMAP server and queues new emails.

        Args:
            responses (list): List of responses from the IMAP server.
        """
        if not responses:
            logging.info("No new messages from IMAP server.")
            return

        logging.info("IMAP server sent: %s", responses)
        new_emails = [response[0] for response in responses if response[1].decode() == "EXISTS"]

        if new_emails:
            logging.info("New emails detected: %s", new_emails)
            self.task_queue.put(new_emails)

    def handle_idle(self):
        """Handles IDLE mode and processes responses."""
        try:
            responses = self.client.idle_check(timeout=IDLE_CHECK_TIMEOUT)
            self.idle_uptime += IDLE_CHECK_TIMEOUT
            self.process_responses(responses)

            # Renew the IDLE command if the timeout is reached
            if self.idle_uptime >= IDLE_COMMAND_TIMEOUT:
                self.renew_idle_command()
        except Exception as e:
            logging.error("Error during IDLE handling: %s", e)
            self.stop_client()

    def renew_idle_command(self):
        """Renews the IDLE command after reaching the timeout."""
        try:
            self.client.idle_done()
            self.client.idle()
            self.idle_uptime = 0
            logging.info("IDLE command renewed")
        except Exception as e:
            logging.error("Failed to renew IDLE command: %s", e)

    def stop_client(self):
        """Stops the IMAP client and logs out."""
        try:
            self.client.idle_done()
            logging.info("Exited IDLE mode")
        except Exception as e:
            logging.error("Error exiting IDLE mode: %s", e)
        finally:
            self.client.logout()
            self.email_processor.stop()
            logging.info("IMAP client logged out and email processor stopped.")

    def listen(self):
        """Main loop to listen for new emails."""

        try:
            self.client.login(self.username, self.password)
            self.client.select_folder(self.mailbox)
            self.client.idle()
            logging.info("Entered IDLE mode for mailbox: %s", self.mailbox)

            # Continuously check for responses while in IDLE mode
            while True:
                self.handle_idle()
        except (KeyboardInterrupt, SystemExit):
            logging.info("Shutting down due to user interruption.")
        except Exception as e:
            logging.error("Error in listen loop: %s", e)
        finally:
            self.stop_client()
