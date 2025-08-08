import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str = "app.log", level: int = logging.DEBUG):
    """
    Sets up a logger with the specified name, log file, and logging level.

    Args:
        name (str): Name of the logger.
        log_file (str): File to which logs will be written.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO, etc.).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:  # Avoid adding duplicate handlers
        # Log format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # File handler
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
