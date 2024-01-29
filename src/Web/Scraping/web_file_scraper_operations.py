from os import environ
from pathlib import Path
from logging import getLogger
from asyncio import (to_thread as aio_thread)

from src.Web.Scraping.web_scraper_utils import WebScraperUtils, WebResponseType
from src.Error.web_scraping_error import WebScrapingError
from bs4 import BeautifulSoup
from re import (search as re_search,
                I as re_I)
from urllib.parse import urlparse, urljoin
from uuid import uuid4

LOGGER = getLogger()


class WebFileScraperOperations(WebScraperUtils):

    @staticmethod
    async def _on_scraping_file_contents_from_url(*,
                                                  base_url: str,
                                                  saved_path: Path,
                                                  file_ext: str,
                                                  scraping_deep: int,
                                                  is_save_page_html: bool,
                                                  page_search_patterns: str or None):

        try:
            default_scraping_deep = int(environ.get("DEFAULT_SCRAPING_DEEP"))

            html_content = await WebScraperUtils._get_content_from_url(url=base_url,
                                                                       response_type=WebResponseType.html)

            if not html_content:
                LOGGER.error(f"Not get html content from url - {base_url}")

            if is_save_page_html:
                await WebScraperUtils._save_content_to_file(content=html_content,
                                                            file_name_prefix=f"{scraping_deep}",
                                                            file_ext="html",
                                                            path=saved_path / "html")

            result = await WebFileScraperOperations._extract_links_from_html_content(html_content=html_content,
                                                                                     file_ext=file_ext,
                                                                                     base_url=base_url,
                                                                                     page_search_patterns=page_search_patterns)
            if not result:
                LOGGER.error(f"Not extract pages and files links from url - {base_url}")

            file_links, page_links = result

            if len(file_links) != 0:
                for link in file_links:
                    await WebFileScraperOperations._download_file_from_link(link=link,
                                                                            saved_path=saved_path,
                                                                            file_name_prefix=f"{scraping_deep}",
                                                                            file_ext=file_ext)

            if scraping_deep < default_scraping_deep:

                if len(page_links) != 0:
                    scraping_deep += 1

                    for link in page_links:
                        await WebFileScraperOperations._on_scraping_file_contents_from_url(base_url=link,
                                                                                           saved_path=saved_path,
                                                                                           file_ext=file_ext,
                                                                                           scraping_deep=scraping_deep,
                                                                                           is_save_page_html=is_save_page_html,
                                                                                           page_search_patterns=page_search_patterns)

        except (Exception, WebScrapingError) as error:
            LOGGER.error(error)

    @staticmethod
    async def _extract_links_from_html_content(*,
                                               html_content: str,
                                               file_ext: str,
                                               base_url: str,
                                               page_search_patterns: str or None) -> (list, list) or None:
        page_links = []
        file_links = []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            objs = await aio_thread(soup.find_all, href=True)

            for obj in objs:
                link = obj.get('href')

                if not link:
                    continue

                if re_search(f'\.{file_ext}(?:\?[^\/]*)?$', link, re_I):
                    file_links.append(link)

                elif not re_search(r'\.\w+(?:\?.*)?$', link, re_I) and (
                        all([re_search(pattern, link, re_I) for pattern in
                             page_search_patterns]) if page_search_patterns else True):
                    if link.startswith('/'):
                        page_links.append(urljoin(base_url, link))
                    elif urlparse(link).netloc == urlparse(base_url).netloc:
                        page_links.append(link)

        except Exception as error:
            LOGGER.error(error)
        finally:
            return file_links, page_links

    @staticmethod
    async def _download_file_from_link(*,
                                       link: str,
                                       saved_path: Path,
                                       file_name_prefix: str or None,
                                       file_ext: str):
        try:
            file_content = await WebScraperUtils._get_content_from_url(url=link,
                                                                       response_type=WebResponseType.file)

            if not file_content:
                raise WebScrapingError(f"Not content from url - {link}")

            await WebScraperUtils._save_content_to_file(content=file_content,
                                                        path=saved_path / file_ext,
                                                        file_name_prefix=file_name_prefix,
                                                        file_ext=file_ext,
                                                        encoding=None)

        except (Exception, WebScrapingError) as error:
            LOGGER.error(error)
