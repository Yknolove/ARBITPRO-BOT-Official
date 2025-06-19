from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

# Пример базы данных PRO-подписчиков (можно заменить реальной проверкой)
PRO_USERS = [123456789, 987654321]  # <-- замените на реальные chat_id

@router.message(Command("calc"))
async def calc_info(message: Message):
    if message.chat.id not in PRO_USERS:
        await message.answer("🔒 Эта функция доступна только для пользователей с PRO-подпиской.")
        return

    await message.answer(
        "💹 <b>Калькулятор прибыли</b>\n\n"
        "Отправьте данные в формате:\n"
        "<code>buy=41.20 sell=43.00 volume=100 fee=0.5</code>\n\n"
        "• volume — сумма в USD\n"
        "• fee — комиссия в % (на обе стороны)",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("buy="))
async def calculate_profit(message: Message):
    if message.chat.id not in PRO_USERS:
        await message.answer("🔒 Эта функция доступна только для пользователей с PRO-подпиской.")
        return

    try:
        parts = dict(x.split("=") for x in message.text.split())
        buy = float(parts["buy"])
        sell = float(parts["sell"])
        volume = float(parts["volume"])
        fee = float(parts.get("fee", 0))

        gross = volume * (sell - buy) / buy
        net = gross - (volume * fee / 100) * 2

        await message.answer(
            f"📈 <b>Расчёт прибыли:</b>\n\n"
            f"🔹 Покупка: {buy}$\n"
            f"🔹 Продажа: {sell}$\n"
            f"🔹 Объём: {volume}$\n"
            f"🔹 Комиссия: {fee}%\n\n"
            f"💰 <b>Чистая прибыль:</b> {net:.2f}$",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Введите корректное число.")
    except Exception:
        await message.answer("⚠️ Неверный формат. Повторите ещё раз.")
