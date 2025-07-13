# stages.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import assets

async def send_stage(query, text, keyboard):
    """Універсальна функція для надсилання нового етапу."""
    await query.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def game_over(query, reason):
    await query.message.reply_text(f"<b>Гру закінчено.</b>\n{reason}\n\nЩоб почати знову, натисніть /start або /newgame", parse_mode='HTML')

async def send_photo_from_path(message, path, caption=""):
    """Надсилає фото з локального шляху, обробляючи помилки."""
    try:
        with open(path, 'rb') as photo_file:
            await message.reply_photo(photo=photo_file, caption=caption)
    except FileNotFoundError:
        print(f"Photo not found at {path}. Skipping.")
    except Exception as e:
        print(f"Error sending photo from {path}: {e}")

# --- СЦЕНИ ГРИ (ОНОВЛЕНІ) ---

async def stage_day1(query):
    text = "<b>День 1 — 24 лютого</b>\n\n5:00 ранку. Вибух. Глибший, страшніший. Це повномасштабне вторгнення."
    keyboard = [
        [InlineKeyboardButton("📱 Перевірити телефон", callback_data='act_day1_phone')],
        [InlineKeyboardButton("🎒 Схопити 'тривожну валізку'", callback_data='act_day1_suitcase')],
        [InlineKeyboardButton("👀 Виглянути у вікно", callback_data='act_day1_window')],
    ]
    await send_stage(query, text, keyboard)

async def stage_day1_call(query):
    text = "Минає хвилина... Перша свідома думка — батьки. З десятої спроби ти чуєш рідний голос.\n\n<b>Мати:</b> 'Синку/Донько! Ви живі?'"
    keyboard = [
        [InlineKeyboardButton("🗣️ 'Я в порядку. Без паніки.'", callback_data='act_day1call_calm')],
        [InlineKeyboardButton("🗣️ 'Не знаю! Війна!'", callback_data='act_day1call_panic')],
        [InlineKeyboardButton("🗣️ 'Збирайте речі!'", callback_data='act_day1call_evacuate')],
    ]
    await send_stage(query, text, keyboard)
    
async def stage_day2(query):
    text = "Це остання спокійна розмова на довгі тижні.\n\n<b>День 2 — 25 лютого</b>\n\nМісто гуде. Запаси — це життя."
    keyboard = [
        [InlineKeyboardButton("🛒 Піти в супермаркет", callback_data='act_day2_supermarket')],
        [InlineKeyboardButton("🏧 Піти зняти готівку", callback_data='act_day2_atm')],
        [InlineKeyboardButton("💊 Піти в аптеку", callback_data='act_day2_pharmacy')],
    ]
    await send_stage(query, text, keyboard)
    
async def stage_day5(query):
    text = "<b>День 5 — 2 березня</b>\n\nЗв'язок зникає. Місто повністю оточене. Ти один. У дворі сусіди розводять багаття, щоб приготувати їжу з того, що знайшли."
    await send_photo_from_path(query.message, assets.PHOTO_PATHS['cooking_outside'], "Люди готують їжу на вогні біля розбитих будинків.")
    
    keyboard = [
        [InlineKeyboardButton("🤝 Приєднатися, принести продукти", callback_data='act_day5_join')],
        [InlineKeyboardButton("🔥 Розвести власне багаття", callback_data='act_day5_own_fire')],
        [InlineKeyboardButton("📻 Спробувати зловити радіосигнал", callback_data='act_day5_radio')],
    ]
    await send_stage(query, text, keyboard)

async def stage_signal_hunt(query):
    text = "<b>День 9 — 6 березня</b>\n\nЗв'язку немає зовсім. Але містом шириться чутка, що біля ТЦ 'Порт-Сіті' іноді з'являється слабкий сигнал. Це шанс подзвонити рідним, але йти туди — величезний ризик."
    await send_photo_from_path(query.message, assets.PHOTO_PATHS['signal_hunt'], "Люди відчайдушно намагаються зловити сигнал.")

    keyboard = [
        [InlineKeyboardButton("🚶 Йти до 'Порт-Сіті' (Великий ризик)", callback_data='act_signalhunt_go')],
        [InlineKeyboardButton("🏠 Залишитися. Це занадто небезпечно", callback_data='act_signalhunt_stay')],
    ]
    await send_stage(query, text, keyboard)

async def stage_m_sign(query):
    text = "<b>День 11 — 8 березня</b>\n\nСусід пропонує намалювати на стіні будинку велику літеру 'М', щоб позначити, що тут мирні жителі. Дехто каже, що це може врятувати, інші — що це лише приверне увагу мародерів або стане мішенню для росіян, які не розбирають."
    await send_photo_from_path(query.message, assets.PHOTO_PATHS['m_sign'], "Позначка, що мала б рятувати.")
    keyboard = [
        [InlineKeyboardButton("👍 Погодитись і допомогти намалювати", callback_data='act_msign_draw')],
        [InlineKeyboardButton("👎 Відмовитися. Це погана ідея", callback_data='act_msign_refuse')],
    ]
    await send_stage(query, text, keyboard)

