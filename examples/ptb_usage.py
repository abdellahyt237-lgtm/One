# Example usage with python-telegram-bot v20+
from __future__ import annotations

import asyncio
from pathlib import Path

from bot_texts import BotTexts

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    from bot_texts.adapters import build_reply_keyboard
except Exception:  # pragma: no cover - keep example import-safe
    Update = object  # type: ignore
    Application = None  # type: ignore
    CommandHandler = object  # type: ignore
    ContextTypes = object  # type: ignore
    build_reply_keyboard = None  # type: ignore


texts = BotTexts(base_dir=Path(__file__).resolve().parent.parent / "bot_texts")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin = texts.admin_main_menu()
    labels = [item["label"] for item in admin["menu"]]
    if build_reply_keyboard:
        keyboard = build_reply_keyboard(labels, row_width=1)
        await update.message.reply_text(admin["header"], reply_markup=keyboard)
    else:
        await update.message.reply_text(admin["header"] + "\n" + "\n".join(labels))


def main():
    if Application is None:
        print("Install python-telegram-bot to run the example: pip install python-telegram-bot")
        return
    # Replace with your token
    token = "YOUR_TOKEN"
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    print("Running bot… /start")
    app.run_polling()


if __name__ == "__main__":
    main()
