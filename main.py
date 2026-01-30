import requests
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from flask import Flask, request
import threading

# ====== ВСТАВЬ СВОИ ДАННЫЕ ======

BOT_TOKEN = "8582953155:AAG2KhurX860OrKAxIhvWqlzTFmW1AFrvB4"
CRYPTO_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiT0RjeU56QT0iLCJ0eXBlIjoicHJvamVjdCIsInYiOiJlN2Y3NDUwZjZmZWViNzA3OWU1Yzk4OTZmZjkzMjYyMjlmM2UzNDcxYWU4NDFiZTFiMWI3YjJmOTY5M2JhY2FiIiwiZXhwIjo4ODE2OTQ5OTU4MX0.JRJjDMzQJN05NrUX8cy7rKsi2vawY9wa2Xw5GeBeSTo"
SHOP_ID = "ylzq8nf8U45ONjp3"

# ===============================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# -------- Тарифы (фиксированные цены) --------
TARIFFS = {
    "tariff_1": 100,
    "tariff_2": 220,
    "tariff_3": 1000
}

# -------- Создание платежа --------
def create_payment(amount):
    order_id = str(uuid.uuid4())

    url = "https://api.cryptocloud.plus/v1/invoice/create"
    headers = {
        "Authorization": f"Token {CRYPTO_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "shop_id": SHOP_ID,
        "amount": amount,
        "currency": "USDT",
        "order_id": order_id,
        "desc": f"Оплата тарифа {amount} USDT",
        "callback_url": "https://archwarg-bot.onrender.com/webhook"
    }

    r = requests.post(url, json=data, headers=headers)
    return r.json()["pay_url"], order_id


# -------- Команда /start --------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton("🔥 Тариф 1 — 100 USDT", callback_data="tariff_1"))
    keyboard.add(InlineKeyboardButton("⚡ Тариф 2 — 220 USDT", callback_data="tariff_2"))
    keyboard.add(InlineKeyboardButton("💎 Тариф 3 — 1000 USDT", callback_data="tariff_3"))

    await message.answer("Выбери тариф 👇", reply_markup=keyboard)


# -------- Нажатие на тариф --------
@dp.callback_query_handler(lambda c: c.data in TARIFFS)
async def process_tariff(callback_query: types.CallbackQuery):
    tariff_key = callback_query.data
    amount = TARIFFS[tariff_key]

    pay_url, order_id = create_payment(amount)

    await bot.send_message(
        callback_query.from_user.id,
        f"💳 Оплата тарифа {amount} USDT\n\n"
        f"👉 Перейди по ссылке для оплаты:\n{pay_url}"
    )


# -------- Webhook от CryptoCloud --------
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data and data.get("status") == "paid":
        order_id = data.get("order_id")
        print("✅ Оплата прошла:", order_id)

    return "OK"


# -------- Запуск Flask и бота --------
def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
