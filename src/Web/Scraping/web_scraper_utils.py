from logging import getLogger
from asyncio import (to_thread as aio_thread)
from typing import Any
from enum import Enum
from src.Error.web_scraping_error import WebScrapingError

from validators import url as validate_url
from aiofiles import open as aio_open
from pathlib import Path
from uuid import uuid4
from cloudscraper import create_scraper
from fake_useragent import UserAgent


LOGGER = getLogger()


class WebResponseType(Enum):
    html = 0
    file = 1


class WebScraperUtils:

    @staticmethod
    def _check_url_is_valid(*, url: str) -> bool:

        result = False

        try:
            result = validate_url(url)

        except Exception as error:
            LOGGER.error(error)

        finally:
            return result

    @staticmethod
    async def _read_content_from_file(*, path: Path, encoding: str or None = 'utf-8') -> bytes or str:
        result = None

        try:
            async with aio_open(path, 'r' if encoding else 'rb', encoding=encoding) as file:
                result = await file.read()
        except Exception as error:
            LOGGER.error(error)
        finally:
            return result

    @staticmethod
    async def _save_content_to_file(*,
                                    content: str or bytes,
                                    path: Path,
                                    file_name_prefix: str or None = None,
                                    file_ext: str,
                                    encoding: str or None = 'utf-8') -> None:

        try:
            await aio_thread(path.mkdir, parents=True, exist_ok=True)

            random_uid = str(uuid4()).lower()

            file_name = f"{ file_name_prefix }_{ random_uid }"if file_name_prefix else random_uid

            async with aio_open(path / f"{ file_name }.{ file_ext }", mode='w' if encoding else 'wb',
                                encoding=encoding) as f:
                await f.write(content)

        except Exception as error:
            LOGGER.error(error)

    @staticmethod
    async def _get_content_from_url(*, url: str, response_type: WebResponseType) -> Any:
        result = None

        try:
            scraper = create_scraper()

            response = await aio_thread(scraper.get, url, headers={'User-agent': UserAgent().random})

            if response.status_code == 200:
                if response_type == WebResponseType.html:
                    result = response.text
                elif response_type == WebResponseType.file:
                    result = response.content
            else:
                raise WebScrapingError(f"Not success request to url - {url} with response - {response}")

        except (Exception, WebScrapingError) as error:
            LOGGER.error(error)
        finally:
            return result
