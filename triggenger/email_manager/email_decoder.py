import email
import logging
from triggenger.message_manager.message import Message
from triggenger.email_manager.types import MessageData


def decode_email(msg_data: MessageData, msg_id: int) -> Message:
    """Decodes an email message from the raw IMAP response.

    This function extracts the envelope, date, and content of an email from the
    IMAP response and converts it into a `Message` object, specifically fetching
    the plain text body.

    Args:
        msg_data (dict | defaultdict[int, _ParseFetchResponseInnerDict]):
            The raw message data fetched from the IMAP server.
        msg_id (int):
            The unique ID of the message to decode.

    Returns:
        Message:
            A `Message` object containing the sender, subject, body, date, and source
            of the email.

    Raises:
        KeyError:
            If required message data fields like 'ENVELOPE', 'INTERNALDATE',
            or 'BODY[]' are missing.
        ValueError:
            If the email content cannot be decoded properly.
    """
    try:
        # Extract the envelope and date from the message data
        envelope = msg_data[msg_id][b"ENVELOPE"]
        date = msg_data[msg_id][b"INTERNALDATE"]

        logging.info(f"Fetched email with Subject: {envelope.subject.decode()}")

        # Extract and parse the raw email content from the BODY[]
        raw_email = msg_data[msg_id][b"BODY[]"]
        parsed_email = email.message_from_bytes(raw_email)

    except KeyError as e:
        logging.error(f"Missing expected email field: {e}")
        raise KeyError(f"Required field {e} is missing in the email data.")

    # Try to decode the plain text part of the email
    plain_text = None
    if parsed_email.is_multipart():
        # Iterate through each part of the email to find text/plain content
        for part in parsed_email.walk():
            if part.get_content_type() == "text/plain":
                try:
                    plain_text = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                    break
                except (UnicodeDecodeError, AttributeError) as e:
                    logging.warning(f"Failed to decode email part: {e}")
    else:
        # If the email is not multipart, it may be a plain text email
        if parsed_email.get_content_type() == "text/plain":
            try:
                plain_text = parsed_email.get_payload(decode=True).decode(parsed_email.get_content_charset() or "utf-8")
            except (UnicodeDecodeError, AttributeError) as e:
                logging.warning(f"Failed to decode email body: {e}")

    # If plain text is still None, assign a default value
    if plain_text is None:
        logging.warning("No plain text body found in email.")
        plain_text = ""

    # Construct the sender's email address from the envelope
    sender = f"{envelope.from_[0].mailbox.decode()}@{envelope.from_[0].host.decode()}"

    subject = envelope.subject.decode()

    # Create a Message object with the decoded information
    message = Message(
        sender=sender,
        subject=subject,
        body=plain_text,
        source="email",
        date=date,
    )

    logging.info(f"Email from {sender} with subject '{subject}' decoded successfully.")
    return message