# НОВА СЦЕНА
async def stage_day12_respite(query):
    text = "<b>День 12 — 9 березня</b>\n\nНастала тимчасова, моторошна тиша. Обстріли стихли. Це рідкісний шанс зробити щось важливе для виживання."
    keyboard = [
        [InlineKeyboardButton("📲 Почистити телефон від 'небезпечного' контенту", callback_data='act_day12_clean')],
        [InlineKeyboardButton("😴 Спробувати поспати, відновити сили", callback_data='act_day12_sleep')],
        [InlineKeyboardButton("🍲 Ризикнути і пошукати їжу в покинутих квартирах", callback_data='act_day12_food')],
    ]
    await send_stage(query, text, keyboard)

async def stage_day13(query):
    text = "<b>День 13 — 9 березня</b>\n\nГучний свист, вибух. Скинули авіабомбу на пологовий. У під'їзді ховається молода жінка, яка мала народжувати там. Вона мовчки плаче."
    keyboard = [
        [InlineKeyboardButton("🫂 Обійняти її і сидіти поруч", callback_data='act_day13_hug')],
        [InlineKeyboardButton("☕ Заварити їй останній чай", callback_data='act_day13_tea')],
        [InlineKeyboardButton("🤬 Висловити свій гнів і безсилля", callback_data='act_day13_rage')],
    ]
    await send_stage(query, text, keyboard)

async def stage_wounded_neighbor(query):
    text = "<b>День 15 — 11 березня</b>\n\nПід час чергового обстрілу уламок поранив вашого сусіда в ногу. Крові багато. Він просить допомоги. У вас є трохи перев'язувальних матеріалів з аптечки та чиста вода, але це майже останні ваші запаси."
    await send_photo_from_path(query.message, assets.PHOTO_PATHS['wounded_neighbor'], "Кожен вибір має ціну.")
    keyboard = [
        [InlineKeyboardButton("🩹 Віддати все і допомогти", callback_data='act_wounded_help')],
        [InlineKeyboardButton("💧 Дати лише трохи води", callback_data='act_wounded_little')],
        [InlineKeyboardButton("🤐 Сказати, що у вас нічого немає", callback_data='act_wounded_refuse')],
    ]
    await send_stage(query, text, keyboard)

async def stage_dramatheater(query):
    text = "<b>16 березня.</b>\n\nПо місту йде чутка, що найбезпечніші місця — це великі підвали. Два найбільших — у Драмтеатрі та у Школі мистецтв №12. Куди спробувати дістатися?"
    await send_photo_from_path(query.message, assets.PHOTO_PATHS['dramtheater_before'], "Драматичний театр. Серце Маріуполя до вторгнення.")

    keyboard = [
        [InlineKeyboardButton("🎭 Йти до Драмтеатру", callback_data='act_shelter_dramatheater')],
        [InlineKeyboardButton("🎨 Йти до Школи мистецтв", callback_data='act_shelter_artschool')],
        [InlineKeyboardButton("🏠 Залишитися у своєму сховку", callback_data='act_shelter_stay')],
    ]
    await send_stage(query, text, keyboard)

async def show_dramatheater_after(query):
    """Надсилає фото розбомбленого театру."""
    await send_photo_from_path(query.message, assets.PHOTO_PATHS['dramtheater_after'])

async def stage_day18(query):
    text = "<b>День 18 — 14 березня</b>\n\nВода закінчилася. Повна знемога. Люди зливають залишки з труб опалення, збирають воду з калюж. Єдиний шанс — розтопити брудний сніг у дворі або спуститись у темний підвал."
    keyboard = [
        [InlineKeyboardButton("❄️ Збирати сніг у дворі (Ризик)", callback_data='act_day18_snow')],
        [InlineKeyboardButton("🔧 Спускатися в темний підвал", callback_data='act_day18_basement')],
        [InlineKeyboardButton("😴 Лягти і спробувати заснути", callback_data='act_day18_sleep')],
    ]
    await send_stage(query, text, keyboard)

async def stage_green_corridor(query):
    text = "<b>21 березня.</b>\n\nЗ'являється інформація про 'зелений коридор' для евакуації. Люди формують колони, маркують машини білими стрічками та написами 'ДІТИ'. Але чи можна вірити окупантам?"
    await send_photo_from_path(query.message, assets.PHOTO_PATHS['green_corridor'], "Дорога, що мала стати порятунком.")

    keyboard = [
        [InlineKeyboardButton("🚗 Спробувати виїхати в колоні", callback_data='act_corridor_go')],
        [InlineKeyboardButton(" distrust Залишитися. Це пастка", callback_data='act_corridor_stay')],
    ]
    await send_stage(query, text, keyboard)
    
