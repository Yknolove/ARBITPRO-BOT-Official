from aiogram import Router
from aiogram.filters import CommandStart, CallbackQuery  # или Command
from aiogram.types import Message, CallbackQuery as CQ, InlineKeyboardButton, InlineKeyboardMarkup

router = Router()

# Главное меню — клавиатура с версиями
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

# Обработчик нажатия “Free Version”
@router.callback_query(lambda c: c.data == "ver_free")
async def cb_free(c: CQ):
    # Здесь отображаете интерфейс Free-версии
    free_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [ InlineKeyboardButton(text="⚙️ Настройки", callback_data="free_settings") ]
        ]
    )
    await c.message.edit_text(
        "🆓 *Free Version*\n\n"
        "• Мониторинг одной биржи\n"
        "• Покупка ≤ X\n"
        "• Продажа ≥ Y\n\n"
        "Настройте через кнопку ниже:",
        parse_mode="Markdown",
        reply_markup=free_kb
    )
    await c.answer()  # чтобы убрать “часики” у кнопки

# Обработчик нажатия “Pro Version”
@router.callback_query(lambda c: c.data == "ver_pro")
async def cb_pro(c: CQ):
    await c.answer("💎 Pro Version пока недоступна", show_alert=True)
