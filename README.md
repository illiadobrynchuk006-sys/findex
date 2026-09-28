# findex — Lab 01: Streams, Not Lists

Lab 01 for the Python search-engine course. The project streams a text corpus through a Unicode-aware tokenizer and computes corpus statistics without loading the whole corpus into memory.

## Requirements covered

- `src/` project layout.
- `data/` is excluded from Git.
- `iter_documents(root)` is a generator that opens one UTF-8 text file at a time.
- Invalid UTF-8/unreadable files are logged and skipped.
- `tokenize(text)` is a generator using NFC normalization, `casefold()`, and `re.finditer()`.
- `python -m findex.stats data/` reports documents, tokens, vocabulary size, top-50 terms, elapsed time, and peak traced memory.
- `--limit N` uses `itertools.islice`.
- `python -m findex.benchmark data/` compares eager list-based processing with the lazy generator pipeline.
- Tokenizer behavior is covered by pytest tests, including Cyrillic and combining-mark Unicode input.

## Corpus

The corpus itself is **not committed**. Put UTF-8 `.txt` files under `data/`.

For a quick reproducible corpus of 1,000 documents:

```bash
python scripts/make_demo_corpus.py data --documents 1000 --repeat 80
```

For the semester project, replace or extend this with a corpus you actually want to search (for example public-domain Project Gutenberg books). Keep the corpus under `data/`, which is already ignored by Git.

## Tokenizer policy

The tokenizer first applies `unicodedata.normalize("NFC", text)`, then `casefold()`.

- Unicode letters and digits are kept.
- `_` is treated as a separator.
- ASCII apostrophe (`'`) and typographic apostrophe (`’`) are kept **inside** words, so `don't`, `п'ять`, and `п’ять` stay single tokens.
- Hyphens split words, so `state-of-the-art` becomes `state`, `of`, `the`, `art`.
- Digits are kept, including alphanumeric tokens such as `python3`.

The regex is consumed with `re.finditer()`, so token matches are yielded lazily instead of being collected by `findall()`.

## Setup with `uv`

```bash
uv sync
```

Run checks:

```bash
uv run pytest
uv run ruff check .
```

## Run the lazy statistics pipeline

```bash
uv run python -m findex.stats data/
```

During development, process only the first N documents:

```bash
uv run python -m findex.stats data/ --limit 100
```

## Eager vs lazy benchmark

Run both implementations on the same corpus:

```bash
uv run python -m findex.benchmark data/
```

Benchmark performed in the prepared project environment on the generated 1,000-document demo corpus:

<!-- BENCHMARK_TABLE_START -->
| Version | Documents | Tokens | Vocabulary | Peak memory | Elapsed |
|---|---:|---:|---:|---:|---:|
| eager (lists) | 1000 | 768000 | 44 | 56.07 MiB | 1.6254 s |
| lazy (generators) | 1000 | 768000 | 44 | 0.30 MiB | 1.8950 s |
<!-- BENCHMARK_TABLE_END -->

The eager version stores the complete `Document` list and then a list of tokens for every document, so memory grows with the corpus and token count. The lazy version keeps only the current document, the current token/match state, and the `Counter`; therefore the corpus itself is not materialized. Its memory is not zero because one document string and the vocabulary counter still have to exist. Timings can vary between runs and machines, so rerun the benchmark before submission if your instructor expects numbers from your own computer.

## Why the pipeline is lazy

`iter_documents()` contains `yield`, therefore calling it creates a generator and does not read the corpus immediately. `tokenize()` also contains `yield`; work happens only when its consumer asks for the next token. The stats loop pulls one document and then one token at a time until the stream is exhausted.

Quick demonstration:

```python
import inspect
from findex.corpus import iter_documents
from findex.tokenize import tokenize

assert inspect.isgeneratorfunction(iter_documents)
assert inspect.isgeneratorfunction(tokenize)
```

## Git / GitHub submission

Create the repository and tag the finished lab:

```bash
git init
git add .
git commit -m "Lab 1: iterators and corpus pipeline"
git branch -M main
git tag lab-01
```

After creating an empty public GitHub repository, connect it and push:

```bash
git remote add origin https://github.com/YOUR-USERNAME/findex.git
git push -u origin main
git push origin lab-01
```

Do not commit `data/`.

## Reflection notes

1. `for x in xs` calls `iter(xs)` once and repeatedly calls `next()` until `StopIteration`. An iterable can create an iterator; an iterator holds traversal state. A generator object is an iterator.
2. A list can produce a fresh iterator every time. A generator is single-pass; to restart it, call the generator function again (or materialize its output, which removes the memory advantage).
3. At token 10,000 the lazy pipeline holds the current document text, the generator state/current regex match, loop variables, and the growing `Counter` of terms—not all corpus documents or all tokens.
4. Exceptions inside a generator body appear when the generator is consumed, because the body does not execute at generator creation time.
5. `casefold()` is stronger than `lower()` for caseless Unicode comparison (for example German `ß`); NFC makes canonically equivalent forms such as precomposed `é` and `e` + combining accent compare the same.
6. `re.findall()` builds a list of all matches for the document; `re.finditer()` yields matches one at a time, reducing temporary memory use.
7. The eager version spends memory on the full document list and token lists. The lazy version retains only one document at a time plus the result `Counter`.
