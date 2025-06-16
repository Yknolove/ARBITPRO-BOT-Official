from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from handlers.filters import FilterStates

router = Router()

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена фильтра")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.callback_query(F.data == "set_filter")
async def send_filter_instruction(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Введите максимальную цену покупки (например, 41.00):",
        reply_markup=cancel_kb
    )
    await state.set_state(FilterStates.choosing_buy_price)

@router.message(F.text == "❌ Отмена фильтра")
async def cancel_filter(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Настройка фильтра отменена.")
