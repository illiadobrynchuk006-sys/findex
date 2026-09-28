"""Compare eager and lazy corpus processing on the same input."""

from __future__ import annotations

import argparse
import tracemalloc
from collections import Counter
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from time import perf_counter

from findex.corpus import Document, iter_documents
from findex.tokenize import tokenize


@dataclass(frozen=True, slots=True)
class BenchResult:
    version: str
    documents: int
    tokens: int
    vocabulary: int
    elapsed_seconds: float
    peak_bytes: int


def _measure(version: str, run) -> BenchResult:
    tracemalloc.start()
    start = perf_counter()
    try:
        documents, tokens, vocabulary = run()
        elapsed = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return BenchResult(version, documents, tokens, vocabulary, elapsed, peak)


def eager(root: Path, limit: int | None) -> BenchResult:
    def run() -> tuple[int, int, int]:
        docs_iter = iter_documents(root)
        if limit is not None:
            docs_iter = islice(docs_iter, limit)
        docs: list[Document] = list(docs_iter)
        token_lists = [list(tokenize(doc.text)) for doc in docs]
        counts = Counter(token for tokens in token_lists for token in tokens)
        return len(docs), sum(len(tokens) for tokens in token_lists), len(counts)

    return _measure("eager (lists)", run)


def lazy(root: Path, limit: int | None) -> BenchResult:
    def run() -> tuple[int, int, int]:
        docs_iter = iter_documents(root)
        if limit is not None:
            docs_iter = islice(docs_iter, limit)
        counts: Counter[str] = Counter()
        documents = 0
        tokens = 0
        for doc in docs_iter:
            documents += 1
            for token in tokenize(doc.text):
                counts[token] += 1
                tokens += 1
        return documents, tokens, len(counts)

    return _measure("lazy (generators)", run)


def _mib(value: int) -> float:
    return value / (1024 * 1024)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark eager vs lazy processing")
    parser.add_argument("root", type=Path)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be >= 0")

    results = [eager(args.root, args.limit), lazy(args.root, args.limit)]
    print("| Version | Documents | Tokens | Vocabulary | Peak memory | Elapsed |")
    print("|---|---:|---:|---:|---:|---:|")
    for result in results:
        print(
            f"| {result.version} | {result.documents} | {result.tokens} | "
            f"{result.vocabulary} | {_mib(result.peak_bytes):.2f} MiB | "
            f"{result.elapsed_seconds:.4f} s |"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
