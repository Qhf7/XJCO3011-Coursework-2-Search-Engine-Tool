from __future__ import annotations

import sys
from pathlib import Path

from crawler import CrawlerError, QuotesCrawler
from indexer import InvertedIndex
from search import SearchService


DEFAULT_INDEX_PATH = Path("data/index.json")


class SearchApp:
    def __init__(
        self,
        index_path: str | Path = DEFAULT_INDEX_PATH,
        crawler_factory=QuotesCrawler,
    ) -> None:
        self.index_path = Path(index_path)
        self.crawler_factory = crawler_factory
        self.index = InvertedIndex()
        self.service = SearchService(self.index)
        self.running = True

    def execute(self, command_line: str) -> str:
        parts = command_line.strip().split(maxsplit=1)
        if not parts:
            return "Enter a command."

        command = parts[0].lower()
        argument = parts[1] if len(parts) > 1 else ""

        try:
            if command == "build":
                return self._build()
            if command == "load":
                return self._load()
            if command == "print":
                return self.service.format_print(argument)
            if command == "find":
                return self.service.format_find(argument)
            if command in {"quit", "exit"}:
                self.running = False
                return "Bye."
            if command == "help":
                return self._help()
            return f"Unknown command: {command}"
        except (CrawlerError, FileNotFoundError, OSError, ValueError) as exc:
            return f"Error: {exc}"

    def _build(self) -> str:
        crawler = self.crawler_factory()
        pages = crawler.crawl()
        self.index.build_from_pages(pages)
        self.index.save(self.index_path)
        return f"Built index for {len(pages)} pages and saved to {self.index_path}."

    def _load(self) -> str:
        self.index = InvertedIndex.load(self.index_path)
        self.service = SearchService(self.index)
        return f"Loaded index from {self.index_path}."

    def _help(self) -> str:
        return (
            "Commands: build, load, print <word>, find <terms>, help, quit\n"
            f"Index file: {self.index_path}"
        )

    def run(self) -> None:
        while self.running:
            try:
                line = input("search> ")
            except EOFError:
                break
            output = self.execute(line)
            if output:
                print(output)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    app = SearchApp()

    if args:
        print(app.execute(" ".join(args)))
        return 0

    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
