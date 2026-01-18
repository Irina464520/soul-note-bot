from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from keyboards.main_menu import get_main_menu

# Состояния для дневника
class MoodStates(StatesGroup):
    waiting_for_mood = State()      # Ждем оценку настроения
    waiting_for_note = State()      # Ждем описание (опционально)
    waiting_for_tags = State()      # Ждем теги (опционально)
    confirmation = State()          # Подтверждение сохранения

# Клавиатура для оценки настроения
def get_mood_keyboard():
    builder = ReplyKeyboardBuilder()
    
    # Шкала настроения с эмодзи
    moods = [
        ("1 😔", "1"),
        ("2 🙁", "2"), 
        ("3 😐", "3"),
        ("4 🙂", "4"),
        ("5 😊", "5"),
        ("6 🤩", "6"),
        ("7 🌈", "7"),
        ("8 ✨", "8"),
        ("9 🌟", "9"),
        ("10 💫", "10")
    ]
    
    # Добавляем кнопки по 2 в ряд
    for i in range(0, len(moods), 2):
        row = moods[i:i+2]
        builder.row(
            types.KeyboardButton(text=row[0][0]),
            types.KeyboardButton(text=row[1][0]) if len(row) > 1 else None
        )
    
    builder.row(types.KeyboardButton(text="🚫 Отмена"))
    builder.row(types.KeyboardButton(text="🏠 Главное меню"))
    
    return builder.as_markup(resize_keyboard=True)

# Клавиатура для пропуска
def get_skip_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="⏭ Пропустить"))
    builder.row(types.KeyboardButton(text="🚫 Отмена"))
    builder.row(types.KeyboardButton(text="🏠 Главное меню"))
    return builder.as_markup(resize_keyboard=True)

# Начинаем запись настроения
async def start_mood_entry(message: types.Message, state: FSMContext):
    await message.answer(
        "📓 *Запись настроения*\n\n"
        "Как ты себя чувствуешь сегодня?\n"
        "Оцени по шкале от 1 до 10:",
        parse_mode="Markdown",
        reply_markup=get_mood_keyboard()
    )
    await state.set_state(MoodStates.waiting_for_mood)
    await state.update_data(selected_tags=[])  # Инициализируем пустой список тегов

