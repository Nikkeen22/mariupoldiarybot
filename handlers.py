# handlers.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

# Імпортуємо наші модулі
import stages
import state_manager
import assets

async def handle_choice(query, text_response, health=0, resources=0, relationships=0, hope=0, suspicion=0):
    """Універсальна функція для обробки вибору та оновлення стану."""
    user_id = query.from_user.id
    state_manager.update_stats(user_id, health, resources, relationships, hope, suspicion)
    if text_response:
        await query.message.reply_text(text_response, parse_mode='HTML')

# --- Обробники команд ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Надсилає вступне повідомлення, відео та кнопку для старту."""
    user = update.effective_user
    state_manager.reset_user_state(user.id)
    
    disclaimer_text = (
        "<b>Увага!</b>\n\n"
        "Ця інтерактивна історія заснована на реальних свідченнях людей, що пережили облогу Маріуполя. "
        "Її мета — не розважити, а зберегти пам'ять про трагедію та незламність українського духу.\n\n"
        "Історія може містити сцени, що емоційно важко сприймати."
    )
    await update.message.reply_html(disclaimer_text)

    try:
        with open(assets.VIDEO_PATH, 'rb') as video_file:
            await context.bot.send_video(chat_id=user.id, video=video_file, caption="Погляньте на те, що росія зробила з нашим містом.", supports_streaming=True)
    except Exception as e:
        print(f"Error sending local video: {e}.")
        await update.message.reply_text(f"Відео зруйнованого міста: {assets.VIDEO_URL}")

    keyboard = [[InlineKeyboardButton("Я готовий / готова почати", callback_data='intro_accept_start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Натисніть, щоб продовжити.", reply_markup=reply_markup)

async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    state = state_manager.get_user_state(user_id)
    
    suspicion = state.get('filtration_suspicion', 0)
  # отримаємо рівень підозрілості
    
    # Проста індикаторна оцінка
    if suspicion < 10:
        suspicion_status = "🟢 Низька"
    elif suspicion < 25:
        suspicion_status = "🟡 Помірна"
    elif suspicion < 50:
        suspicion_status = "🟠 Висока"
    else:
        suspicion_status = "🔴 Критична"
    
    status_text = (
        "<b>Ваш поточний стан:</b>\n\n"
        f"❤️ Здоров'я: {state['health']}/100\n"
        f"💡 Ресурси: {state['resources']}/100\n"
        f"🤝 Відносини: {state['relationships']}/100\n"
        f"🔥 Надія: {state['hope']}/100\n"
        f"⚠️ Підозрілість: {suspicion} ({suspicion_status})"
    )
    
    await update.message.reply_html(status_text)


# --- Головний обробник кнопок ---




async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    user_id = query.from_user.id
    data = query.data.split('_')
    action_type, stage_name, choice = query.data.split('_', 2)
    
    state = state_manager.get_user_state(user_id)
    if state['health'] <= 0:
        await stages.game_over(query, "Ви померли від ран, голоду та виснаження.")
        return
    if state['hope'] <= 0:
        await stages.game_over(query, "Ви втратили будь-яку надію і здалися.")
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
        # ... (попередні етапи залишаються без змін) ...
        if stage_name == 'day1':
            if choice == 'phone':
                await handle_choice(query, "📱 Ти бачиш новини... (💡-10, 🔥-10)", resources=-10, hope=-10)
            elif choice == 'suitcase':
                await handle_choice(query, "🎒 Ти дієш на інстинктах... (💡+5)", resources=5)
            elif choice == 'window':
                await handle_choice(query, "👀 Ти бачиш заграву... (❤️-10, 🔥-20)", health=-10, hope=-20)
            await stages.stage_day1_call(query)

        elif stage_name == 'day1call':
            if choice == 'calm':
                await handle_choice(query, "Твій спокій передається їм. (🤝+5, 🔥+3)", relationships=5, hope=3)
            elif choice == 'panic':
                await handle_choice(query, "Ваша розмова лише посилює паніку. (🤝-10, 🔥-10)", relationships=-10, hope=-10)
            elif choice == 'evacuate':
                await handle_choice(query, "Ідея про виїзд породжує безсилля. (💡-15, 🔥-25)", resources=-15, hope=-25)
            await stages.stage_day2(query)

        elif stage_name == 'day2':
            if choice == 'supermarket':
                await handle_choice(query, "Ти встигаєш схопити останні крупи... (💡+10)", resources=10)
            elif choice == 'atm':
                await handle_choice(query, "Вдається зняти кілька тисяч... (💡+5)", resources=7)
            elif choice == 'pharmacy':
                await handle_choice(query, "Найцінніша інвестиція. (❤️+3, 💡+7)", health=3, resources=7)
            await stages.stage_day5(query)

        elif stage_name == 'day5':
            if choice == 'join':
                await handle_choice(query, "Спільна біда об'єднує... (🤝+7, 🔥+3)", relationships=7, hope=3)
            elif choice == 'own_fire':
                await handle_choice(query, "Зараз кожен сам за себе. (🤝-10, 💡-10)", relationships=-10, resources=-10)
            elif choice == 'radio':
                await handle_choice(query, "Крізь шипіння ти чуєш уривки українських новин. Це дає надію. (🔥+15, 💡-10)", hope=15, resources=-10)
            await stages.stage_signal_hunt(query)

        elif stage_name == 'signalhunt':
            if choice == 'go':
                await handle_choice(query, "Ти добираєшся до місця. Десятки людей. Ти зміг відправити одне повідомлення: 'Живий'. Але натовп помічає ворожий дрон. Починається обстріл. Ти ледь встигаєш втекти. (❤️-40, 🔥+30, 🤝+10)", health=-40, hope=30, relationships=10)
            elif choice == 'stay':
                await handle_choice(query, "Ти не ризикнув. Невідомість про долю рідних продовжує тебе мучити. (🔥-45)", hope=-45)
            await stages.stage_m_sign(query)

        elif stage_name == 'msign':
            if choice == 'draw':
                await handle_choice(query, "Ви малюєте літеру. Можливо, це самообман, але він дає крихту спокою. (🔥+5)", hope=5)
            elif choice == 'refuse':
                await handle_choice(query, "Ти вважаєш це маркуванням цілі. Твоя недовіра до ворога сильніша за бажання примарної безпеки. (🔥-15, 🤝-20)", hope=-15, relationships=-20)
            await stages.stage_day12_respite(query)

        elif stage_name == 'day12':
            if choice == 'clean':
                state_manager.set_flag(user_id, 'phone_cleaned', True)
                await handle_choice(query, "Ти сидиш у темряві, видаляючи фото, листування, спогади. Частина твого життя зникає з екрану. Це боляче, але, можливо, це врятує тобі життя. (🔥-20)", hope=-20)
            elif choice == 'sleep':
                await handle_choice(query, "Тобі вдається провалитися у важкий, тривожний сон на кілька годин. Це не приносить радості, але відновлює трохи сил. (❤️+7, 🔥+3)", health=7, hope=3)
            elif choice == 'food':
                await handle_choice(query, "Ти ризикуєш. У сусідній покинутій квартирі ти знаходиш півпачки макаронів і банку консервів. Це справжній скарб. (💡+15, ❤️-15)", resources=15, health=-15)
            await stages.stage_day13(query)

        elif stage_name == 'day13':
            if choice == 'hug':
                await handle_choice(query, "Мовчазна підтримка важить більше за слова. (🤝+7, 🔥+5)", relationships=7, hope=5)
            elif choice == 'tea':
                await handle_choice(query, "Маленький акт людяності. (💡-15, 🤝+5)", resources=-15, relationships=5)
            elif choice == 'rage':
                await handle_choice(query, "Твій гнів лякає її... (🔥-25, 🤝-20)", hope=-25, relationships=-20)
            await stages.stage_wounded_neighbor(query)

        elif stage_name == 'wounded':
            if choice == 'help':
                await handle_choice(query, "Ти витрачаєш майже все, що мав, але рятуєш життя. (💡-40, ❤️-10, 🤝+50, 🔥+25)", resources=-40, health=-10, relationships=50, hope=25)
            elif choice == 'little':
                await handle_choice(query, "Ти допоміг, чим міг, але цього було замало. (💡-15, 🤝+10, 🔥-15)", resources=-10, relationships=10, hope=-10)
            elif choice == 'refuse':
                await handle_choice(query, "Ти проходиш повз. Вночі ти чуєш, як сусід помирає. (🤝-40, 🔥-30)", relationships=-40, hope=-30)
            await stages.stage_dramatheater(query)

        elif stage_name == 'shelter':
            if choice == 'dramatheater':
                await query.message.reply_text("Ти вирішив йти до Драмтеатру. 16 березня ти чуєш жахливий гул літака, а потім - вибух...")
                await stages.show_dramatheater_after(query)
                await stages.game_over(query, "Ти загинув під завалами Драмтеатру. Напис 'ДЕТИ' не врятував нікого.")
                return
            elif choice == 'artschool':
                await stages.game_over(query, "Ти обрав Школу мистецтв. 20 березня росіяни скинули на неї бомбу. Ти загинув під завалами.")
                return
            elif choice == 'stay':
                await handle_choice(query, "Ти вирішив залишитися. Пізніше ти дізнався, що і Драмтеатр, і Школу мистецтв розбомбили. Ти вижив, але ціною страшного знання.", hope=-20)
                await stages.stage_day18(query)

        elif stage_name == 'day18':
            if choice == 'snow':
                await handle_choice(query, "Ризик був величезний, але ти здобув воду. (❤️-40, 💡+15)", health=-40, resources=7)
            elif choice == 'basement':
                await handle_choice(query, "Безпечніше. Ти знаходиш трубу, що капає. (❤️-10, 💡+10)", health=-10, resources=5)
            elif choice == 'sleep':
                await handle_choice(query, "Зневоднення посилюється. (❤️-30, 💡+3)", health=-30, resources=3)
            await stages.stage_green_corridor(query)

        elif stage_name == 'corridor':
            if choice == 'go':
                await handle_choice(query, "За містом колону розстрілюють. Твоя машина пошкоджена. Ти дивом виживаєш, але змушений повернутися назад у пекло. (❤️-60, 💡-60, 🔥-80)", health=-60, resources=-60, hope=-80)
            elif choice == 'stay':
                await handle_choice(query, "Ти не повірив окупантам і залишився. Пізніше ти дізнався, що колону розстріляли. Твоя недовіра врятувала тобі життя.", hope=10)
            await stages.stage_day25(query)

        elif stage_name == 'day25':
            if choice == 'roof':
                await handle_choice(query, "Перебираючись по хиткому даху під звуки стрілянини, ти зриваєшся. Падіння було не дуже високим, але нога зламана. (❤️-80, 🔥-40)", health=-80, hope=-40)
            elif choice == 'entrance':
                await handle_choice(query, "Ти накидаєш білу тканину і біжиш. Російський солдат бачить тебе. Він вагається, але не стріляє. Ти пробігаєш повз, не дихаючи. (❤️-20, 🔥+20)", health=-20, hope=20, suspicion=6)
            elif choice == 'flooded_basement':
                await handle_choice(query, "Ти спускаєшся у крижану воду. Ти сидиш там годинами, поки пожежа не вщухне. Ти вижив, але сильно замерз і втратив частину речей. (❤️-50, 💡-20)", health=-50, resources=-20)
            await stages.stage_day32(query)

        elif stage_name == 'day32':
            state_manager.set_flag(user_id, 'met_azov', True)
            if choice == 'take_help':
                await handle_choice(query, "Вода і галети повертають тебе до життя. (❤️+7, 💡+10, 🔥+5)", health=7, resources=10, hope=5, suspicion=3)
            elif choice == 'blame':
                await handle_choice(query, "У його погляді втома і біль. (🤝-20, 🔥-20)", relationships=-20, hope=-20, suspicion=0)
            elif choice == 'give_info':
                await handle_choice(query, "Твоя інформація може врятувати життя. (🤝+5, 🔥+7)", relationships=5, hope=7, suspicion=6)
                state_manager.set_flag(user_id, 'helped_azov', True)
            await stages.stage_day45(query)

        elif stage_name == 'day45':
            if choice == 'orphan':
                await handle_choice(query, "Турбота про дитину повертає сенс... (🤝+10, 🔥+10)", relationships=10, hope=10)
                state_manager.set_flag(user_id, 'took_orphan', True)
            elif choice == 'read':
                await handle_choice(query, "Діти, що слухають казку - символ незламності. (🤝+5, 🔥+5)", relationships=5, hope=5)
            elif choice == 'avoid':
                await handle_choice(query, "Ти замикаєшся в собі. (🤝-30)", relationships=-30)
            await stages.stage_day60(query)

        elif stage_name == 'day60':
            if choice == 'believe':
                await handle_choice(query, "Надія - єдине, що залишилось. (🔥+10)", hope=10)
            elif choice == 'lose_faith':
                await handle_choice(query, "Ти бачив забагато брехні... (🔥-40)", hope=-40)
            elif choice == 'write_letter':
                await handle_choice(query, "Ти виливаєш свій біль на папір. (🔥-20)", hope=-20)
            await stages.stage_filtration1(query)
           
# --- Ланцюжок фільтрації (виправлена версія) ---

        elif stage_name == 'filtration1':
            if choice == 'relatives': await handle_choice(query, "", suspicion=1)  # було 1
            elif choice == 'home': await handle_choice(query, "Він зневажливо хмикає.", suspicion=5)  # було 2 (раніше 3)
            elif choice == 'end': await handle_choice(query, "", suspicion=-3)
            await stages.stage_filtration2(query)

        elif stage_name == 'filtration2':
            if choice == 'no':
                if state.get('met_azov'): await handle_choice(query, "Ти брешеш. Чи повірить він?", suspicion=2)  # було 2 (раніше 3)
                else: await handle_choice(query, "Ти кажеш правду.", suspicion=0)
            elif choice == 'silence': await handle_choice(query, "Твоє мовчання красномовніше за слова.", suspicion=3)  # було 3 (раніше 5)
            await stages.stage_filtration10(query)

        elif stage_name == 'filtration10':
            if choice == 'teacher': await handle_choice(query, "'Вчили дітей ненавидіти росію?' - питає він.", suspicion=0)  # було 1 (раніше 2)
            elif choice == 'unemployed': await handle_choice(query, "Він дивиться на тебе з підозрою. 'Чим заробляв?'", suspicion=1)  # було 2 (раніше 3)
            elif choice == 'volunteer': await handle_choice(query, "Це слово для них - як червона ганчірка для бика.", suspicion=4)  # було 5 (раніше 8)
            await stages.stage_filtration11(query)

        elif stage_name == 'filtration11':
            if choice == 'no': await handle_choice(query, "Це підозріло в сучасному світі. 'Брешеш'.", suspicion=3)  # було 2 (раніше 3)
            elif choice == 'passive': await handle_choice(query, "Найбезпечніший варіант.", suspicion=-3)
            elif choice == 'active': await handle_choice(query, "Він робить позначку. Вони обов'язково перевірять.", suspicion=4)  # було 5 (раніше 8)
            await stages.stage_filtration3(query)

        elif stage_name == 'filtration3':
            if choice == 'apolitical': await handle_choice(query, "", suspicion=-1)
            elif choice == 'tragedy': await handle_choice(query, "Його обличчя не виражає нічого.", suspicion=1)  # було 1 (раніше 2)
            elif choice == 'truth': await handle_choice(query, "Твоя відповідь сповнена ненависті. Він це бачить.", suspicion=4)  # було 5 (раніше 10)
            await stages.stage_filtration_pressure(query)

        elif stage_name == 'filtrationpressure':
            if choice == 'family': await handle_choice(query, "", suspicion=3)  # було 1
            elif choice == 'scared': await handle_choice(query, "", suspicion=-2)  # було -3 (раніше -2), більше зниження
            elif choice == 'enemy': await handle_choice(query, "Твоя непокора не залишиться непоміченою.", suspicion=15)  # було 5 (раніше 10)
            await stages.stage_filtration4(query)

        elif stage_name == 'filtration4':
            phone_is_actually_clean = state.get('phone_cleaned', False)

            if choice == 'clean':
                if phone_is_actually_clean:
                    await handle_choice(query, "Він довго гортає порожній телефон. 'Дуже підозріло,' - каже він, але доказів немає.", suspicion=4)  # було -1 (раніше -2)
                else:
                    await handle_choice(query, "Ти кажеш, що телефон чистий, але він знаходить компрометуючі фото та переписки. Твоя брехня лише погіршує ситуацію.", suspicion=5)  # було 10 (раніше 15)
            
            elif choice == 'patriotic':
                if phone_is_actually_clean:
                    await handle_choice(query, "Ти віддаєш телефон, заявляючи, що там 'контент'. Він нічого не знаходить і здивовано дивиться на тебе. 'Дивак'. Твоя дивна поведінка викликає підозру.", suspicion=1)  # було 2 (раніше 3)
                else:
                    await handle_choice(query, "Ти чесно віддаєш телефон. Він бачить фото, новини, переписки... 'Все з тобою зрозуміло'. Це вирок.", suspicion=10)  # було 15 (раніше 20)
            
            elif choice == 'lost':
                await handle_choice(query, "Найбільш підозріла відповідь. 'Звісно, загубив'.", suspicion=3)  # було 5 (раніше 7)
            
            await stages.filtration_results(query)



        elif stage_name == 'epilogue':
            final_text = ""
            if choice == 'z_recover': final_text = "<b>Епілог: Вцілілий.</b>\nТи пройшов крізь пекло і вижив. Ти знаходиш у собі сили жити далі, заради тих, хто не зміг. Твоє життя - це пам'ять."
            elif choice == 'z_army': final_text = "<b>Епілог: Захисник.</b>\nТвій біль перетворився на лють. Ти береш до рук зброю, щоб Маріуполь більше ніколи не повторився."
            elif choice == 'z_witness': final_text = "<b>Епілог: Свідок.</b>\nТвій обов'язок - говорити. Ти присвячуєш своє життя тому, щоб розповісти світові правду про те, що сталося в місті Марії."
            elif choice == 'e_escape': final_text = "<b>Епілог: В'язень, що біжить.</b>\nТи не здаєшся. Навіть у сибірській глушині ти шукаєш шлях додому. Боротьба триває."
            elif choice == 'e_wait': final_text = "<b>Епілог: Той, хто чекає.</b>\nТи затаївся, ставши тінню. Ти чекаєш. На звільнення, на перемогу, на шанс повернутися."
            elif choice == 'e_keeper': final_text = "<b>Епілог: Хранитель.</b>\nСеред чужих ти знаходиш своїх. Ви тримаєтеся разом, підтримуючи один в одному вогонь України, який нікому не згасити."
            
            await query.message.reply_text(final_text, parse_mode='HTML')
            await query.message.reply_text("Дякую за гру. Маріуполь. Місто, яке боролося.\n\nЩоб почати знову, натисніть /start або /newgame")