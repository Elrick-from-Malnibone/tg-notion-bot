from aiogram import Dispatcher

def setup_routers(dp: Dispatcher):
    from modules.admin import router as admin_router
    from modules.settings import router as settings_router
    from modules.notes import router as notes_router
    from modules.webapp import router as webapp_router

    dp.include_router(admin_router)
    dp.include_router(settings_router)
    dp.include_router(notes_router)
    dp.include_router(webapp_router)