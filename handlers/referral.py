import json
from aiogram import Router, F
from aiogram.types import Message

router = Router()
REF_FILE = "referrals.json"
PRO_USERS_FILE = "pro_users.json"

def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

@router.message(F.text == "/refer")
async def send_ref_link(message: Message):
    ref_code = f"ref{message.chat.id}"
    link = f"https://t.me/ArbitProBot?start={ref_code}"
    await message.answer(f"👥 Пригласи друзей и получи 3 дня PRO!\n\nВот твоя ссылка:\n{link}")

@router.message(F.text == "/myref")
async def show_ref_stats(message: Message):
    ref_data = load_json(REF_FILE).get(str(message.chat.id), {})
    count = len(ref_data.get("invited", []))
    used = ref_data.get("used_bonus", False)
    await message.answer(
        f"👥 Приглашено: {count} пользователей\n"
        f"🎁 Бонус использован: {'✅ Да' if used else '❌ Нет'}"
    )

@router.message(F.text.regexp(r"^/start ref(\d+)$"))
async def register_referral(message: Message, regexp_command):
    inviter_id = regexp_command.group(1)
    user_id = str(message.chat.id)

    if user_id == inviter_id:
        await message.answer("❗ Нельзя пригласить самого себя.")
        return

    refs = load_json(REF_FILE)
    if user_id in refs.get(inviter_id, {}).get("invited", []):
        await message.answer("✅ Вы уже были приглашены этим пользователем.")
        return

    if inviter_id not in refs:
        refs[inviter_id] = {"invited": [], "used_bonus": False}
    refs[inviter_id]["invited"].append(user_id)

    if len(refs[inviter_id]["invited"]) >= 2 and not refs[inviter_id]["used_bonus"]:
        pro = load_json(PRO_USERS_FILE)
        if "users" not in pro:
            pro["users"] = []
        if inviter_id not in pro["users"]:
            pro["users"].append(inviter_id)
        refs[inviter_id]["used_bonus"] = True
        save_json(PRO_USERS_FILE, pro)

    save_json(REF_FILE, refs)
    await message.answer("🎉 Вы были успешно зарегистрированы как приглашённый!")
