import logging
import os
from logging.handlers import RotatingFileHandler
import colorlog

def setup_root_logger(
    log_dir='./logs',
    log_file='app.log',
    max_bytes=10_000_00,
    backup_count=5,
    log_level='DEBUG',
    enable_file_logging=False
):
    """
    Configure the root logger with rotating file and colorful console handlers.
    This affects all logging calls without explicit logger names.
    """

    level = log_level or os.getenv('LOG_LEVEL', 'DEBUG').upper()
    numeric_level = getattr(logging, level, logging.INFO)

    logger = logging.getLogger()  # root logger
    logger.setLevel(numeric_level)

    # Clear existing handlers to avoid duplicates if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Setup file handler if enabled
    if enable_file_logging:
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create log directory {log_dir}: {e}")

        log_path = os.path.join(log_dir, log_file)
        file_handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Colorful console handler with message in white
    console_handler = colorlog.StreamHandler()

    # Format: color timestamp and levelname, but message is always white
    # console_formatter = colorlog.ColoredFormatter(
    #     "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(white)s%(message)s",
    #     datefmt='%Y-%m-%d %H:%M:%S',
    #     log_colors={
    #         'DEBUG':    'cyan',
    #         'INFO':     'green',
    #         'WARNING':  'yellow',
    #         'ERROR':    'red',
    #         'CRITICAL': 'bold_red',
    #     },
    #     secondary_log_colors={
    #         'message': {
    #             'DEBUG': 'white',
    #             'INFO': 'white',
    #             'WARNING': 'white',
    #             'ERROR': 'white',
    #             'CRITICAL': 'white',
    #         }
    #     },
    #     reset=True
    # )

    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s "
        "- %(filename)s:%(lineno)d - %(funcName)s() "
        "- %(message_log_color)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        secondary_log_colors={
            "message": {
                "DEBUG": "white",
                "INFO": "white",
                "WARNING": "white",
                "ERROR": "white",
                "CRITICAL": "white",
            }
        },
        reset=True,
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

