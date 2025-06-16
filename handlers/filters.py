import json
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()
FILTERS_PATH = "filters.json"

class FilterStates(StatesGroup):
    choosing_buy_price = State()
    choosing_sell_price = State()
    choosing_volume = State()

@router.message(F.text == "/filter")
async def start_filter_setup(message: Message, state: FSMContext):
    await message.answer("Введите максимальную цену покупки (например, 41.00):")
    await state.set_state(FilterStates.choosing_buy_price)

@router.message(FilterStates.choosing_buy_price)
async def set_buy_price(message: Message, state: FSMContext):
    try:
        buy_price = float(message.text)
        await state.update_data(buy_price=buy_price)
        await message.answer("Введите минимальную цену продажи (например, 43.00):")
        await state.set_state(FilterStates.choosing_sell_price)
    except ValueError:
        await message.answer("Введите число. Попробуйте снова:")

@router.message(FilterStates.choosing_sell_price)
async def set_sell_price(message: Message, state: FSMContext):
    try:
        sell_price = float(message.text)
        await state.update_data(sell_price=sell_price)
        await message.answer("Введите максимальный объём сделки (до 100$ для Free):")
        await state.set_state(FilterStates.choosing_volume)
    except ValueError:
        await message.answer("Введите число. Попробуйте снова:")

@router.message(FilterStates.choosing_volume)
async def save_filter(message: Message, state: FSMContext):
    try:
        volume = float(message.text)
        if volume > 100:
            await message.answer("🚫 В Free-версии максимум 100$. Введите значение до 100:")
            return
        data = await state.get_data()
        data.update({
            "volume": volume,
            "chat_id": message.chat.id,
            "exchange": "bybit"
        })

        try:
            with open(FILTERS_PATH, "r") as f:
                all_filters = json.load(f)
        except:
            all_filters = {}

        all_filters[str(message.chat.id)] = data
        with open(FILTERS_PATH, "w") as f:
            json.dump(all_filters, f)

        await message.answer(
            f"✅ Фильтр сохранён!\n\n"
            f"Биржа: Bybit\n"
            f"Покупка до: {data['buy_price']}\n"
            f"Продажа от: {data['sell_price']}\n"
            f"Объём до: {data['volume']}$"
        )
        await state.clear()

    except ValueError:
        await message.answer("Введите число. Попробуйте снова:")
