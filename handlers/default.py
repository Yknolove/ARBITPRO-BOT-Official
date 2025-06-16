from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

router = Router()

# Главное меню с разделением по доступности
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Поиск арбитража", callback_data="arbitrage")],
    [InlineKeyboardButton(text="📈 Курс валют", callback_data="rates")],
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="💎 Перейти в PRO", callback_data="pro")]
])

# Кнопки внутри раздела арбитража
arbitrage_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔧 Настроить фильтр", callback_data="set_filter")],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
])

# Назад из любого раздела
back_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="main_menu")]
])

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в <b>ArbitPRO</b> <code>(Free)</code>!

"
        "🔓 Доступные функции:
"
        "• Поиск арбитража
"
        "• Курс валют
"
        "• Настройки

"
        "🔒 <b>PRO-функции (в разработке):</b>
"
        "• Калькулятор прибыли
"
        "• История сделок
"
        "• Архив топ-сделок

"
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
        "📊 <b>Арбитраж</b>

"
        "🔎 Здесь вы можете настроить фильтр и получать уведомления
"
        "о сделках на выбранной бирже (Bybit).
",
        reply_markup=arbitrage_menu,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "set_filter")
async def send_filter_instruction(call: CallbackQuery):
    await call.message.answer("Чтобы настроить фильтр, используйте команду:
<code>/filter</code>", parse_mode="HTML")

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
        "💎 <b>PRO-функции</b> скоро будут доступны!

"
        "🔓 Подписка откроет доступ к:
"
        "• Калькулятору прибыли
"
        "• Истории сделок
"
        "• Архиву топ-сделок
"
        "• Реферальной системе и бонусам
",
        reply_markup=back_menu,
        parse_mode="HTML"
    )
