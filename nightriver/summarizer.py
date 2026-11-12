"""One-sentence summary extractor for NightRiver.

No LLM required — extracts the first sentence from a feed item's
description/summary field using pure Python.
"""

import html
import re

_MAX_LEN = 280

# Matches HTML tags
_TAG_RE = re.compile(r"<[^>]+>")

# Matches runs of whitespace
_SPACE_RE = re.compile(r"\s+")

# Sentence-ending punctuation followed by whitespace or end-of-string
_SENTENCE_END_RE = re.compile(r"([.!?])\s+")


def strip_html(text: str) -> str:
    """Remove HTML tags and unescape HTML entities."""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _SPACE_RE.sub(" ", text).strip()
    return text


def first_sentence(text: str | None) -> str:
    """Return the first sentence of *text*, stripped of HTML.

    - Strips HTML tags and entities.
    - Returns the first sentence (terminated by . ! or ? + whitespace).
    - Truncates to 280 characters if needed.
    - Falls back to "(No summary available.)" for empty/None input.
    """
    if not text or not text.strip():
        return "(No summary available.)"

    clean = strip_html(text)
    if not clean:
        return "(No summary available.)"

    # Split at the first sentence boundary
    match = _SENTENCE_END_RE.search(clean)
    if match:
        sentence = clean[: match.end()].rstrip()
    else:
        # No sentence boundary found — use the whole text as one sentence
        sentence = clean
        if not sentence.endswith((".", "!", "?")):
            sentence += "."

    # Truncate if needed
    if len(sentence) > _MAX_LEN:
        sentence = sentence[: _MAX_LEN - 1].rstrip() + "."

    return sentence