# ОНОВЛЕНА СЦЕНА
async def stage_day25(query):
    text = "<b>День 25 — 21 березня</b>\n\nВуличні бої. Твій район перетворився на лінію фронту. Ти чуєш російську мову зовсім поруч. Твій будинок починає горіти після влучання снаряда. Треба тікати."
    keyboard = [
        [InlineKeyboardButton("🏃 Через дах на сусідній будинок", callback_data='act_day25_roof')],
        [InlineKeyboardButton("💨 Через задимлений під'їзд (з білою стрічкою)", callback_data='act_day25_entrance')],
        [InlineKeyboardButton("💧 Спуститися в затоплений підвал", callback_data='act_day25_flooded_basement')],
    ]
    await send_stage(query, text, keyboard)

async def stage_day32(query):
    text = "<b>День 32 — 28 березня</b>\n\nТи ховаєшся в руїнах. Раптом бачиш українських військових з 'Азову'. Один помічає тебе.\n\n<b>Боєць:</b> 'Цивільний? Тримайся. У нас є трохи галет і води.'"
    keyboard = [
        [InlineKeyboardButton("🙏 Взяти допомогу", callback_data='act_day32_take_help')],
        [InlineKeyboardButton("🗣️ 'Чому ви не врятували місто?'", callback_data='act_day32_blame')],
        [InlineKeyboardButton("🗺️ 'Я знаю короткий шлях...'", callback_data='act_day32_give_info')],
    ]
    await send_stage(query, text, keyboard)
    
async def stage_day45(query):
    text = "<b>День 45 — 10 квітня</b>\n\nТи дістався до бункера біля 'Азовсталі'. Тут сотні людей. Повітря важке, але тут не вбивають бомби."
    await send_photo_from_path(query.message, assets.PHOTO_PATHS['azovstal'], "Прохідна комбінату 'Азовсталь'. Фортеця надії та болю.")
    
    keyboard = [
        [InlineKeyboardButton("🤝 Взяти під опіку дитину-сироту", callback_data='act_day45_orphan')],
        [InlineKeyboardButton("📖 Читати дітям знайдену книгу", callback_data='act_day45_read')],
        [InlineKeyboardButton("😔 Уникати чужих поглядів", callback_data='act_day45_avoid')],
    ]
    await send_stage(query, text, keyboard)
    
async def stage_day60(query):
    text = "<b>День 60 — 25 квітня</b>\n\nПочинаються переговори про евакуацію цивільних. Перший промінь надії. Але росіяни постійно зривають домовленості."
    keyboard = [
        [InlineKeyboardButton("🔥 Вірити до останнього", callback_data='act_day60_believe')],
        [InlineKeyboardButton("😒 Втратити віру", callback_data='act_day60_lose_faith')],
        [InlineKeyboardButton("✍️ Написати прощального листа", callback_data='act_day60_write_letter')],
    ]
    await send_stage(query, text, keyboard)

async def stage_filtration1(query):
    text = "<b>День 70. Фільтраційний табір.</b>\nТи в черзі до намету для допитів. За столом офіцер ФСБ.\n\n<b>Офіцер:</b> 'Мета виїзду на територію, підконтрольну київському режиму?'"
    keyboard = [
        [InlineKeyboardButton("🗣️ 'Там мої родичі'", callback_data='act_filtration1_relatives')],
        [InlineKeyboardButton("🗣️ 'Я їду в Україну. Це мій дім'", callback_data='act_filtration1_home')],
        [InlineKeyboardButton("🗣️ 'Просто хочу, щоб це скінчилося'", callback_data='act_filtration1_end')],
    ]
    await send_stage(query, text, keyboard)

async def stage_filtration2(query):
    text = "<b>Офіцер:</b> 'Родичі, знайомі у ЗСУ, поліції, батальйоні Азов?'"
    keyboard = [
        [InlineKeyboardButton("🗣️ 'Ні, нікого немає'", callback_data='act_filtration2_no')],
        [InlineKeyboardButton(" мов 'Мовчати'", callback_data='act_filtration2_silence')],
    ]
    await send_stage(query, text, keyboard)

# СЦЕНУ З ТАТУ ВИДАЛЕНО

async def stage_filtration10(query):
    text = "<b>Офіцер:</b> 'Чим ви займались у Маріуполі?'"
    keyboard = [
        [InlineKeyboardButton("🗣️ Працював(ла) в школі", callback_data='act_filtration10_teacher')],
        [InlineKeyboardButton("🗣️ Був(ла) безробітним(ою)", callback_data='act_filtration10_unemployed')],
        [InlineKeyboardButton("🗣️ Волонтерив(ла)", callback_data='act_filtration10_volunteer')],
    ]
    await send_stage(query, text, keyboard)

