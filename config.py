# config.py
import os
from dotenv import load_dotenv

# Завантажує змінні з .env
load_dotenv()

# Токен бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_TOKEN у .env!")

# ID адміністратора
ADMIN_ID = os.getenv("ADMIN_ID")
if not ADMIN_ID:
    raise ValueError("Не знайдено ADMIN_ID у .env!")
ADMIN_ID = int(ADMIN_ID)  # Перетворюємо з рядка на int

# Увімкнення повідомлень при старті
NOTIFY_ON_START = os.getenv("NOTIFY_ON_START", "false").lower() == "true"
