from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

router = Router()

# Главное меню с выбором версии
version_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🆓 Free Version", callback_data="ver_free"),
            InlineKeyboardButton(text="💎 Pro Version",  callback_data="ver_pro"),
        ]
    ]
)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать! Выберите версию:",
        reply_markup=version_menu
    )

@router.callback_query(lambda c: c.data == "ver_free")
async def cb_free(c: CallbackQuery):
    free_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="free_settings")
            ]
        ]
    )
    await c.message.edit_text(
        "🆓 *Free Version*\n\n"
        "• Мониторинг одной биржи\n"
        "• Покупка по курсу ≤ X\n"
        "• Продажа по курсу ≥ Y\n\n"
        "Нажмите кнопку ниже для настроек:",
        parse_mode="Markdown",
        reply_markup=free_kb
    )
    await c.answer()

@router.callback_query(lambda c: c.data == "ver_pro")
async def cb_pro(c: CallbackQuery):
    await c.answer("💎 Pro Version пока недоступна", show_alert=True)
