"""Simple loader for Arabic bot texts with medical emojis.

Usage:
    from bot_texts import BotTexts
    texts = BotTexts()  # auto-detects package directory
    admin_menu = texts.admin_main_menu()

Optional PTB helpers are in bot_texts.adapters.ptb.
"""
from .loader import BotTexts

__all__ = ["BotTexts"]
