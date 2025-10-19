import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from .db import init_db, ensure_user

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
TZ = os.getenv("TZ", "Africa/Algiers")

bot = Bot(TOKEN)
dp = Dispatcher()

DISCLAIMER = (
    "iClinic — Outil éducatif uniquement.\n"
    "Les informations fournies ne remplacent pas un avis médical professionnel.\n"
    "En cas d'urgence, contactez les services médicaux."
)

@dp.message(CommandStart())
async def start_handler(msg: Message) -> None:
    await ensure_user(msg.from_user.id, language="fr")
    await msg.answer(
        "Bienvenue à iClinic! 🇫🇷\n"
        "Je suis un bot d'étude pour les étudiants en médecine.\n\n"
        "Commandes utiles:\n"
        "/help — Aide et avertissement\n"
    )

@dp.message(Command("help"))
async def help_handler(msg: Message) -> None:
    await msg.answer(
        "Aide iClinic:\n"
        "- Objectif: assister vos révisions et QCM.\n"
        "- Langue: Français.\n\n"
        f"Avertissement:\n{DISCLAIMER}"
    )

async def main() -> None:
    if not TOKEN:
        print("Veuillez définir BOT_TOKEN dans l'environnement.")
        return
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
