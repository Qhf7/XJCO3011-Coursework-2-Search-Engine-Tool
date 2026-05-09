# XJCO3011 Coursework 2

Search engine tool for `quotes.toscrape.com`.

## Features

- `build` crawls the site and saves an inverted index
- `load` loads a saved index
- `print <word>` shows the postings list for one word
- `find <terms>` returns pages containing all query terms
- Search is case-insensitive
- The index stores document metadata, term frequency, and token positions
- The crawler respects a 6-second politeness window between successive requests

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python src/main.py
```

If your shell points `python3` to a broken system interpreter, use `python` from your active conda environment instead.

Example commands:

```text
build
load
print nonsense
find good friends
quit
```

You can also run one command directly:

```bash
python src/main.py build
python src/main.py find good friends
```

## Architecture

- `src/crawler.py`: crawls the paginated quote site and extracts visible page text
- `src/indexer.py`: tokenizes text and builds the inverted index
- `src/search.py`: formats `print` and `find` query results
- `src/main.py`: command-line shell and command dispatch

## Index Structure

The compiled index contains:

- `documents`: metadata for each crawled page, including title, URL, order, and token count
- `index`: postings for each token, including frequency and token positions per page

Multi-word search uses AND semantics, so a page is only returned if it contains every query term.

## Error Handling

- Request failures are wrapped as crawler errors
- Empty queries and unknown words return friendly messages
- `print` requires exactly one word
- `load` reports an error if the index file does not exist

## Tests

```bash
pytest
```

The tests cover:

- crawling the next-page chain
- politeness-window enforcement
- request-error handling
- case normalization
- index save/load round-tripping
- single-word and multi-word search
- CLI command behavior and edge cases

## Output file

The compiled index is saved to `data/index.json`.

## Notes

- The crawler indexes the visible text of each page so the index reflects the page content rather than only quote blocks.
- The video submission must include a critical evaluation of any GenAI tools used.
