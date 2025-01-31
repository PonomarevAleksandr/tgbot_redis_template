import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage
from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator
import redis
from shared.config import settings
from src.utils.middlewares import ThrottlingMiddleware, DataBaseMiddleware, UserMiddleware, AlbumMiddleware, \
    TranslateMiddleware
from shared.db import db
from src.handlers import router as main_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

t_hub = TranslatorHub(
    {
        "ru": ("ru",)
    },
    translators=[
        FluentTranslator(
            "ru",
            translator=FluentBundle.from_files(
                "ru-RU",
                filenames=[
                    "shared/i18n/ru/text.ftl",
                    "shared/i18n/ru/button.ftl",
                ]
            ),
        )
    ],
    root_locale="ru",
)


async def main():
    session = AiohttpSession()
    bot = Bot(
        token=settings.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    storage = RedisStorage.from_url(
        url=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0")
    rdb = redis.Redis(host=settings.REDIS_HOST, port=int(settings.REDIS_PORT),
                      password=settings.REDIS_PASSWORD)
    dp = Dispatcher(storage=storage, t_hub=t_hub)

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.outer_middleware(DataBaseMiddleware(db=db, rdb=rdb))
    dp.message.outer_middleware(UserMiddleware())
    dp.message.outer_middleware(TranslateMiddleware())
    dp.message.middleware(AlbumMiddleware())

    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.callback_query.outer_middleware(DataBaseMiddleware(db=db, rdb=rdb))
    dp.callback_query.outer_middleware(UserMiddleware())
    dp.callback_query.outer_middleware(TranslateMiddleware())

    dp.include_router(main_router)

    try:
        await dp.start_polling(bot)
    except ValueError as e:
        logger.error("ValueError occurred: %s: ", e)
    except KeyError as e:
        logger.error("KeyError occurred: %s:", e)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
