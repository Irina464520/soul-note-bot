from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from keyboards.main_menu import get_main_menu
import os
from datetime import datetime

# Проверяем, есть ли записи
def has_mood_entries(user_id=None):
    if not os.path.exists("mood_diary.txt"):
        return False
    
    with open("mood_diary.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    if not lines:
        return False
    
    if user_id:
        # Проверяем записи конкретного пользователя
        user_str = str(user_id)
        for line in lines:
            if f"| {user_str} |" in line:
                return True
        return False
    
    return len(lines) > 0

# Получаем записи пользователя
def get_user_mood_entries(user_id, limit=10):
    entries = []
    
    if not os.path.exists("mood_diary.txt"):
        return entries
    
    with open("mood_diary.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    user_str = str(user_id)
    
    for line in reversed(lines):  # Сначала новые записи
        if f"| {user_str} |" in line:
            # Парсим строку
            parts = line.strip().split(" | ")
            if len(parts) >= 5:
                entry = {
                    'date': parts[0],
                    'mood': parts[2].replace("Настроение: ", "").replace("/10", ""),
                    'note': parts[3].replace("Описание: ", ""),
                    'tags': parts[4].replace("Теги: ", "").split(", ") if parts[4] != "Теги: нет" else []
                }
                entries.append(entry)
                
                if len(entries) >= limit:
                    break
    
    return entries

# Клавиатура для истории
def get_history_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="📅 За неделю"),
        types.KeyboardButton(text="📊 График")
    )
    builder.row(
        types.KeyboardButton(text="📋 Последние записи"),
        types.KeyboardButton(text="📈 Статистика")
    )
    builder.row(
        types.KeyboardButton(text="🏠 Главное меню")
    )
    return builder.as_markup(resize_keyboard=True)

# Показываем историю
async def show_history_menu(message: types.Message):
    user_id = message.from_user.id
    
    if not has_mood_entries(user_id):
        await message.answer(
            "📭 У тебя пока нет записей в дневнике.\n\n"
            "Начни с кнопки *📓 Дневник* — сделай первую запись!",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        return
    
    # Получаем последние записи
    entries = get_user_mood_entries(user_id, 3)
    
    if not entries:
        await message.answer(
            "Что-то пошло не так. Записей не найдено.",
            reply_markup=get_main_menu()
        )
        return
    
    # Показываем краткую статистику
    mood_scores = [int(entry['mood']) for entry in entries if entry['mood'].isdigit()]
    avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0
    
    # Эмодзи для средней оценки
    mood_emoji = {
        1: "😔", 2: "🙁", 3: "😐", 4: "🙂",
        5: "😊", 6: "🤩", 7: "🌈", 8: "✨",
        9: "🌟", 10: "💫"
    }
    
    emoji = mood_emoji.get(round(avg_mood), "😐")
    
    welcome_text = (
        f"📖 *Твой дневник*\n\n"
        f"Всего записей: *{len(entries)}*\n"
        f"Среднее настроение: *{avg_mood:.1f}/10* {emoji}\n\n"
        f"Что хочешь посмотреть?"
    )
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_history_keyboard()
    )

# Показываем последние записи
async def show_recent_entries(message: types.Message):
    user_id = message.from_user.id
    entries = get_user_mood_entries(user_id, 5)
    
    if not entries:
        await message.answer("Записей не найдено.")
        return
    
    response = "📝 *Последние записи:*\n\n"
    
    for i, entry in enumerate(entries, 1):
        # Форматируем дату
        try:
            dt = datetime.strptime(entry['date'], "%Y-%m-%d %H:%M:%S")
            date_str = dt.strftime("%d.%m %H:%M")
        except:
            date_str = entry['date']
        
        # Эмодзи для настроения
        mood_emoji_map = {
            "1": "😔", "2": "🙁", "3": "😐", "4": "🙂",
            "5": "😊", "6": "🤩", "7": "🌈", "8": "✨",
            "9": "🌟", "10": "💫"
        }
        
        mood_score = entry['mood']
        emoji = mood_emoji_map.get(mood_score, "😐")
        
        # Обрезаем длинное описание
        note = entry['note']
        if len(note) > 50:
            note = note[:47] + "..."
        
        # Формируем запись
        response += f"*{i}. {date_str}*\n"
        response += f"{emoji} Настроение: *{mood_score}/10*\n"
        
        if note and note != "нет":
            response += f"📝 {note}\n"
        
        if entry['tags']:
            response += f"🏷️ {', '.join(entry['tags'])}\n"
        
        response += "\n"
    
    await message.answer(
        response,
        parse_mode="Markdown",
        reply_markup=get_history_keyboard()
    )

# Простая статистика
async def show_statistics(message: types.Message):
    user_id = message.from_user.id
    entries = get_user_mood_entries(user_id, 100)  # Все записи
    
    if not entries:
        await message.answer("Недостаточно данных для статистики.")
        return
    
    # Анализируем
    mood_scores = [int(entry['mood']) for entry in entries if entry['mood'].isdigit()]
    total_entries = len(mood_scores)
    
    if total_entries == 0:
        await message.answer("Недостаточно данных для статистики.")
        return
    
    avg_mood = sum(mood_scores) / total_entries
    
    # Считаем распределение
    mood_dist = {i: 0 for i in range(1, 11)}
    for score in mood_scores:
        if 1 <= score <= 10:
            mood_dist[score] += 1
    
    # Находим самое частое настроение
    most_common = max(mood_dist.items(), key=lambda x: x[1])
    
    # Формируем ответ
    mood_emoji = {
        1: "😔", 2: "🙁", 3: "😐", 4: "🙂",
        5: "😊", 6: "🤩", 7: "🌈", 8: "✨",
        9: "🌟", 10: "💫"
    }
    
    emoji = mood_emoji.get(round(avg_mood), "😐")
    
    response = (
        f"📊 *Твоя статистика*\n\n"
        f"Всего записей: *{total_entries}*\n"
        f"Среднее настроение: *{avg_mood:.1f}/10* {emoji}\n"
        f"Чаще всего: *{most_common[0]}/10* ({most_common[1]} раз)\n\n"
        f"*Распределение:*\n"
    )
    
    # Добавляем график ASCII
    for score in range(10, 0, -1):
        count = mood_dist[score]
        percentage = (count / total_entries) * 100 if total_entries > 0 else 0
        bar = "█" * int(percentage / 10)
        response += f"{score:2}/10: {bar} {count} зап.\n"
    
    await message.answer(
        response,
        parse_mode="Markdown",
        reply_markup=get_history_keyboard()
    )