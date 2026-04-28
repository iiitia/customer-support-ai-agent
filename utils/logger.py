import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Configure root logger for the application.
    Call once at startup (e.g. in main.py or evaluator.py).
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)  # silence Groq SDK noise
    logging.getLogger("httpcore").setLevel(logging.WARNING)
