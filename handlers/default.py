from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

router = Router()

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Поиск арбитража", callback_data="arbitrage")],
    [InlineKeyboardButton(text="📈 Курс валют", callback_data="rates")],
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="💎 Перейти в PRO", callback_data="pro")]
])

arbitrage_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔧 Настроить фильтр", callback_data="set_filter")],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
])

back_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
])

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в <b>ArbitPRO</b> <code>(Free)</code>!\n\n"
        "🔓 Доступные функции:\n"
        "• Поиск арбитража\n"
        "• Курс валют\n"
        "• Настройки\n\n"
        "🔒 <b>PRO-функции (в разработке):</b>\n"
        "• Калькулятор прибыли\n"
        "• История сделок\n"
        "• Архив топ-сделок\n\n"
        "👇 Выберите раздел:",
        reply_markup=main_menu,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "main_menu")
async def back_to_menu(call: CallbackQuery):
    await call.message.edit_text(
        "👇 Выберите раздел:",
        reply_markup=main_menu
    )

@router.callback_query(F.data == "arbitrage")
async def show_arbitrage(call: CallbackQuery):
    await call.message.edit_text(
        "📊 <b>Арбитраж</b>\n\n"
        "🔎 Здесь вы можете настроить фильтр и получать уведомления "
        "о сделках на выбранной бирже (Bybit).",
        reply_markup=arbitrage_menu,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "set_filter")
async def send_filter_instruction(call: CallbackQuery):
    await call.message.answer("Чтобы настроить фильтр, используйте команду:\n<code>/filter</code>", parse_mode="HTML")

@router.callback_query(F.data == "rates")
async def show_rates(call: CallbackQuery):
    await call.message.edit_text(
        "📈 Курсы валют скоро будут добавлены.",
        reply_markup=back_menu
    )

@router.callback_query(F.data == "settings")
async def show_settings(call: CallbackQuery):
    await call.message.edit_text(
        "⚙️ Раздел настроек в разработке.",
        reply_markup=back_menu
    )

@router.callback_query(F.data == "pro")
async def show_pro_info(call: CallbackQuery):
    await call.message.edit_text(
        "💎 <b>PRO-функции</b> скоро будут доступны!\n\n"
        "🔓 Подписка откроет доступ к:\n"
        "• Калькулятору прибыли\n"
        "• Истории сделок\n"
        "• Архиву топ-сделок\n"
        "• Реферальной системе и бонусам",
        reply_markup=back_menu,
        parse_mode="HTML"
    )
