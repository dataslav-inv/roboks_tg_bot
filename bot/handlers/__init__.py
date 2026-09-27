from aiogram import Router

from bot.handlers import start, menu, application, admin

def get_all_routers() -> list[Router]:
    return [
        start.router,
        menu.router,
        application.router,
        admin.router,
    ]
