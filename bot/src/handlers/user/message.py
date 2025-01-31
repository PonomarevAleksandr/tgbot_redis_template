from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from fluentogram import TranslatorRunner

from shared.db import MongoDbClient

router = Router()

@router.message(Command("start"))
async def _(message: Message,
            bot: Bot,
            db: MongoDbClient,
            locale: TranslatorRunner):
    await message.answer(locale.welcome_text())