from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from crawler import CrawledPage


TOKEN_RE = re.compile(r"[A-Za-z0-9']+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass(slots=True)
class SearchHit:
    url: str
    title: str
    order: int
    frequency: int
    positions: list[int]


class InvertedIndex:
    def __init__(self) -> None:
        self.documents: dict[str, dict[str, Any]] = {}
        self.index: dict[str, dict[str, dict[str, Any]]] = {}

    def build_from_pages(self, pages: list[CrawledPage]) -> None:
        self.documents.clear()
        self.index.clear()

        for page in pages:
            self.add_page(page)

    def add_page(self, page: CrawledPage) -> None:
        tokens = tokenize(page.content)
        self.documents[page.url] = {
            "url": page.url,
            "title": page.title,
            "order": page.order,
            "token_count": len(tokens),
        }

        for position, token in enumerate(tokens):
            postings = self.index.setdefault(token, {})
            entry = postings.setdefault(
                page.url,
                {
                    "url": page.url,
                    "title": page.title,
                    "order": page.order,
                    "frequency": 0,
                    "positions": [],
                },
            )
            entry["frequency"] += 1
            entry["positions"].append(position)

    def get_postings(self, term: str) -> dict[str, dict[str, Any]]:
        return self.index.get(term.lower(), {})

    def find_pages(self, query: str) -> list[SearchHit]:
        terms = list(dict.fromkeys(tokenize(query)))
        if not terms:
            return []

        matching_urls: set[str] | None = None
        for term in terms:
            term_urls = set(self.index.get(term, {}))
            matching_urls = term_urls if matching_urls is None else matching_urls & term_urls
            if not matching_urls:
                return []

        ordered_urls = sorted(
            matching_urls,
            key=lambda url: self.documents.get(url, {}).get("order", 0),
        )

        hits: list[SearchHit] = []
        for url in ordered_urls:
            stats = self.documents[url]
            token_stats = {
                term: self.index[term][url]
                for term in terms
                if term in self.index and url in self.index[term]
            }
            frequency = sum(entry["frequency"] for entry in token_stats.values())
            positions = sorted(
                {position for entry in token_stats.values() for position in entry["positions"]}
            )
            hits.append(
                SearchHit(
                    url=url,
                    title=stats["title"],
                    order=stats["order"],
                    frequency=frequency,
                    positions=positions,
                )
            )

        return hits

    def to_dict(self) -> dict[str, Any]:
        return {
            "documents": self.documents,
            "index": self.index,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InvertedIndex":
        instance = cls()
        instance.documents = dict(data.get("documents", {}))
        instance.index = dict(data.get("index", {}))
        return instance

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "InvertedIndex":
        source = Path(path)
        data = json.loads(source.read_text(encoding="utf-8"))
        return cls.from_dict(data)
