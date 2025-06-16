import json
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()
PRO_USERS_FILE = "pro_users.json"

class CalcStates(StatesGroup):
    buying = State()
    selling = State()
    volume = State()
    commission = State()

def is_pro(user_id: int) -> bool:
    try:
        with open(PRO_USERS_FILE, "r") as f:
            data = json.load(f)
        return str(user_id) in data.get("users", [])
    except:
        return False

@router.message(F.text == "/calc")
async def start_calc(message: Message, state: FSMContext):
    if not is_pro(message.chat.id):
        await message.answer(
            "🔒 Калькулятор доступен только для <b>PRO</b>-пользователей.\n"
            "💎 Подключите PRO, чтобы получить доступ к расширенным функциям.",
            parse_mode="HTML"
        )
        return
    await message.answer("🔢 Введите курс покупки (₴):")
    await state.set_state(CalcStates.buying)

@router.message(CalcStates.buying)
async def set_buy(message: Message, state: FSMContext):
    try:
        await state.update_data(buy=float(message.text))
        await message.answer("📈 Введите курс продажи (₴):")
        await state.set_state(CalcStates.selling)
    except:
        await message.answer("❌ Введите число (например: 41.00):")

@router.message(CalcStates.selling)
async def set_sell(message: Message, state: FSMContext):
    try:
        await state.update_data(sell=float(message.text))
        await message.answer("💵 Введите объём сделки ($):")
        await state.set_state(CalcStates.volume)
    except:
        await message.answer("❌ Введите число (например: 43.00):")

@router.message(CalcStates.volume)
async def set_volume(message: Message, state: FSMContext):
    try:
        await state.update_data(volume=float(message.text))
        await message.answer("💸 Введите комиссию (%), если есть (0 по умолчанию):")
        await state.set_state(CalcStates.commission)
    except:
        await message.answer("❌ Введите число (например: 100):")

@router.message(CalcStates.commission)
async def calc_profit(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        buy = data["buy"]
        sell = data["sell"]
        volume = data["volume"]
        commission_percent = float(message.text)

        cost = buy * volume
        gain = sell * volume
        commission = gain * commission_percent / 100
        profit = gain - cost - commission
        profit_pct = ((profit / cost) * 100) if cost else 0

        await message.answer(
            f"💹 <b>Результат:</b>\n"
            f"Потрачено: {cost:.2f} ₴\n"
            f"Получено: {gain:.2f} ₴\n"
            f"Комиссия: {commission:.2f} ₴\n"
            f"📊 Прибыль: {profit:.2f} ₴ ({profit_pct:.2f}%)",
            parse_mode="HTML"
        )
        await state.clear()
    except:
        await message.answer("❌ Введите корректное число.")
