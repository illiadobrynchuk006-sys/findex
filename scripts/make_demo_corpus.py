"""Create a deterministic local corpus for testing/benchmarking without committing data."""

from __future__ import annotations

import argparse
from pathlib import Path

PARAGRAPHS = [
    "Python generators produce values lazily and keep pipelines memory efficient.\n",
    "Ітератори дозволяють обробляти український текст без завантаження всього корпусу.\n",
    "Unicode normalization makes café and cafe\u0301 compare consistently.\n",
    "A search engine counts tokens, vocabulary terms, documents, and frequencies.\n",
    "Don't materialize a stream unless you really need the whole collection.\n",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default="data", type=Path)
    parser.add_argument("--documents", type=int, default=1000)
    parser.add_argument("--repeat", type=int, default=80)
    args = parser.parse_args()

    args.root.mkdir(parents=True, exist_ok=True)
    for i in range(args.documents):
        text = "".join(PARAGRAPHS[(i + j) % len(PARAGRAPHS)] for j in range(args.repeat))
        (args.root / f"doc-{i:04d}.txt").write_text(text, encoding="utf-8")
    print(f"Created {args.documents} documents in {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
