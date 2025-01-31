__all__ = ("router", )

from aiogram import Router
from .admin import router as admin_router
from .user import router as user_router
router = Router()
router.include_routers(admin_router, user_router)