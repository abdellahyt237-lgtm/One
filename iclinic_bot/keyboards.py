from __future__ import annotations

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# Admin main menu
ADMIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("➕ Ajouter matière")],
        [KeyboardButton("🩺 Ajouter cas ou question")],
        [KeyboardButton("📥 Demandes d'accès")],
        [KeyboardButton("🗑️ Supprimer")],
        [KeyboardButton("↩️ Aller à l'interface utilisateur")],
    ],
    resize_keyboard=True,
)

# User main menu
USER_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🩺 Cas aléatoire"), KeyboardButton("❓ Question aléatoire")],
        [KeyboardButton("📚 Choisir matière")],
    ],
    resize_keyboard=True,
)


def subjects_keyboard(subjects: list[tuple[int, str]], postfix: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"{postfix}:{sid}")]
        for sid, name in subjects
    ]
    return InlineKeyboardMarkup(buttons)


def confirm_keyboard(prefix: str, payload: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Confirmer", callback_data=f"{prefix}:ok:{payload}"),
                InlineKeyboardButton("❌ Annuler", callback_data=f"{prefix}:cancel:{payload}"),
            ]
        ]
    )


def deletion_keyboard(prefix: str, items: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"{prefix}:del:{item_id}")]
        for item_id, label in items
    ]
    return InlineKeyboardMarkup(buttons)
