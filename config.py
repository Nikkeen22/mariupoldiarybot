# config.py
import os
from dotenv import load_dotenv

# Завантажує змінні з файлу .env в оточення
load_dotenv()

# Беремо токен з оточення. Якщо його там немає, повертається None.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Перевірка, чи токен взагалі існує
if not TELEGRAM_TOKEN:
    raise ValueError("Не знайдено токен! Перевірте ваш .env файл або налаштування оточення.")
