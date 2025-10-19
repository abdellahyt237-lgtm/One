from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .db import Database
from .keyboards import USER_MENU, subjects_keyboard
from .texts import START_USER, ACCESS_PENDING, ACCESS_DENIED


class UserFlows:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def start_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        approved = self.db.user_is_approved(update.effective_user.id)
        if not approved:
            await update.message.reply_text(START_USER, reply_markup=USER_MENU)
        else:
            await update.message.reply_text("Choisissez une option:", reply_markup=USER_MENU)

    async def request_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.db.create_join_request(user.id, user.username)
        await update.message.reply_text(ACCESS_PENDING)

    async def random_case(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.db.user_is_approved(update.effective_user.id):
            await update.message.reply_text(ACCESS_DENIED)
            return
        c = self.db.get_random_case()
        if c is None:
            await update.message.reply_text("Aucun cas.")
            return
        await update.message.reply_text(c.text)

    async def random_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.db.user_is_approved(update.effective_user.id):
            await update.message.reply_text(ACCESS_DENIED)
            return
        # pick random question: simple approach - fetch all then pick in code
        from random import choice

        subjects = self.db.list_subjects()
        if not subjects:
            await update.message.reply_text("Aucune question.")
            return
        # Build list of all questions
        all_q = []
        for s in subjects:
            all_q.extend(self.db.list_questions_by_subject(s.id))
        if not all_q:
            await update.message.reply_text("Aucune question.")
            return
        q = choice(all_q)
        await update.message.reply_text(q.text)

    async def choose_subject(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.db.user_is_approved(update.effective_user.id):
            await update.message.reply_text(ACCESS_DENIED)
            return
        subs = self.db.list_subjects()
        if not subs:
            await update.message.reply_text("Aucune matière.")
            return
        await update.message.reply_text(
            "Choisissez la matière:",
            reply_markup=subjects_keyboard([(s.id, s.name) for s in subs], "user_pick_subject"),
        )

    async def on_pick_subject(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.db.user_is_approved(update.effective_user.id):
            return
        query = update.callback_query
        await query.answer()
        _, sid_str = query.data.split(":")
        sid = int(sid_str)
        # present a random case from that subject
        c = self.db.get_random_case(sid)
        if c is None:
            await query.edit_message_text("Aucun cas pour cette matière.")
            return
        await query.edit_message_text(c.text)
