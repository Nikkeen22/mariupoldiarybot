# handlers.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

# Імпортуємо наші модулі
import stages
import state_manager
import assets

async def handle_choice(query, text_response, health=0, resources=0, relationships=0, hope=0, suspicion=0):
    """Універсальна функція для обробки вибору."""
    user_id = query.from_user.id
    state_manager.update_stats(user_id, health, resources, relationships, hope, suspicion)
    if text_response:
        await query.message.reply_text(text_response, parse_mode='HTML')

# --- Обробники команд ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Надсилає вступне повідомлення, відео та кнопку для старту."""
    user = update.effective_user
    state_manager.reset_user_state(user.id)
    
    # 1. Надсилаємо текстовий дисклеймер
    disclaimer_text = (
        "<b>Увага!</b>\n\n"
        "Ця інтерактивна історія заснована на реальних свідченнях людей, що пережили облогу Маріуполя. "
        "Її мета — не розважити, а зберегти пам'ять про трагедію та незламність українського духу.\n\n"
        "Історія може містити сцени, що емоційно важко сприймати. "
        "Погляньте на те, що росія зробила з нашим містом."
    )
    await update.message.reply_html(disclaimer_text)

    # 2. Надсилаємо відеофайл з локального шляху
    try:
        with open(assets.VIDEO_PATH, 'rb') as video_file:
            await context.bot.send_video(chat_id=user.id, video=video_file, supports_streaming=True)
    except FileNotFoundError:
        print(f"Video file not found at {assets.VIDEO_PATH}. Sending URL as fallback.")
        await update.message.reply_text(f"Відео зруйнованого міста: {assets.VIDEO_URL}")
    except Exception as e:
        print(f"Error sending local video: {e}. Sending URL as fallback.")
        await update.message.reply_text(f"Відео зруйнованого міста: {assets.VIDEO_URL}")

    # 3. Надсилаємо кнопку для початку гри
    keyboard = [[InlineKeyboardButton("Я готовий / готова почати", callback_data='intro_accept_start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Натисніть, щоб продовжити.", reply_markup=reply_markup)


async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Перезапускає гру, викликаючи логіку /start."""
    await start(update, context)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показує поточний стан гравця."""
    user_id = update.effective_user.id
    state = state_manager.get_user_state(user_id)
    status_text = (
        "<b>Ваш поточний стан:</b>\n\n"
        f"❤️ Здоров'я: {state['health']}/100\n"
        f"💡 Ресурси: {state['resources']}/100\n"
        f"🤝 Відносини: {state['relationships']}/100\n"
        f"🔥 Надія: {state['hope']}/100"
    )
    await update.message.reply_html(status_text)

# --- Головний обробник кнопок ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    user_id = query.from_user.id
    data = query.data.split('_')
    action_type, stage_name, choice = data[0], data[1], '_'.join(data[2:])
    
    state = state_manager.get_user_state(user_id)
    if state['health'] <= 0:
        await stages.game_over(query, "Ти помер від ран та виснаження.")
        return
    if state['hope'] <= 0:
        await stages.game_over(query, "Ти втратив будь-яку надію і здався.")
        return

    # --- Маршрутизатор дій ---
    
    if action_type == 'intro' and stage_name == 'accept':
        try:
            caption = "Для повного занурення, рекомендую увімкнути цей трек."
            with open(assets.MUSIC_PATH, 'rb') as audio_file:
                await query.message.reply_audio(audio=audio_file, caption=caption)
        except Exception as e:
            print(f"Error sending audio: {e}")
        
        await stages.stage_day1(query)
        return

    if action_type == 'act':
        if stage_name == 'day1':
            if choice == 'phone':
                await handle_choice(query, "📱 Ти бачиш новини... (💡-5, 🔥-5)", resources=-5, hope=-5)
                state_manager.set_flag(user_id, 'phone_cleaned', False)
            elif choice == 'suitcase':
                await handle_choice(query, "🎒 Ти дієш на інстинктах... (�+10)", resources=10)
            elif choice == 'window':
                await handle_choice(query, "👀 Ти бачиш заграву... (❤️-5, 🔥-10)", health=-5, hope=-10)
            await stages.stage_day1_call(query)
        
        elif stage_name == 'day1call':
            if choice == 'calm': await handle_choice(query, "Твій спокій передається їм. (🤝+10, 🔥+5)", relationships=10, hope=5)
            elif choice == 'panic': await handle_choice(query, "Ваша розмова лише посилює паніку. (🤝-5, 🔥-5)", relationships=-5, hope=-5)
            elif choice == 'evacuate': await handle_choice(query, "Ідея про виїзд породжує безсилля. (💡-5, 🔥-10)", resources=-5, hope=-10)
            await stages.stage_day2(query)
        
        elif stage_name == 'day2':
            if choice == 'supermarket': await handle_choice(query, "Ти встигаєш схопити останні крупи... (💡+20)", resources=20)
            elif choice == 'atm': await handle_choice(query, "Вдається зняти кілька тисяч... (💡+15)", resources=15)
            elif choice == 'pharmacy': await handle_choice(query, "Найцінніша інвестиція. (❤️+5, 💡+15)", health=5, resources=15)
            await stages.stage_day5(query)

        elif stage_name == 'day5':
            if choice == 'join': await handle_choice(query, "Спільна біда об'єднує... (🤝+15, 🔥+5)", relationships=15, hope=5)
            elif choice == 'own_fire': await handle_choice(query, "Зараз кожен сам за себе. (🤝-5, 💡-5)", relationships=-5, resources=-5)
            elif choice == 'radio': await handle_choice(query, "Крізь шипіння ти чуєш уривки українських новин. Це дає надію. (🔥+15, 💡-2)", hope=15, resources=-2)
            await stages.stage_signal_hunt(query)
        
        elif stage_name == 'signalhunt':
            if choice == 'go':
                await handle_choice(query, "Ти добираєшся до місця. Десятки людей стоять з піднятими руками, намагаючись зловити сигнал. Ти зміг відправити одне повідомлення: 'Живий'. Але натовп помічає ворожий дрон. Починається обстріл. Ти ледь встигаєш втекти. (❤️-25, 🔥+20, 🤝+5)", health=-25, hope=20, relationships=5)
            elif choice == 'stay':
                await handle_choice(query, "Ти не ризикнув. Невідомість про долю рідних продовжує тебе мучити. (🔥-15)", hope=-15)
            await stages.stage_day13(query)

        elif stage_name == 'day13':
            if choice == 'hug': await handle_choice(query, "Мовчазна підтримка важить більше за слова. (🤝+15, 🔥+10)", relationships=15, hope=10)
            elif choice == 'tea': await handle_choice(query, "Маленький акт людяності. (💡-10, 🤝+10)", resources=-10, relationships=10)
            elif choice == 'rage': await handle_choice(query, "Твій гнів лякає її... (🔥-15, 🤝-10)", hope=-15, relationships=-10)
            await stages.stage_dramatheater(query) 

        elif stage_name == 'shelter':
            if choice == 'dramatheater':
                await query.message.reply_text("Ти вирішив йти до Драмтеатру. Ти дістався до нього. Там тисячі людей. Здається, це найбезпечніше місце у місті. 16 березня ти чуєш жахливий гул літака, а потім - вибух, що руйнує все навколо. Стеля обвалюється.")
                await stages.send_photo_from_path(query.message, assets.PHOTO_PATHS['dramtheater_after'])
                await stages.game_over(query, "Ти загинув під завалами Драмтеатру. Напис 'ДЕТИ' не врятував нікого.")
                return
            elif choice == 'artschool':
                await query.message.reply_text("Ти обрав Школу мистецтв. Там теж багато людей, переважно жінки та діти. 20 березня, коли ти знаходився у підвалі, росіяни скинули на школу бомбу.")
                await stages.send_photo_from_path(query.message, assets.PHOTO_PATHS['art_school_ruins'])
                await stages.game_over(query, "Ти загинув під завалами Школи мистецтв №12.")
                return
            elif choice == 'stay':
                await handle_choice(query, "Ти вирішив залишитися у своєму сховку. Це був правильний вибір. Через кілька днів ти дізнався, що і Драмтеатр, і Школу мистецтв розбомбили. Ти вижив, але ціною знання про загибель сотень інших.", hope=-25, suspicion=-3)
                await stages.stage_day18(query)

        elif stage_name == 'day18':
            if choice == 'snow': await handle_choice(query, "Ризик був величезний, але ти здобув воду. (❤️-20, 💡+15)", health=-20, resources=15)
            elif choice == 'basement': await handle_choice(query, "Безпечніше. Ти знаходиш трубу, що капає. (❤️-5, 💡+10)", health=-5, resources=10)
            elif choice == 'sleep': await handle_choice(query, "Зневоднення посилюється. (❤️-15, 💡+5)", health=-15, resources=5)
            await stages.stage_green_corridor(query)

        elif stage_name == 'corridor':
            if choice == 'go':
                await handle_choice(query, "Ваша колона рушає. Але за містом її починають розстрілювати з мінометів. Паніка, крики. Твоя машина пошкоджена. Ти дивом виживаєш, але змушений повернутися назад у пекло, втративши майже все.", health=-30, resources=-30, hope=-40)
            elif choice == 'stay':
                await handle_choice(query, "Ти не повірив окупантам і залишився. Пізніше ти дізнався, що колону розстріляли. Твоя недовіра врятувала тобі життя.", hope=10, suspicion=-2)
            await stages.stage_day32(query)
        
        elif stage_name == 'day32':
            state_manager.set_flag(user_id, 'met_azov', True)
            if choice == 'take_help': await handle_choice(query, "Вода і галети повертають тебе до життя. (❤️+15, 💡+10, 🔥+10)", health=15, resources=10, hope=10, suspicion=3)
            elif choice == 'blame': await handle_choice(query, "У його погляді втома і біль. (🤝-10, 🔥-10)", relationships=-10, hope=-10, suspicion=5)
            elif choice == 'give_info':
                await handle_choice(query, "Твоя інформація може врятувати життя. (🤝+10, 🔥+15)", relationships=10, hope=15, suspicion=10)
                state_manager.set_flag(user_id, 'helped_azov', True)
            await stages.stage_day45(query)
        elif stage_name == 'day45':
            if choice == 'orphan':
                await handle_choice(query, "Турбота про дитину повертає сенс... (🤝+20, 🔥+15)", relationships=20, hope=15)
                state_manager.set_flag(user_id, 'took_orphan', True)
            elif choice == 'read': await handle_choice(query, "Діти, що слухають казку - символ незламності. (🤝+10, 🔥+10)", relationships=10, hope=10)
            elif choice == 'avoid': await handle_choice(query, "Ти замикаєшся в собі. (🤝-15)", relationships=-15)
            await stages.stage_day60(query)
        elif stage_name == 'day60':
            if choice == 'believe': await handle_choice(query, "Надія - єдине, що залишилось. (🔥+20)", hope=20)
            elif choice == 'lose_faith': await handle_choice(query, "Ти бачив забагато брехні... (🔥-20)", hope=-20)
            elif choice == 'write_letter': await handle_choice(query, "Ти виливаєш свій біль на папір. (🔥-10)", hope=-10)
            await stages.stage_filtration1(query)
        elif stage_name == 'filtration1':
            if choice == 'relatives': await handle_choice(query, "", suspicion=1)
            elif choice == 'home': await handle_choice(query, "", suspicion=3)
            elif choice == 'end': await handle_choice(query, "", suspicion=0)
            await stages.stage_filtration2(query)
        elif stage_name == 'filtration2':
            state = state_manager.get_user_state(user_id)
            if choice == 'no':
                if state['met_azov']: await handle_choice(query, "Ти брешеш. Чи повірить він?", suspicion=2)
                else: await handle_choice(query, "Ти кажеш правду.", suspicion=0)
            elif choice == 'silence': await handle_choice(query, "Твоє мовчання красномовніше за слова.", suspicion=5)
            await stages.stage_filtration3(query)
        elif stage_name == 'filtration3':
            if choice == 'apolitical': await handle_choice(query, "", suspicion=0)
            elif choice == 'tragedy': await handle_choice(query, "", suspicion=2)
            elif choice == 'truth': await handle_choice(query, "Твоя відповідь сповнена ненависті...", suspicion=10)
            await stages.stage_filtration4(query)
        elif stage_name == 'filtration4':
            state = state_manager.get_user_state(user_id)
            if choice == 'clean':
                if not state['phone_cleaned']: await handle_choice(query, "Ти брешеш. Ти не мав часу його чистити.", suspicion=5)
                else: await handle_choice(query, "", suspicion=-2)
            elif choice == 'patriotic':
                if not state['phone_cleaned']: await handle_choice(query, "Він бачить фото... Це вирок.", suspicion=20)
                else: await handle_choice(query, "Він нічого не знаходить.", suspicion=-5)
            elif choice == 'lost': await handle_choice(query, "Найбільш підозріла відповідь.", suspicion=7)
            await stages.filtration_results(query)
        elif stage_name == 'epilogue':
            final_text = ""
            if choice == 'z_recover': final_text = "<b>Епілог: Вцілілий.</b>\nТи знайшов у собі сили жити далі..."
            elif choice == 'z_army': final_text = "<b>Епілог: Захисник.</b>\nТвій біль перетворився на лють..."
            elif choice == 'z_witness': final_text = "<b>Епілог: Свідок.</b>\nТи присвячуєш своє життя тому, щоб розповісти світові правду..."
            elif choice == 'e_escape': final_text = "<b>Епілог: В'язень, що біжить.</b>\nТи не здаєшся..."
            elif choice == 'e_wait': final_text = "<b>Епілог: Той, хто чекає.</b>\nТи затаївся, ставши тінню..."
            elif choice == 'e_keeper': final_text = "<b>Епілог: Хранитель.</b>\nСеред чужих ти знаходиш своїх..."
            await query.message.reply_text(final_text, parse_mode='HTML')
            await query.message.reply_text("Дякую за гру. Щоб почати знову, натисніть /start або /newgame")
