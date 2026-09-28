from findex.tokenize import tokenize


def tokens(text: str) -> list[str]:
    return list(tokenize(text))


def test_mixed_case_casefolds() -> None:
    assert tokens("Python PYTHON PyThOn") == ["python", "python", "python"]


def test_cyrillic() -> None:
    assert tokens("Привіт СВІТ") == ["привіт", "світ"]


def test_combining_mark_is_nfc_normalized() -> None:
    assert tokens("cafe\u0301 CAFÉ") == ["café", "café"]


def test_punctuation_is_removed() -> None:
    assert tokens("hello, world! (python).") == ["hello", "world", "python"]


def test_empty_string() -> None:
    assert tokens("") == []


def test_apostrophes_inside_words_are_preserved() -> None:
    assert tokens("don't п'ять п’ять") == ["don't", "п'ять", "п’ять"]


def test_hyphens_split_words() -> None:
    assert tokens("state-of-the-art") == ["state", "of", "the", "art"]


def test_digits_are_kept_and_underscore_splits() -> None:
    assert tokens("Python3 room_101") == ["python3", "room", "101"]
