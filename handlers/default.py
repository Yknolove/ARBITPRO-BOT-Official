from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

router = Router()

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔄 Поиск арбитража", callback_data="arbitrage")],
    [InlineKeyboardButton(text="📈 Курс валют", callback_data="rates")],
    [InlineKeyboardButton(text="🛠 Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="🧾 Инструкция", callback_data="help")]
])

back_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
])

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в <b>ArbitPRO</b>!\n"
        "🔍 Здесь вы можете отслеживать арбитражные возможности и курсы валют.\n\n"
        "👇 Выберите интересующий раздел:",
        reply_markup=main_menu,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "main_menu")
async def back_to_menu(call: CallbackQuery):
    await call.message.edit_text(
        "🔍 Выберите интересующий раздел ниже:",
        reply_markup=main_menu
    )

@router.callback_query(F.data == "arbitrage")
async def show_arbitrage(call: CallbackQuery):
    await call.message.edit_text(
        "📊 Раздел <b>Арбитраж</b> пока в разработке.\nОжидайте обновлений!",
        reply_markup=back_button,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "rates")
async def show_rates(call: CallbackQuery):
    await call.message.edit_text(
        "💰 Курсы валют будут отображаться здесь.\nСледите за обновлениями!",
        reply_markup=back_button,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "settings")
async def show_settings(call: CallbackQuery):
    await call.message.edit_text(
        "⚙️ Настройки в скором времени будут доступны.",
        reply_markup=back_button,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "help")
async def show_help(call: CallbackQuery):
    await call.message.edit_text(
        "🧾 <b>Инструкция:</b>\n\n"
        "1️⃣ Нажмите \"Поиск арбитража\" для анализа сделок.\n"
        "2️⃣ Используйте \"Курс валют\" для отслеживания цен.\n"
        "3️⃣ В разделе \"Настройки\" можно будет настроить фильтры и уведомления.",
        reply_markup=back_button,
        parse_mode="HTML"
    )
