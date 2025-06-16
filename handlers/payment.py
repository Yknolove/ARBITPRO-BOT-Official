from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()
ADMIN_ID = 790571461  # ЗАМЕНИ на свой настоящий Telegram ID

@router.message(F.text == "/buy")
async def show_payment_info(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="💳 Отправить чек")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "💎 <b>Покупка PRO-версии</b>\n\n"
        "Стоимость: <b>$12.99 USDT</b>\n"
        "Сеть: <code>TRC20</code>\n"
        "Кошелёк: <code>TFTkikK4TDTbdFuYttJHcLtAMfBsUGsw27</code>\n\n"
        "После оплаты нажмите кнопку ниже и отправьте TX ID.",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.message(F.text == "💳 Отправить чек")
async def ask_txid(message: Message):
    await message.answer("🔁 Введите TX ID транзакции (хэш):")

@router.message(F.text.regexp(r"^[0-9a-fA-F]{20,}$"))
async def handle_txid(message: Message):
    await message.answer("✅ Чек получен! Мы проверим оплату в течение 24 часов.")

    admin_text = (
        f"📥 <b>Новый чек оплаты</b>\n\n"
        f"От: <a href='tg://user?id={message.chat.id}'>{message.chat.id}</a>\n"
        f"TX ID:\n<code>{message.text}</code>\n\n"
        "Проверьте вручную и добавьте пользователя в pro_users.json"
    )
    await message.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
