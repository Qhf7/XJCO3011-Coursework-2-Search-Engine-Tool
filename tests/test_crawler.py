from __future__ import annotations

from dataclasses import dataclass

import pytest

from crawler import CrawlerError, QuotesCrawler


HTML_PAGE_1 = """
<html>
  <head><title>Quotes to Scrape</title></head>
  <body>
    <nav>Top navigation</nav>
    <div class="quote">
      <span class="text">"Good friends are the family you choose."</span>
      <small class="author">Jess C. Scott</small>
      <div class="tags">
        <a class="tag">friends</a>
        <a class="tag">good</a>
      </div>
    </div>
    <li class="next"><a href="/page/2/">Next</a></li>
  </body>
</html>
"""

HTML_PAGE_2 = """
<html>
  <head><title>Quotes to Scrape - Page 2</title></head>
  <body>
    <div class="quote">
      <span class="text">"It is no use going back to yesterday."</span>
      <small class="author">Lewis Carroll</small>
      <div class="tags">
        <a class="tag">life</a>
      </div>
    </div>
  </body>
</html>
"""


@dataclass
class FakeResponse:
    text: str
    status_code: int = 200

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_crawler_follows_next_and_respects_politeness_window() -> None:
    responses = {
        "http://quotes.toscrape.com/": FakeResponse(HTML_PAGE_1),
        "http://quotes.toscrape.com/page/2/": FakeResponse(HTML_PAGE_2),
    }
    requested_urls: list[str] = []
    slept: list[float] = []
    current_time = [0.0]

    def fake_get(url: str, timeout: float = 0) -> FakeResponse:
        requested_urls.append(url)
        return responses[url]

    def fake_sleep(seconds: float) -> None:
        slept.append(seconds)
        current_time[0] += seconds

    def fake_clock() -> float:
        return current_time[0]

    crawler = QuotesCrawler(
        request_get=fake_get,
        sleep_fn=fake_sleep,
        clock_fn=fake_clock,
        politeness_window=6.0,
    )
    pages = crawler.crawl()

    assert requested_urls == [
        "http://quotes.toscrape.com/",
        "http://quotes.toscrape.com/page/2/",
    ]
    assert slept == [6.0]
    assert len(pages) == 2
    assert pages[0].title == "Quotes to Scrape"
    assert "Good friends" in pages[0].content
    assert "Top navigation" in pages[0].content
    assert pages[1].title == "Quotes to Scrape - Page 2"


def test_crawler_wraps_request_errors() -> None:
    def fake_get(url: str, timeout: float = 0) -> FakeResponse:
        raise Exception("boom")

    crawler = QuotesCrawler(request_get=fake_get)

    with pytest.raises(CrawlerError):
        crawler.crawl()
