from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class CrawlerError(RuntimeError):
    """Raised when the crawler cannot retrieve or parse a page."""


@dataclass(slots=True)
class CrawledPage:
    url: str
    title: str
    content: str
    order: int


class QuotesCrawler:
    """Crawl the paginated pages on quotes.toscrape.com."""

    def __init__(
        self,
        start_url: str = "http://quotes.toscrape.com/",
        politeness_window: float = 6.0,
        request_get: Callable[..., requests.Response] | None = None,
        sleep_fn: Callable[[float], None] = time.sleep,
        clock_fn: Callable[[], float] = time.monotonic,
        timeout: float = 30.0,
        max_pages: int | None = None,
        progress_fn: Callable[[str], None] | None = print,
    ) -> None:
        self.start_url = start_url
        self.politeness_window = politeness_window
        self.request_get = request_get
        self.sleep_fn = sleep_fn
        self.clock_fn = clock_fn
        self.timeout = timeout
        self.max_pages = max_pages
        self.progress_fn = progress_fn
        self._last_request_completed_at: float | None = None
        self._domain = urlparse(start_url).netloc
        if request_get is None:
            session = requests.Session()
            session.trust_env = False
            self.request_get = session.get
            self._session = session
        else:
            self.request_get = request_get
            self._session = None

    def crawl(self) -> list[CrawledPage]:
        pages: list[CrawledPage] = []
        visited: set[str] = set()
        next_url: str | None = self.start_url

        while next_url and next_url not in visited:
            if self.max_pages is not None and len(pages) >= self.max_pages:
                break

            visited.add(next_url)
            if self.progress_fn:
                self.progress_fn(f"Fetching {next_url} ...")
            html = self._fetch(next_url)
            soup = BeautifulSoup(html, "html.parser")
            pages.append(
                CrawledPage(
                    url=next_url,
                    title=self._extract_title(soup, next_url),
                    content=self._extract_content(soup),
                    order=len(pages),
                )
            )
            next_url = self._extract_next_url(soup, next_url)

        return pages

    def _fetch(self, url: str) -> str:
        self._wait_for_politeness()

        try:
            response = self.request_get(url, timeout=self.timeout)
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover - exercised by tests
            raise CrawlerError(f"Failed to fetch {url}: {exc}") from exc
        finally:
            self._last_request_completed_at = self.clock_fn()

        return response.text

    def _wait_for_politeness(self) -> None:
        if self._last_request_completed_at is None:
            return

        elapsed = self.clock_fn() - self._last_request_completed_at
        remaining = self.politeness_window - elapsed
        if remaining > 0:
            if self.progress_fn:
                self.progress_fn(f"Waiting {remaining:.1f}s to respect politeness window ...")
            self.sleep_fn(remaining)

    def _extract_title(self, soup: BeautifulSoup, fallback_url: str) -> str:
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            return title_tag.get_text(" ", strip=True)
        return fallback_url

    def _extract_content(self, soup: BeautifulSoup) -> str:
        sanitized = BeautifulSoup(str(soup), "html.parser")
        for element in sanitized.select("script, style, noscript"):
            element.decompose()
        return sanitized.get_text(" ", strip=True)

    def _extract_next_url(self, soup: BeautifulSoup, current_url: str) -> str | None:
        next_link = soup.select_one("li.next a")
        if not next_link or not next_link.get("href"):
            return None

        candidate = urljoin(current_url, next_link["href"])
        parsed = urlparse(candidate)
        if parsed.netloc and parsed.netloc != self._domain:
            return None
        return candidate
