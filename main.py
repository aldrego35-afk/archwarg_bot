import requests
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from flask import Flask, request
import threading
import os

# ====== ВСТАВЬ СВОИ ДАННЫЕ ======

BOT_TOKEN = "8582953155:AAG2KhurX860OrKAxIhvWqlzTFmW1AFrvB4"
CRYPTO_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiT0RjeU56QT0iLCJ0eXBlIjoicHJvamVjdCIsInYiOiJlN2Y3NDUwZjZmZWViNzA3OWU1Yzk4OTZmZjkzMjYyMjlmM2UzNDcxYWU4NDFiZTFiMWI3YjJmOTY5M2JhY2FiIiwiZXhwIjo4ODE2OTQ5OTU4MX0.JRJjDMzQJN05NrUX8cy7rKsi2vawY9wa2Xw5GeBeSTo"
SHOP_ID = "ylzq8nf8U45ONjp3"

# Render URL (ПОТОМ ВСТАВИМ)
RENDER_URL = os.environ.get("RENDER_URL", "")

# ===============================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

TARIFFS = {
    "tariff_1": 100,
    "tariff_2": 220,
    "tariff_3": 1000
}

import asyncio

def create_payment_sync(amount):
    order_id = str(uuid.uuid4())

    url = "https://api.cryptocloud.plus/v1/invoice/create"
    headers = {
        "Authorization": f"Token {CRYPTO_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "shop_id": SHOP_ID,
        "amount": amount,
        "currency": "USDT_TRC20",
        "order_id": order_id,
        "desc": f"Оплата тарифа {amount} USDT_TRC20",
        "callback_url": f"{RENDER_URL}/webhook"
    }

    r = requests.post(url, json=data, headers=headers)

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)   # 👈 САМОЕ ВАЖНОЕ

    response = r.json()

    if "pay_url" not in response:
        return f"❌ Ошибка API: {response}"

    return response["result"]["pay_url"]



@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔥 6 месяцев — 100 USDT", callback_data="tariff_1"))
    keyboard.add(InlineKeyboardButton("⚡ 3 месяца — 220 USDT", callback_data="tariff_2"))
    keyboard.add(InlineKeyboardButton("💎 VIP — 1000 USDT", callback_data="tariff_3"))

    await message.answer("Выбери тариф 👇", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in TARIFFS)
async def process_tariff(callback_query: types.CallbackQuery):
    await callback_query.answer("Создаю ссылку...")

    amount = TARIFFS[callback_query.data]
    pay_url = await create_payment(amount)

    await bot.send_message(callback_query.from_user.id, str(pay_url))



app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook:", data)
    return "OK"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
