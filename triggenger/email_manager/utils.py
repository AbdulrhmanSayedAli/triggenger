import logging
from imapclient import IMAPClient


def setup_logging() -> None:
    """Sets up the logging configuration for the application.

    Configures the logging module to output log messages to the console with
    a specified logging level and format. The log messages include the timestamp,
    log level, and the actual log message.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def clone_imap_client(client: IMAPClient) -> IMAPClient:
    """Creates a clone of an existing IMAPClient instance.

    This function copies the connection parameters from the provided IMAPClient
    instance to create a new, independent IMAPClient object.

    Args:
        client (IMAPClient): The IMAPClient instance to clone.

    Returns:
        IMAPClient: A new instance of IMAPClient with the same connection parameters.

    Raises:
        TypeError: If the provided client is not an instance of IMAPClient.
    """
    if not isinstance(client, IMAPClient):
        raise TypeError("Provided client must be an instance of IMAPClient.")

    return IMAPClient(
        host=client.host,
        port=client.port,
        use_uid=client.use_uid,
        ssl=client.ssl,
        stream=client.stream,
        ssl_context=client.ssl_context,
        timeout=client._timeout,
    )
