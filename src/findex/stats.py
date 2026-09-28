"""Single-pass statistics pipeline for the corpus."""

from __future__ import annotations

import argparse
import tracemalloc
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from time import perf_counter

from findex.corpus import Document, iter_documents
from findex.tokenize import tokenize


@dataclass(frozen=True, slots=True)
class CorpusStats:
    documents: int
    tokens: int
    vocabulary: int
    top_terms: list[tuple[str, int]]
    elapsed_seconds: float
    peak_bytes: int


def compute_stats(documents: Iterable[Document]) -> CorpusStats:
    """Consume documents once and compute corpus statistics."""
    counts: Counter[str] = Counter()
    document_count = 0
    token_count = 0

    tracemalloc.start()
    start = perf_counter()
    try:
        for doc in documents:
            document_count += 1
            for token in tokenize(doc.text):
                counts[token] += 1
                token_count += 1
        elapsed = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    return CorpusStats(
        documents=document_count,
        tokens=token_count,
        vocabulary=len(counts),
        top_terms=counts.most_common(50),
        elapsed_seconds=elapsed,
        peak_bytes=peak,
    )


def _format_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.2f} {unit}"
        amount /= 1024
    return f"{value} B"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute streaming corpus statistics")
    parser.add_argument("root", type=Path, help="Directory containing .txt files")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N documents")
    args = parser.parse_args(argv)

    documents = iter_documents(args.root)
    if args.limit is not None:
        if args.limit < 0:
            parser.error("--limit must be >= 0")
        documents = islice(documents, args.limit)

    stats = compute_stats(documents)

    print(f"Documents:       {stats.documents}")
    print(f"Tokens:          {stats.tokens}")
    print(f"Vocabulary size: {stats.vocabulary}")
    print(f"Elapsed:         {stats.elapsed_seconds:.4f} s")
    print(f"Peak memory:     {_format_bytes(stats.peak_bytes)}")
    print("Top terms:")
    for term, count in stats.top_terms:
        print(f"  {term:<24} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
