# XJCO3011 Coursework 2

This project is a Python command-line search engine for `quotes.toscrape.com`.
Its purpose is to demonstrate the core stages of a simple search engine workflow:

- crawling the pages of a target website
- extracting visible text content from each page
- building an inverted index with term statistics
- saving and loading the compiled index from disk
- retrieving pages for single-word and multi-word queries

The coursework focuses on web crawling, inverted indexing, query processing, testing, and command-line interaction.

## Video Demonstration

Coursework demonstration video:

https://youtu.be/X_50nlo5Q3g

## Features

- `build` crawls the site and saves an inverted index
- `load` loads a saved index
- `print <word>` shows the postings list for one word
- `find <terms>` returns pages containing all query terms
- Search is case-insensitive
- The index stores document metadata, term frequency, and token positions
- The crawler respects a 6-second politeness window between successive requests

## Requirements

- Python `3.12` or later is recommended
- Internet access is required for the `build` command because it crawls `quotes.toscrape.com`
- The compiled index is stored in `data/index.json`

## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/Qhf7/XJCO3011-Coursework-2-Search-Engine-Tool.git
cd XJCO3011-Coursework-2-Search-Engine-Tool
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Confirm the required packages are available:

- `requests`
- `beautifulsoup4`
- `pytest`

These are listed in [`requirements.txt`](/Users/qiaohongfei/Desktop/Web/cw2/requirements.txt).

## Running the Application

Start the command-line interface with:

```bash
python src/main.py
```

If your shell points `python3` to a broken system interpreter, use `python` from your active conda environment instead.

After the shell starts, you can enter commands interactively.

## Usage Examples for All Four Commands

### 1. `build`

Use `build` to crawl the target website and create the inverted index.

```text
search> build
```

What it does:

- visits all reachable pages on `quotes.toscrape.com`
- waits at least 6 seconds between successive requests
- extracts visible page text
- creates the inverted index
- saves the compiled result to `data/index.json`

### 2. `load`

Use `load` to reload a previously saved index from disk.

```text
search> load
```

What it does:

- reads `data/index.json`
- restores the index into memory
- allows searching without running the crawler again

### 3. `print <word>`

Use `print` to inspect the inverted index entry for exactly one word.

```text
search> print nonsense
```

What it returns:

- the pages where the word appears
- the term frequency in each page
- the token positions stored for that word

### 4. `find <terms>`

Use `find` to retrieve pages that contain a search query.

Single-word example:

```text
search> find indifference
```

Multi-word example:

```text
search> find good friends
```

What it does:

- tokenizes the query
- normalizes it to lowercase
- applies AND semantics for multi-word queries
- returns only pages that contain every query term

## Complete Interactive Example

The following example shows a typical end-to-end session:

```text
search> build
Fetching http://quotes.toscrape.com/ ...
...
Built index for 10 pages and saved to data/index.json.

search> load
Loaded index from data/index.json.

search> print nonsense
Index for 'nonsense':
- http://quotes.toscrape.com/page/2/ | freq=1 | positions=[...]
- http://quotes.toscrape.com/page/7/ | freq=1 | positions=[...]

search> find good friends
Pages for 'good friends':
- http://quotes.toscrape.com/ | Quotes to Scrape | matches=...

search> quit
Bye.
```

You can also run one command directly without entering interactive mode:

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

## Testing Instructions

Run the automated test suite with:

```bash
pytest
```

What the tests cover:

- crawling the next-page chain
- politeness-window enforcement
- request-error handling
- case normalization
- index save/load round-tripping
- single-word and multi-word search
- CLI command behavior and edge cases

The test files are:

- `tests/test_crawler.py`
- `tests/test_indexer.py`
- `tests/test_search.py`

These tests are designed to confirm both normal behaviour and common failure scenarios.

## Output file

The compiled index is saved to `data/index.json`.

## Notes

- The crawler indexes the visible text of each page so the index reflects the page content rather than only quote blocks.
- The video submission must include a critical evaluation of any GenAI tools used.
