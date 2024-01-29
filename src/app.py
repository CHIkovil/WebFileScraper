from asyncio import run as aio_run
from src.Web.Scraping.web_file_scraper import WebFileScraper
from pathlib import Path
from logging import getLogger
from urllib.parse import urlparse


LOGGER = getLogger()



if __name__ == "__main__":
    try:
        aio_run(on_script())
    except Exception as error:
        LOGGER.error(error)
