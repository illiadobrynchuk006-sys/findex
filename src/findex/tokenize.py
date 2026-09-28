"""Unicode-aware streaming tokenization."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator

# Policy:
# - letters and digits are token characters (Unicode-aware through \w semantics)
# - underscores are excluded
# - ASCII apostrophe and typographic apostrophe are allowed only inside a token
# - hyphens split tokens
# Examples: "don't" -> "don't", "п’ять" -> "п’ять", "state-of-the-art" -> 4 tokens.
_TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", flags=re.UNICODE)


def tokenize(text: str) -> Iterator[str]:
    """Yield normalized, case-insensitive tokens lazily from ``text``."""
    normalized = unicodedata.normalize("NFC", text).casefold()
    for match in _TOKEN_RE.finditer(normalized):
        yield match.group(0)
