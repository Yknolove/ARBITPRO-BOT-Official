from aiogram import Router
from aiogram.filters import CommandStart, Text
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

router = Router()

# Главное меню
menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🆓 Free Version", callback_data="ver_free"),
        InlineKeyboardButton(text="💎 Pro Version", callback_data="ver_pro"),
    ]
])

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в ArbitPRO! Выберите версию:",
        reply_markup=menu
    )

@router.callback_query(Text("ver_free"))
async def cb_free(c: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Show Arbitrage", callback_data="show_arb")]
    ])
    await c.message.edit_text(
        "🆓 *Free Version*\n\n"  
        "• Мониторинг одной биржи P2P\n"
        "• Настройка порогов: /set_buy и /set_sell", parse_mode="Markdown",
        reply_markup=kb
    )
    await c.answer()

@router.callback_query(Text("show_arb"))
async def cb_show_arb(c: CallbackQuery):
    # stub: сюда придут расчёты
    await c.message.answer("🔄 Fetching arbitrage...")
    await c.answer()
