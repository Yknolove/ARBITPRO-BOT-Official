from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, CallbackQuery
from services.aggregator import start_monitoring  # пример функции запуска мониторинга

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🆓 Free Version", callback_data="free")],
        [InlineKeyboardButton("🔒 Pro Version", callback_data="pro")],
    ])
    await message.answer("Выберите версию:", reply_markup=kb)

@router.callback_query(CallbackQuery.filter(lambda c: c.data in ["free", "pro"]))
async def cb_version(cq: CallbackQuery):
    if cq.data == "free":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("📊 Выбрать биржу", callback_data="choose_exchange")],
            [InlineKeyboardButton("🔄 Обновить", callback_data="refresh")],
        ])
        await cq.message.edit_text(
            "Free версия: мониторинг одной P2P‑биржи.\n"
            "Доступные биржи: Binance, Bybit, OKX, Bitget.",
            reply_markup=kb
        )
    else:
        await cq.answer("Pro версия пока недоступна", show_alert=True)

@router.callback_query(CallbackQuery.filter(lambda c: c.data == "choose_exchange"))
async def cb_choose_exchange(cq: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(x, callback_data=f"exch_{x.lower()}")] for x in ["Binance","Bybit","OKX","Bitget"]
    ])
    await cq.message.edit_text("Выберите биржу для мониторинга:", reply_markup=kb)

# Пример кнопки 'refresh'
@router.callback_query(CallbackQuery.filter(lambda c: c.data == "refresh"))
async def cb_refresh(cq: CallbackQuery):
    await start_monitoring(cq.from_user.id)  # пример: обновляем данные
    await cq.answer("Данные обновлены ✅")
