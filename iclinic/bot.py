from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import List

from iclinic.iclinic.texts import TextStore

try:
    from telegram import Update, ReplyKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        ContextTypes,
        MessageHandler,
        filters,
    )
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "Missing python-telegram-bot. Install requirements and retry."
    ) from exc


@dataclass
class IClinicBot:
    token: str
    texts: TextStore

    def keyboard(self, labels: List[str]) -> ReplyKeyboardMarkup:
        rows = [[label] for label in labels]
        return ReplyKeyboardMarkup(rows, resize_keyboard=True)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_home = self.texts.user_home()
        labels = [item["label"] for item in user_home["menu"]]
        await update.message.reply_text(
            user_home["title"], reply_markup=self.keyboard(labels)
        )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = (update.message.text or "").strip()
        admin_menu = self.texts.admin_main_menu()
        admin_labels = [item["label"] for item in admin_menu["menu"]]
        # Simple echo to demonstrate routing
        if text in admin_labels:
            await update.message.reply_text(f"[Admin] اخترت: {text}")
        else:
            await update.message.reply_text(f"اختر خيارًا من القائمة ⬆️")


async def main() -> None:
    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise SystemExit("Set BOT_TOKEN environment variable first")

    texts = TextStore.default()
    bot = IClinicBot(token=token, texts=texts)

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", bot.cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text))

    print("iClinic bot is running. Press Ctrl+C to stop.")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
