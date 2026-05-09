from __future__ import annotations

from crawler import CrawledPage
from indexer import InvertedIndex, tokenize


def test_tokenize_normalises_case() -> None:
    assert tokenize("Good, GOOD friends!") == ["good", "good", "friends"]


def test_indexer_builds_frequencies_and_positions(tmp_path) -> None:
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

    postings = index.get_postings("good")
    assert postings["https://quotes.toscrape.com/"]["frequency"] == 2
    assert postings["https://quotes.toscrape.com/"]["positions"] == [0, 3]

    out = tmp_path / "index.json"
    index.save(out)
    loaded = InvertedIndex.load(out)

    assert loaded.get_postings("good")["https://quotes.toscrape.com/page/2/"]["frequency"] == 1
    assert loaded.documents["https://quotes.toscrape.com/page/2/"]["title"] == "Page 2"


def test_get_postings_is_case_insensitive() -> None:
    page = CrawledPage(
        url="https://quotes.toscrape.com/",
        title="Page 1",
        content="Good friends are good.",
        order=0,
    )

    index = InvertedIndex()
    index.add_page(page)

    assert index.get_postings("GOOD") == index.get_postings("good")
