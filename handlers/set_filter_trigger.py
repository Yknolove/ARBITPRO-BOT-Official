from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.filters import FilterStates

router = Router()

@router.callback_query(F.data == "set_filter")
async def send_filter_instruction(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите максимальную цену покупки (например, 41.00):")
    await state.set_state(FilterStates.choosing_buy_price)
