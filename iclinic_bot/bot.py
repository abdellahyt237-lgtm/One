from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from .config import load_settings
from .db import Database
from .admin_handlers import AdminFlows, ADD_SUBJECT_NAME, CHOOSE_CONTENT_TYPE, ADDING_CASE_TEXT, ADDING_QUESTION_TEXT
from .user_handlers import UserFlows

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context):
    settings = context.application.bot_data["settings"]
    admin_id = settings.admin_id
    if update.effective_user and update.effective_user.id == admin_id:
        await context.application.bot_data["admin"].start_admin(update, context)
    else:
        await context.application.bot_data["user"].start_user(update, context)


def build_app() -> Application:
    settings = load_settings()
    db = Database(settings.database_path)
    admin = AdminFlows(db, settings.admin_id)
    user = UserFlows(db)

    app = ApplicationBuilder().token(settings.bot_token).build()
    app.bot_data["settings"] = settings
    app.bot_data["db"] = db
    app.bot_data["admin"] = admin
    app.bot_data["user"] = user

    # /start
    app.add_handler(CommandHandler("start", start))

    # Admin conversations
    add_subject_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Ajouter matière$"), admin.add_subject_entry)],
        states={
            ADD_SUBJECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.add_subject_name)],
        },
        fallbacks=[],
    )

    add_content_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🩺 Ajouter cas ou question$"), admin.add_content_entry)],
        states={
            CHOOSE_CONTENT_TYPE: [
                CallbackQueryHandler(admin.on_pick_subject, pattern="^admin_pick_subject:"),
                CallbackQueryHandler(admin.on_confirm_type, pattern="^(admin_type_case):"),
            ],
            ADDING_CASE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.on_case_text)],
            ADDING_QUESTION_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.on_question_text)],
        },
        fallbacks=[],
    )

    app.add_handler(add_subject_conv)
    app.add_handler(add_content_conv)

    # Admin: list join requests, approve/refuse
    app.add_handler(MessageHandler(filters.Regex("^📥 Demandes d'accès$"), admin.list_join_requests))
    app.add_handler(CallbackQueryHandler(admin.on_approve, pattern="^approve:"))

    # Admin: delete
    app.add_handler(MessageHandler(filters.Regex("^🗑️ Supprimer$"), admin.delete_entry))
    app.add_handler(CallbackQueryHandler(admin.on_delete_subject, pattern="^admin_del_subject:"))
    app.add_handler(CallbackQueryHandler(admin.on_delete_item, pattern="^(del_case|del_q):"))

    # User commands/buttons
    app.add_handler(MessageHandler(filters.Regex("^🩺 Cas aléatoire$"), user.random_case))
    app.add_handler(MessageHandler(filters.Regex("^❓ Question aléatoire$"), user.random_question))
    app.add_handler(MessageHandler(filters.Regex("^📚 Choisir matière$"), user.choose_subject))
    app.add_handler(CallbackQueryHandler(user.on_pick_subject, pattern="^user_pick_subject:"))

    return app


def main():
    app = build_app()
    app.run_polling()


if __name__ == "__main__":
    main()
