from __future__ import annotations

from typing import Iterable, List

try:
    from telegram import ReplyKeyboardMarkup
except Exception:  # pragma: no cover - optional dependency
    ReplyKeyboardMarkup = None  # type: ignore


def build_reply_keyboard(labels: Iterable[str], row_width: int = 2):
    """Build a PTB ReplyKeyboardMarkup from a list of labels.

    This helper is optional and keeps UI code small. If python-telegram-bot
    is not installed, it will raise a clear error upon use.
    """
    if ReplyKeyboardMarkup is None:
        raise RuntimeError(
            "python-telegram-bot is not installed. Install it to use keyboards."
        )
    buttons: List[List[str]] = []
    row: List[str] = []
    for label in labels:
        row.append(label)
        if len(row) >= row_width:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
