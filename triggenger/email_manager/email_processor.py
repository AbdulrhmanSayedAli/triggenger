import threading
from imapclient import IMAPClient
import queue
import logging
from typing import List
from triggenger.email_manager.email_decoder import decode_email
from triggenger.email_manager.types import OnEmailReceivedCallable


class EmailProcessor(threading.Thread):
    """A class that processes emails fetched from an IMAP server in a separate thread.

    Attributes:
        client (IMAPClient): The IMAP client for connecting to the email server.
        username (str): The username for email authentication.
        password (str): The password for email authentication.
        mailbox (str): The mailbox to fetch emails from.
        task_queue (queue.Queue): A queue that holds email fetch tasks.
        _stop_event (threading.Event): An event to signal when the thread should stop.
        on_email_received_callback (OnEmailReceivedCallable): A callback function invoked when a new email is received.
    """

    def __init__(
        self,
        client: IMAPClient,
        username: str,
        password: str,
        mailbox: str,
        task_queue: queue.Queue,
        on_email_received_callback: OnEmailReceivedCallable,
    ):
        """Initializes the EmailProcessor instance.

        Args:
            client (IMAPClient): The IMAP client used for connecting to the email server.
            username (str): The username for email authentication.
            password (str): The password for email authentication.
            mailbox (str): The mailbox to fetch emails from.
            task_queue (queue.Queue): A queue that holds email fetch tasks.
        """
        super().__init__()
        self.client = client
        self.username = username
        self.password = password
        self.mailbox = mailbox
        self.task_queue = task_queue
        self.on_email_received_callback = on_email_received_callback
        self._stop_event = threading.Event()

    def fetch_emails(self, new_email_orders: List[int]) -> None:
        """Fetches and processes emails based on the provided email order indices.

        This method selects the specified mailbox, fetches message IDs, and retrieves
        the content of emails based on the indices provided in the `new_email_orders`.
        It then decodes and processes each email.

        Args:
            new_email_orders (List[int]):
                A list of indices representing the email orders to fetch. Indices are
                1-based (1 is the first email).

        Raises:
            ValueError: If no emails are found in the mailbox or if the mailbox is not selected.
            Exception: Catches and logs any other errors during the email fetching process.
        """
        try:
            # Select the mailbox (raises an exception if the mailbox doesn't exist)
            logging.info(f"Selecting mailbox: {self.mailbox}")
            self.client.select_folder(self.mailbox)

            # Search for all message IDs in the selected mailbox
            msg_ids = self.client.search()
            if not msg_ids:
                raise ValueError(f"No emails found in mailbox '{self.mailbox}'.")

            logging.info(f"Found {len(msg_ids)} emails in '{self.mailbox}'.")

            # Process the email orders
            for email_order in new_email_orders:
                # Validate email order indices
                if email_order <= 0 or email_order > len(msg_ids):
                    logging.warning(f"Invalid email order index: {email_order}. Skipping.")
                    continue  # Skip invalid indices

                msg_id = msg_ids[email_order - 1]

                try:
                    # Fetch the envelope, date, and full content of the email
                    msg_data = self.client.fetch([msg_id], ["ENVELOPE", "INTERNALDATE", "BODY[]"])

                    if msg_data is None or msg_id not in msg_data:
                        logging.error(f"Failed to fetch email data for message ID: {msg_id}")
                        continue

                    # Decode and call the on_email_received_callback
                    message = decode_email(msg_data, msg_id)
                    self.on_email_received_callback(message, msg_data, msg_id)

                except Exception as email_fetch_error:
                    logging.error(f"Error fetching or decoding email (ID: {msg_id}): {email_fetch_error}")

        except ValueError as ve:
            logging.error(ve)
        except Exception as e:
            logging.error(f"An error occurred during the email fetching process: {e}")

    def stop(self):
        """Signals the thread to stop and adds a sentinel value to the task queue."""
        self._stop_event.set()  # Set the stop event
        self.task_queue.put([-1])  # Add a sentinel value to signal stop

    def run(self):
        """Runs the thread, processing email tasks from the task queue."""
        try:
            self.client.login(self.username, self.password)
            self.client.select_folder(self.mailbox)

            while not self._stop_event.is_set():
                # Wait for tasks to be available in the queue
                new_email_orders = self.task_queue.get()

                if new_email_orders and new_email_orders[0] == -1:
                    logging.info("Received stop signal, exiting processing loop.")
                    break

                logging.info(f"Processing email orders: {new_email_orders}")
                self.fetch_emails(new_email_orders)
                self.task_queue.task_done()
        except Exception as e:
            logging.error(f"Error during processing: {e}")
        finally:
            self.client.logout()
            logging.info("Logged out from the IMAP server.")
