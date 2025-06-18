from aiogram import Router
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(lambda c: c.data == "settings")
async def settings_menu(call: CallbackQuery):
    await call.message.edit_text(
        "⚙️ Раздел настроек в разработке.",
        reply_markup=None
    )
