from os import environ as os_environ
from src.Web.Scraping.web_file_scraper_operations import WebFileScraperOperations
from pathlib import Path
from logging import getLogger
from asyncio import to_thread as aio_thread

LOGGER = getLogger()


class WebFileScraper(WebFileScraperOperations):

    def __init__(self, *, url: str,
                 saved_path: Path,
                 file_ext: str,
                 is_save_page_html: bool,
                 scraping_deep: int = 0,
                 page_search_patterns: str or None = None):

        self._url = url
        self._saved_path = saved_path
        self._file_ext = file_ext
        self._is_save_page_html = is_save_page_html
        self._page_search_patterns = page_search_patterns

        os_environ["DEFAULT_SCRAPING_DEEP"] = f"{scraping_deep}"

    async def run(self):
        try:

            await aio_thread(self._saved_path.mkdir, parents=True, exist_ok=True)

            await self._on_scraping_file_contents_from_url(base_url=self._url,
                                                           saved_path=self._saved_path,
                                                           file_ext=self._file_ext,
                                                           scraping_deep=0,
                                                           is_save_page_html=self._is_save_page_html,
                                                           page_search_patterns=self._page_search_patterns)
        except Exception as error:
            LOGGER.error(error)

    def check_valid(self) -> bool:
        return self._check_url_is_valid(url=self._url)
