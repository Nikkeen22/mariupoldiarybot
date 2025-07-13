# state_manager.py

import json
import logging

logger = logging.getLogger(__name__)
DB_FILE = 'user_states.json'
user_states = {}

def load_states():
    """Завантажує стан гравців з файлу при старті бота."""
    global user_states
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            # Конвертуємо ключі з рядків назад у числа
            data = json.load(f)
            user_states = {int(k): v for k, v in data.items()}
            logger.info(f"Successfully loaded {len(user_states)} user(s) from {DB_FILE}")
    except FileNotFoundError:
        logger.info(f"{DB_FILE} not found. Starting with an empty state.")
        user_states = {}
    except json.JSONDecodeError:
        logger.error(f"Could not decode JSON from {DB_FILE}. Starting with an empty state.")
        user_states = {}

def save_states():
    """Зберігає поточний стан гравців у файл."""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_states, f, ensure_ascii=False, indent=4)

def get_user_state(user_id: int) -> dict:
    """Отримує або створює початковий стан для гравця."""
    if user_id not in user_states:
        user_states[user_id] = {
            'health': 100,
            'resources': 100,
            'relationships': 50,
            'hope': 100,
            'met_azov': False,
            'helped_azov': False,
            'took_orphan': False,
            'phone_cleaned': True,
            'filtration_suspicion': 0,
        }
    return user_states[user_id]

def update_stats(user_id: int, health=0, resources=0, relationships=0, hope=0, suspicion=0):
    """Оновлює параметри гравця та зберігає стан."""
    state = get_user_state(user_id)
    state['health'] = max(0, min(100, state['health'] + health))
    state['resources'] = max(0, min(100, state['resources'] + resources))
    state['relationships'] = max(0, min(100, state['relationships'] + relationships))
    state['hope'] = max(0, min(100, state['hope'] + hope))
    state['filtration_suspicion'] += suspicion
    logger.info(f"Stats for {user_id}: H{state['health']} R{state['resources']} Rl{state['relationships']} Ho{state['hope']} S{state['filtration_suspicion']}")
    save_states()

def reset_user_state(user_id: int):
    """Скидає стан гравця до початкових значень та зберігає стан."""
    # Просто створюємо новий стан, викликаючи get_user_state з "неіснуючим" id
    user_states[user_id] = get_user_state(0)
    del user_states[0] # Видаляємо тимчасовий шаблон
    logger.info(f"State for user {user_id} has been reset.")
    save_states()

def set_flag(user_id: int, flag_name: str, value: bool):
    """Встановлює сюжетний прапорець та зберігає стан."""
    state = get_user_state(user_id)
    state[flag_name] = value
    logger.info(f"Flag '{flag_name}' for {user_id} set to {value}")
    save_states()
