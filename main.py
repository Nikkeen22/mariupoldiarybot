# main.py

import logging
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Імпортуємо наші модулі
from config import TELEGRAM_TOKEN
from handlers import start, new_game, status, button_handler
from state_manager import load_states
from handlers import notify_on, notify_off




# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application: Application) -> None:
    """Встановлює меню команд після ініціалізації бота."""
    await application.bot.set_my_commands([
        BotCommand("start", "Почати нову гру"),
        BotCommand("newgame", "Перезапустити гру"),
        BotCommand("status", "Перевірити свій стан"),
    ])

def main() -> None:
    """Головна функція, що збирає все разом і запускає бота."""
    
    load_states()

    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    # Реєструємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("newgame", new_game))
    application.add_handler(CommandHandler("status", status))

    # Реєструємо головний обробник для всіх натискань на кнопки
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("notify_on", notify_on))
    application.add_handler(CommandHandler("notify_off", notify_off))

    logger.info("Bot is starting...")
    application.run_polling()
    logger.info("Bot has stopped.")

if __name__ == "__main__":
    main()
