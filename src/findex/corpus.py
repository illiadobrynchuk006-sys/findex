"""Lazy document loading for plain-text corpora."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Document:
    """One text document from the corpus."""

    doc_id: str
    path: Path
    text: str


def iter_documents(root: Path) -> Iterator[Document]:
    """Yield UTF-8 ``.txt`` documents one at a time.

    ``root`` may be a single text file or a directory tree. Invalid UTF-8 files
    are logged and skipped so one bad document does not abort the full run.
    """
    root = Path(root)

    if root.is_file():
        paths = iter((root,))
        base = root.parent
    elif root.is_dir():
        paths = root.rglob("*.txt")
        base = root
    else:
        raise FileNotFoundError(f"Corpus path does not exist: {root}")

    for path in paths:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            logger.warning("Skipping non-UTF-8 file %s: %s", path, exc)
            continue
        except OSError as exc:
            logger.warning("Skipping unreadable file %s: %s", path, exc)
            continue

        try:
            doc_id = path.relative_to(base).as_posix()
        except ValueError:
            doc_id = path.name
        yield Document(doc_id=doc_id, path=path, text=text)
