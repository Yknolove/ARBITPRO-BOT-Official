from aiogram import Router, F
from aiogram.types import Message
import json
import os

router = Router()
HISTORY_FILE = "history.json"
PRO_USERS_FILE = "pro_users.json"

def is_pro_user(user_id: int) -> bool:
    if not os.path.exists(PRO_USERS_FILE):
        return False
    with open(PRO_USERS_FILE, "r") as f:
        data = json.load(f)
    return str(user_id) in data

@router.message(F.text == "/history")
async def show_history(message: Message):
    user_id = str(message.chat.id)

    if not is_pro_user(message.chat.id):
        await message.answer("🚫 История доступна только для PRO-пользователей.")
        return

    if not os.path.exists(HISTORY_FILE):
        await message.answer("❗ История сделок пока пуста.")
        return

    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)

    user_history = data.get(user_id, [])
    if not user_history:
        await message.answer("❗ У вас пока нет истории сделок.")
        return

    text = "📈 <b>История сделок:</b>\n\n"
    for i, record in enumerate(user_history[-10:], 1):
        text += f"{i}. {record}\n"

    await message.answer(text, parse_mode="HTML")
