from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Добро пожаловать в ArbitPRO!")

@router.message(F.text == "Привет")
async def handle_hello(message: Message):
    await message.answer("Привет-привет! Чем могу помочь?")

@router.message(F.text.contains("курс"))
async def handle_rate_request(message: Message):
    await message.answer("💸 Актуальные курсы ты можешь узнать в разделе 📊 Арбитраж.")
