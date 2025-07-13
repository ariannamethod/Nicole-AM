from __future__ import annotations

import logging
from typing import List, Tuple

from Nicole.serve.app_modules.utils import convert_asis, convert_mdtext, detect_converted_mark


def compact_text_chunks(self, prompt, text_chunks: List[str]) -> List[str]:
    logging.debug("Compacting text chunks...🚀🚀🚀")
    cleaned_chunks = [c.strip() for c in text_chunks if c.strip()]
    numbered = [f"[{index+1}] {c}" for index, c in enumerate(cleaned_chunks)]
    combined_str = "\n\n".join(numbered)
    # resplit based on self.max_chunk_overlap
    text_splitter = self.get_text_splitter_given_prompt(prompt, 1, padding=1)
    return text_splitter.split_text(combined_str)


def postprocess(
    self, y: List[Tuple[str | None, str | None]]
) -> List[Tuple[str | None, str | None]]:
    """
    Parameters:
        y: List of tuples representing the message and response pairs. Each message and response should be a string, which may be in Markdown format.
    Returns:
        List of tuples representing the message and response. Each message and response will be a string of HTML.
    """
    if y is None or y == []:
        return []
    temp = []
    for x in y:
        user, bot = x
        if not detect_converted_mark(user):
            user = convert_asis(user)
        if not detect_converted_mark(bot):
            bot = convert_mdtext(bot)
        temp.append((user, bot))
    return temp


def reload_javascript():
    """Placeholder for compatibility after removing custom JS injection."""
    print("Reloading javascript...")

