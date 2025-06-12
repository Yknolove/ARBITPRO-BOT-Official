from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    Message, ReplyKeyboardRemove
)
from aiogram.fsm.state import State, StatesGroup, AnyState
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

class FreeSettingsStates(StatesGroup):
    exchange = State()
    buy      = State()
    sell     = State()
    volume   = State()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🆓 Free Version")],
        [KeyboardButton(text="💎 Pro Version")],
    ], resize_keyboard=True
)
free_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏷 Биржа"), KeyboardButton(text="📈 BUY")],
        [KeyboardButton(text="📉 SELL"), KeyboardButton(text="🔢 Лимит")],
        [KeyboardButton(text="📊 Показать настройки"), KeyboardButton(text="🔙 Главное меню")],
    ], resize_keyboard=True
)

@router.message(Command("start"), state=AnyState())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Добро пожаловать в ArbitPRO!\nВыберите версию:", reply_markup=main_kb)

@router.message(lambda m: m.text=="🆓 Free Version", state=AnyState())
async def enter_free(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🆓 Free Version Menu:\nВыберите действие:", reply_markup=free_kb)

@router.message(lambda m: m.text=="💎 Pro Version", state=AnyState())
async def enter_pro(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("💎 Pro версия скоро будет доступна!", reply_markup=main_kb)

@router.message(lambda m: m.text=="🔙 Главное меню", state=AnyState())
async def back_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню:", reply_markup=main_kb)

# Далее идут уже FSM-хэндлеры для FreeSettingsStates
@router.message(lambda m: m.text=="🏷 Биржа", state=AnyState())
async def set_exchange_prompt(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите биржу...", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FreeSettingsStates.exchange)

@router.message(FreeSettingsStates.exchange)
async def process_exchange(message: Message, state: FSMContext):
    # ...ваша логика...
    await state.clear()
    await message.answer("✅ Биржа установлена", reply_markup=free_kb)
