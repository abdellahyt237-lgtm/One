from __future__ import annotations

from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from .db import Database
from .keyboards import ADMIN_MENU, subjects_keyboard, confirm_keyboard, deletion_keyboard
from .texts import (
    START_ADMIN,
    PROMPT_SUBJECT_NAME,
    ADDED_SUBJECT,
    PROMPT_CONTENT_TYPE,
    PROMPT_CASE_TEXT,
    PROMPT_QUESTION_TEXT,
    NO_DATA,
)

# Conversation states
ADD_SUBJECT_NAME = 1
CHOOSE_CONTENT_TYPE = 2
ADDING_CASE_TEXT = 3
ADDING_QUESTION_TEXT = 4


class AdminFlows:
    def __init__(self, db: Database, admin_id: int) -> None:
        self.db = db
        self.admin_id = admin_id

    def _is_admin(self, update: Update) -> bool:
        return update.effective_user and update.effective_user.id == self.admin_id

    async def start_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return
        await update.message.reply_text(START_ADMIN, reply_markup=ADMIN_MENU)

    async def add_subject_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return ConversationHandler.END
        await update.message.reply_text(PROMPT_SUBJECT_NAME)
        return ADD_SUBJECT_NAME

    async def add_subject_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return ConversationHandler.END
        name = update.message.text.strip()
        self.db.add_subject(name)
        await update.message.reply_text(ADDED_SUBJECT, reply_markup=ADMIN_MENU)
        return ConversationHandler.END

    async def add_content_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return ConversationHandler.END
        subjects = [(s.id, s.name) for s in self.db.list_subjects()]
        if not subjects:
            await update.message.reply_text(NO_DATA)
            return ConversationHandler.END
        await update.message.reply_text(
            PROMPT_CONTENT_TYPE,
            reply_markup=subjects_keyboard(subjects, "admin_pick_subject"),
        )
        return CHOOSE_CONTENT_TYPE

    async def on_pick_subject(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return ConversationHandler.END
        query = update.callback_query
        await query.answer()
        _, sid_str = query.data.split(":")
        context.user_data["subject_id"] = int(sid_str)
        # ask what to add: case or question
        await query.edit_message_text(
            PROMPT_CONTENT_TYPE,
            reply_markup=confirm_keyboard("admin_type_case", "case"),
        )
        return CHOOSE_CONTENT_TYPE

    async def on_confirm_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return ConversationHandler.END
        query = update.callback_query
        await query.answer()
        parts = query.data.split(":")
        prefix, action, payload = parts[0], parts[1], parts[2]
        if prefix == "admin_type_case":
            if action == "ok":
                await query.edit_message_text(PROMPT_CASE_TEXT)
                return ADDING_CASE_TEXT
            else:
                await query.edit_message_text(PROMPT_QUESTION_TEXT)
                return ADDING_QUESTION_TEXT
        return ConversationHandler.END

    async def on_case_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return ConversationHandler.END
        text = update.message.text
        sid = int(context.user_data.get("subject_id"))
        self.db.add_case(sid, text)
        await update.message.reply_text("Cas ajouté.", reply_markup=ADMIN_MENU)
        return ConversationHandler.END

    async def on_question_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return ConversationHandler.END
        text = update.message.text
        sid = int(context.user_data.get("subject_id"))
        self.db.add_question(sid, text)
        await update.message.reply_text("Question ajoutée.", reply_markup=ADMIN_MENU)
        return ConversationHandler.END

    async def list_join_requests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return
        pending = self.db.list_pending_requests()
        if not pending:
            await update.message.reply_text("Aucune demande en attente.")
            return
        for req in pending:
            label = f"@{req.username or 'user'} ({req.user_id})"
            await update.message.reply_text(
                label,
                reply_markup=confirm_keyboard("approve", str(req.user_id)),
            )

    async def on_approve(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return
        query = update.callback_query
        await query.answer()
        _, action, payload = query.data.split(":")
        user_id = int(payload)
        self.db.set_join_request(user_id, approved=(action == "ok"))
        await query.edit_message_text(
            "Approuvé." if action == "ok" else "Refusé."
        )

    async def delete_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return ConversationHandler.END
        subjects = [(s.id, s.name) for s in self.db.list_subjects()]
        if not subjects:
            await update.message.reply_text(NO_DATA)
            return ConversationHandler.END
        await update.message.reply_text(
            "Choisir une matière pour supprimer cas/questions",
            reply_markup=subjects_keyboard(subjects, "admin_del_subject"),
        )
        return ConversationHandler.END

    async def on_delete_subject(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return
        query = update.callback_query
        await query.answer()
        _, sid_str = query.data.split(":")
        sid = int(sid_str)
        # list cases and questions to delete
        cases = self.db.list_cases_by_subject(sid)
        questions = self.db.list_questions_by_subject(sid)
        if not cases and not questions:
            await query.edit_message_text("Rien à supprimer.")
            return
        if cases:
            await query.edit_message_text(
                "Supprimer un cas:",
                reply_markup=deletion_keyboard(
                    "del_case", [(c.id, f"Cas #{c.id}") for c in cases]
                ),
            )
        if questions:
            await query.message.reply_text(
                "Supprimer une question:",
                reply_markup=deletion_keyboard(
                    "del_q", [(q.id, f"Q #{q.id}") for q in questions]
                ),
            )

    async def on_delete_item(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_admin(update):
            return
        query = update.callback_query
        await query.answer()
        prefix, _, item_id_str = query.data.split(":")
        item_id = int(item_id_str)
        if prefix == "del_case":
            self.db.delete_case(item_id)
            await query.edit_message_text("Cas supprimé.")
        elif prefix == "del_q":
            self.db.delete_question(item_id)
            await query.edit_message_text("Question supprimée.")
