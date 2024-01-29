import logging
from os import environ

from dotenv import load_dotenv

LOGGER = logging.getLogger()

if not load_dotenv():
    LOGGER.error("Not found .env file")

