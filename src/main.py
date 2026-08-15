import logging

from src.core.config import APP_ENV, LOG_LEVEL
from src.core.logging_config import configure_logging


def main() -> None:
    configure_logging(LOG_LEVEL)

    logger = logging.getLogger(__name__)

    logger.info("Starting Enterprise Multi-Industry RAG")
    logger.info("Environment: %s", APP_ENV)


if __name__ == "__main__":
    main()