async def stage_filtration11(query):
    text = "<b>Офіцер:</b> 'Чи маєте акаунти в соцмережах?'"
    keyboard = [
        [InlineKeyboardButton("🗣️ Ні", callback_data='act_filtration11_no')],
        [InlineKeyboardButton("🗣️ Так, але не публікую нічого", callback_data='act_filtration11_passive')],
        [InlineKeyboardButton("🗣️ Так, я писав(ла) про війну", callback_data='act_filtration11_active')],
    ]
    await send_stage(query, text, keyboard)

async def stage_filtration3(query):
    text = "<b>Офіцер:</b> 'Як ставитеся до проведення СВО?'"
    keyboard = [
        [InlineKeyboardButton("🗣️ 'Я не розбираюся в політиці'", callback_data='act_filtration3_apolitical')],
        [InlineKeyboardButton("🗣️ 'Це трагедія для всіх нас'", callback_data='act_filtration3_tragedy')],
        [InlineKeyboardButton("🗣️ 'Ви зруйнували моє місто'", callback_data='act_filtration3_truth')],
    ]
    await send_stage(query, text, keyboard)

async def stage_filtration_pressure(query):
    text = "<b>Офіцер (пильно дивлячись):</b> 'Чому не поїхали в росію? Там безпечно, вам би допомогли. В Україні на вас ніхто не чекає.'"
    keyboard = [
        # Змінюємо 'filtration_pressure' на 'filtrationpressure'
        [InlineKeyboardButton("🗣️ 'Там вся моя родина'", callback_data='act_filtrationpressure_family')],
        [InlineKeyboardButton("🗣️ 'Я боявся їхати в невідомість'", callback_data='act_filtrationpressure_scared')],
        [InlineKeyboardButton("🗣️ 'Бо росія - ворог'", callback_data='act_filtrationpressure_enemy')],
    ]
    await send_stage(query, text, keyboard)

async def stage_filtration4(query):
    text = "Він простягає руку.\n\n<b>Офіцер:</b> 'Телефон'."
    keyboard = [
        [InlineKeyboardButton("📲 Віддати почищений телефон", callback_data='act_filtration4_clean')],
        [InlineKeyboardButton("📲 Віддати телефон з контентом", callback_data='act_filtration4_patriotic')],
        [InlineKeyboardButton("🗣️ 'Я його загубив(ла)'", callback_data='act_filtration4_lost')],
    ]
    await send_stage(query, text, keyboard)

async def filtration_results(query):
    from state_manager import get_user_state
    user_id = query.from_user.id
    state = get_user_state(user_id)
    score = state['filtration_suspicion']

    if score >= 15:
        await game_over(query, "<b>Результат: Зникнення.</b>\nОфіцер каже: 'Пройдемо зі мною'. Тебе ведуть до іншого намету. Більше тебе ніхто не бачив.")
    elif 8 <= score < 15:
        await query.message.reply_text("<b>Результат: Депортація.</b>\nТебе садять в інший автобус і везуть вглиб росії.", parse_mode='HTML')
        await epilogue_exile(query)
    else:
        await query.message.reply_text("<b>Результат: Успіх.</b>\nТебе випускають і садять в автобус до Запоріжжя.", parse_mode='HTML')
        await epilogue_zaporizhzhia(query)

async def epilogue_zaporizhzhia(query):
    text = "<b>Запоріжжя.</b> Волонтер дає тобі тарілку гарячого борщу. Це смак забутого життя. Що далі?"
    keyboard = [
        [InlineKeyboardButton("❤️‍🩹 Відновитися і почати спочатку", callback_data='act_epilogue_z_recover')],
        [InlineKeyboardButton("🎖️ Приєднатися до Збройних Сил", callback_data='act_epilogue_z_army')],
        [InlineKeyboardButton("🤝 Стати голосом Маріуполя", callback_data='act_epilogue_z_witness')],
    ]
    await send_stage(query, text, keyboard)
    
async def epilogue_exile(query):
    text = "<b>Сибір.</b> Ти у в'язниці без ґрат. Що далі?"
    keyboard = [
        [InlineKeyboardButton("🏃 Спланувати втечу", callback_data='act_epilogue_e_escape')],
        [InlineKeyboardButton("🕊️ Затаїтися і чекати", callback_data='act_epilogue_e_wait')],
        [InlineKeyboardButton("🫂 Шукати своїх", callback_data='act_epilogue_e_keeper')],
    ]
    await send_stage(query, text, keyboard)