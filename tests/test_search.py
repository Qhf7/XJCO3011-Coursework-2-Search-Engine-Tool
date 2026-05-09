from __future__ import annotations

from crawler import CrawledPage
from indexer import InvertedIndex
from main import SearchApp
from search import SearchService


def build_sample_index() -> InvertedIndex:
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/",
            title="Page 1",
            content="Good friends are good.",
            order=0,
        ),
        CrawledPage(
            url="https://quotes.toscrape.com/page/2/",
            title="Page 2",
            content="Good day only.",
            order=1,
        ),
    ]
    index = InvertedIndex()
    index.build_from_pages(pages)
    return index


def test_print_formats_postings() -> None:
    service = SearchService(build_sample_index())
    output = service.format_print("good")

    assert "Index for 'good':" in output
    assert "freq=2" in output
    assert "page/2" in output


def test_print_rejects_multiple_words() -> None:
    service = SearchService(build_sample_index())
    output = service.format_print("good friends")

    assert output == "Print expects exactly one word."


def test_find_uses_and_semantics() -> None:
    service = SearchService(build_sample_index())
    hits = service.find("good friends")

    assert len(hits) == 1
    assert hits[0].url == "https://quotes.toscrape.com/"


def test_find_handles_empty_and_missing_queries() -> None:
    service = SearchService(build_sample_index())

    assert service.format_find("") == "No query provided."
    assert service.format_find("missingterm") == "No pages found for 'missingterm'."


def test_cli_build_and_load_with_injected_crawler(tmp_path) -> None:
    class FakeCrawler:
        def crawl(self):
            return [
                CrawledPage(
                    url="https://quotes.toscrape.com/",
                    title="Page 1",
                    content="Good friends are good.",
                    order=0,
                )
            ]

    app = SearchApp(index_path=tmp_path / "index.json", crawler_factory=FakeCrawler)
    build_output = app.execute("build")
    assert "Built index for 1 pages" in build_output

    app2 = SearchApp(index_path=tmp_path / "index.json", crawler_factory=FakeCrawler)
    load_output = app2.execute("load")
    assert "Loaded index" in load_output
    assert "Index for 'good':" in app2.execute("print good")
    assert "Pages for 'good friends':" in app2.execute("find good friends")


def test_cli_handles_empty_and_unknown_commands() -> None:
    app = SearchApp()

    assert app.execute("") == "Enter a command."
    assert app.execute("unknown") == "Unknown command: unknown"


def test_cli_load_reports_missing_file(tmp_path) -> None:
    app = SearchApp(index_path=tmp_path / "missing.json")

    output = app.execute("load")

    assert output.startswith("Error:")