# Обработчик выбора настроения
async def process_mood(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await return_to_main_menu(message, state)
        return
        
    if message.text == "🚫 Отмена":
        await cancel_mood_entry(message, state)
        return
    
    # Извлекаем число из текста (например, "5 😊" -> "5")
    mood_text = message.text.split()[0] if message.text else ""
    
    if mood_text.isdigit() and 1 <= int(mood_text) <= 10:
        await state.update_data(mood=int(mood_text))
        
        await message.answer(
            f"Записал настроение: {mood_text}/10\n\n"
            "Хочешь добавить описание дня?\n"
            "(Что произошло, что чувствуешь, мысли)",
            reply_markup=get_skip_keyboard()
        )
        await state.set_state(MoodStates.waiting_for_note)
    else:
        await message.answer("Пожалуйста, выбери оценку из клавиатуры")

# Обработчик описания
async def process_note(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await return_to_main_menu(message, state)
        return
        
    if message.text == "⏭ Пропустить":
        await state.update_data(note=None)
        await ask_for_tags(message, state)
    elif message.text == "🚫 Отмена":
        await cancel_mood_entry(message, state)
    else:
        await state.update_data(note=message.text)
        await ask_for_tags(message, state)

# Спрашиваем теги
async def ask_for_tags(message: types.Message, state: FSMContext):
    tags_keyboard = ReplyKeyboardBuilder()
    
    # Теги как слова (без #)
    tags_rows = [
        ["Работа", "Учёба", "Финансы"],
        ["Семья", "Друзья", "Отношения"],
        ["Здоровье", "Сон", "Спорт"],
        ["Стресс", "Тревога", "Усталость"],
        ["Радость", "Спокойствие", "Вдохновение"],
        ["Природа", "Хобби", "Творчество"],
        ["Успех", "Цели", "Рост"],
        ["Одиночество", "Конфликт", "Перемены"],
        ["Благодарность", "Любовь", "Надежда"]
    ]
    
    # Добавляем теги по строкам
    for row in tags_rows:
        row_buttons = []
        for tag in row:
            row_buttons.append(types.KeyboardButton(text=tag))
        tags_keyboard.row(*row_buttons)
    
    # Кнопки управления
    tags_keyboard.row(
        types.KeyboardButton(text="✅ Готово"),
        types.KeyboardButton(text="⏭ Без тегов")
    )
    tags_keyboard.row(
        types.KeyboardButton(text="🚫 Отмена"),
        types.KeyboardButton(text="🏠 Главное меню")
    )
    
    # Получаем уже выбранные теги
    data = await state.get_data()
    selected_tags = data.get('selected_tags', [])
    
    instruction = (
        "🏷️ *Выбери темы, которые описывают твой день:*\n\n"
        "Можно выбрать несколько — просто нажимай на кнопки.\n"
        f"Выбрано: {', '.join(selected_tags) if selected_tags else 'пока ничего'}\n\n"
        "Когда закончишь, нажми *✅ Готово*"
    )
    
    await message.answer(
        instruction,
        parse_mode="Markdown",
        reply_markup=tags_keyboard.as_markup(resize_keyboard=True)
    )
    await state.set_state(MoodStates.waiting_for_tags)

# Обработчик тегов
async def process_tags(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await return_to_main_menu(message, state)
        return
        
    data = await state.get_data()
    selected_tags = data.get('selected_tags', [])
    
    # Кнопки управления
    if message.text == "✅ Готово":
        await state.update_data(tags=selected_tags)
        await show_preview_and_save(message, state)
            
    elif message.text == "⏭ Без тегов":
        await state.update_data(tags=[])
        await show_preview_and_save(message, state)
        
    elif message.text == "🚫 Отмена":
        await cancel_mood_entry(message, state)
        
    else:
        # Пользователь выбрал тег
        if message.text not in selected_tags:
            selected_tags.append(message.text)
            await state.update_data(selected_tags=selected_tags)
            
            # Показываем обновленную клавиатуру
            await ask_for_tags(message, state)

# Показываем превью перед сохранением
async def show_preview_and_save(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    # Показываем превью
    mood_emoji = {
        1: "😔", 2: "🙁", 3: "😐", 4: "🙂",
        5: "😊", 6: "🤩", 7: "🌈", 8: "✨",
        9: "🌟", 10: "💫"
    }
    
    mood_score = data.get('mood', 5)
    emoji = mood_emoji.get(mood_score, "😐")
    
    preview_text = (
        f"✨ *Проверь запись:*\n\n"
        f"{emoji} *Настроение:* {mood_score}/10\n"
        f"📝 *Описание:* {data.get('note', 'не указано')}\n"
        f"🏷️ *Теги:* {', '.join(data.get('tags', ['нет']))}\n\n"
        f"Всё верно?"
    )
    
    # Клавиатура подтверждения
    confirm_keyboard = ReplyKeyboardBuilder()
    confirm_keyboard.row(
        types.KeyboardButton(text="✅ Да, сохранить"),
        types.KeyboardButton(text="✏️ Редактировать")
    )
    confirm_keyboard.row(
        types.KeyboardButton(text="🚫 Отменить"),
        types.KeyboardButton(text="🏠 Главное меню")
    )
    
    await message.answer(
        preview_text,
        parse_mode="Markdown",
        reply_markup=confirm_keyboard.as_markup(resize_keyboard=True)
    )
    await state.set_state(MoodStates.confirmation)

# Обработчик подтверждения
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await return_to_main_menu(message, state)
        return
        
    if message.text == "✅ Да, сохранить":
        data = await state.get_data()
        
        # Сохраняем в файл
        with open("mood_diary.txt", "a", encoding="utf-8") as f:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} | {message.from_user.id} | ")
            f.write(f"Настроение: {data.get('mood', '?')}/10 | ")
            f.write(f"Описание: {data.get('note', 'нет')} | ")
            f.write(f"Теги: {', '.join(data.get('tags', []))}\n")
        
        # Успешное сообщение
        await message.answer(
            "✅ *Запись сохранена!*\n\n"
            "Спасибо за внимание к себе!\n"
            "Это важный шаг к гармонии.",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        
        await state.clear()
        
    elif message.text == "✏️ Редактировать":
        # Начинаем заново
        await start_mood_entry(message, state)
        
    elif message.text == "🚫 Отменить":
        await cancel_mood_entry(message, state)

# Возврат в главное меню
async def return_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Возвращаемся в главное меню...",
        reply_markup=get_main_menu()
    )

# Отмена записи
async def cancel_mood_entry(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Запись настроения отменена.\n"
        "Всегда можно начать заново!",
        reply_markup=get_main_menu()
    )