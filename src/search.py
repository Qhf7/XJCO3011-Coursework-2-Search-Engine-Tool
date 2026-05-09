from __future__ import annotations

from indexer import InvertedIndex, SearchHit, tokenize


class SearchService:
    def __init__(self, index: InvertedIndex) -> None:
        self.index = index

    def format_print(self, term: str) -> str:
        tokens = tokenize(term)
        if not tokens:
            return "No word provided."
        if len(tokens) != 1:
            return "Print expects exactly one word."

        token = tokens[0]
        postings = self.index.get_postings(token)
        if not postings:
            return f"No entries for '{token}'."

        lines = [f"Index for '{token}':"]
        for url, stats in sorted(postings.items(), key=lambda item: item[1]["order"]):
            lines.append(
                f"- {url} | freq={stats['frequency']} | positions={stats['positions']}"
            )
        return "\n".join(lines)

    def format_find(self, query: str) -> str:
        hits = self.index.find_pages(query)
        if not tokenize(query):
            return "No query provided."
        if not hits:
            return f"No pages found for '{query.strip()}'."

        lines = [f"Pages for '{query.strip()}':"]
        for hit in hits:
            lines.append(f"- {hit.url} | {hit.title} | matches={hit.frequency}")
        return "\n".join(lines)

    def find(self, query: str) -> list[SearchHit]:
        return self.index.find_pages(query)
