import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from keyboards.main_menu import get_main_menu
from handlers.diary import (
    MoodStates, start_mood_entry, process_mood, 
    process_note, process_tags, process_confirmation,
    return_to_main_menu
)
from handlers.history import (
    show_history_menu, show_recent_entries, show_statistics
)
from handlers.gratitude import (
    GratitudeStates, start_gratitude_entry, 
    process_gratitude_1, process_gratitude_2, 
    process_gratitude_3, process_gratitude_confirmation
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Глобальные переменные
user_feedback_mode = {}

# --- ВОЗВРАТ В ГЛАВНОЕ МЕНЮ (глобальная кнопка) ---
@dp.message(F.text == "🏠 Главное меню")
async def main_menu_handler(message: types.Message, state: FSMContext):
    # Если был в режиме отзыва - выходим из него
    if user_feedback_mode.get(message.from_user.id):
        user_feedback_mode[message.from_user.id] = False
    
    await return_to_main_menu(message, state)

# --- ОБРАБОТЧИКИ ДНЕВНИКА НАСТРОЕНИЯ ---

# Кнопка "📓 Дневник" или команда /diary
@dp.message(F.text == "📓 Дневник")
@dp.message(Command("diary"))
async def diary_handler(message: types.Message, state: FSMContext):
    await start_mood_entry(message, state)

# Оценка настроения
@dp.message(MoodStates.waiting_for_mood)
async def mood_handler(message: types.Message, state: FSMContext):
    await process_mood(message, state)

# Описание
@dp.message(MoodStates.waiting_for_note)
async def note_handler(message: types.Message, state: FSMContext):
    await process_note(message, state)

# Теги
@dp.message(MoodStates.waiting_for_tags)
async def tags_handler(message: types.Message, state: FSMContext):
    await process_tags(message, state)

# Подтверждение
@dp.message(MoodStates.confirmation)
async def confirmation_handler(message: types.Message, state: FSMContext):
    await process_confirmation(message, state)

# --- ОБРАБОТЧИКИ ДНЕВНИКА БЛАГОДАРНОСТИ ---

# Кнопка "✨ Благодарность"
@dp.message(F.text == "✨ Благодарность")
async def gratitude_handler(message: types.Message, state: FSMContext):
    await start_gratitude_entry(message, state)

# Первая благодарность
@dp.message(GratitudeStates.waiting_for_gratitude_1)
async def gratitude_1_handler(message: types.Message, state: FSMContext):
    await process_gratitude_1(message, state)

# Вторая благодарность
@dp.message(GratitudeStates.waiting_for_gratitude_2)
async def gratitude_2_handler(message: types.Message, state: FSMContext):
    await process_gratitude_2(message, state)

# Третья благодарность
@dp.message(GratitudeStates.waiting_for_gratitude_3)
async def gratitude_3_handler(message: types.Message, state: FSMContext):
    await process_gratitude_3(message, state)

# Подтверждение благодарностей
@dp.message(GratitudeStates.confirmation)
async def gratitude_confirmation_handler(message: types.Message, state: FSMContext):
    await process_gratitude_confirmation(message, state)

# --- ОБРАБОТЧИКИ ИСТОРИИ И АНАЛИТИКИ ---

# Кнопка "📊 Анализ"
@dp.message(F.text == "📊 Анализ")
async def analytics_handler(message: types.Message):
    await show_history_menu(message)

# Пункты меню истории
@dp.message(F.text == "📋 Последние записи")
async def recent_entries_handler(message: types.Message):
    await show_recent_entries(message)

@dp.message(F.text == "📈 Статистика")
async def statistics_handler(message: types.Message):
    await show_statistics(message)

# Заглушки для остальных кнопок
@dp.message(F.text == "📅 За неделю")
async def week_handler(message: types.Message):
    await message.answer(
        "📅 *За неделю*\n\n"
        "Этот раздел скоро появится!\n"
        "Здесь будет график настроения за 7 дней.",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📊 График")
async def chart_handler(message: types.Message):
    await message.answer(
        "📊 *График*\n\n"
        "Скоро здесь появится красивый график\n"
        "твоего настроения по дням!",
        parse_mode="Markdown"
    )

# --- ГЛАВНОЕ МЕНЮ И СТАРТ ---

@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Если был в режиме отзыва - выходим из него
    if user_feedback_mode.get(message.from_user.id):
        user_feedback_mode[message.from_user.id] = False
    
    welcome_text = (
        "╭─────────────────────────────╮\n"
        "│        🌿 SOULNOTE          │\n"
        "│    Дневник самонаблюдения   │\n"
        "╰─────────────────────────────╯\n\n"
        f"Привет, {message.from_user.first_name}!\n"
        "Твое благополучие — наш приоритет.\n\n"
        "Что исследуем сегодня?"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu()
    )

# Команда /menu
@dp.message(Command("menu"))
async def menu_command(message: types.Message, state: FSMContext):
    await return_to_main_menu(message, state)

# Остальные кнопки меню (пока заглушки)
@dp.message(F.text.in_([
    "🔄 Привычки", "🧭 GPS", "💌 Капсулы", 
    "⚙️ Настройки", "🆘 Помощь", "📤 Экспорт"
]))
async def menu_button_handler(message: types.Message):
    responses = {
        "🔄 Привычки": "🔄 Открываем трекер привычек...",
        "🧭 GPS": "🧭 Запускаем эмоциональный GPS...",
        "💌 Капсулы": "💌 Переходим к капсулам времени...",
        "⚙️ Настройки": "⚙️ Открываем настройки...",
        "🆘 Помощь": "🆘 Чем могу помочь?",
        "📤 Экспорт": "📤 Подготавливаем экспорт данных..."
    }
    
    await message.answer(responses.get(message.text, "Раздел в разработке"))

# --- ПОДДЕРЖКА ПРОЕКТА ---

@dp.message(F.text == "❤️ Поддержать проект")
async def support_handler(message: types.Message):
    support_text = (
        "❤️ *Поддержать SoulNote*\n\n"
        
        "Этот проект создается с любовью и верой, что он поможет людям "
        "обрести гармонию и лучше понимать себя.\n\n"
        
        "Ваша поддержка поможет:\n"
        "• Развивать бота и добавлять новые функции\n"
        "• Интегрировать AI для персонализированных рекомендаций\n"
        "• Создавать контент о ментальном здоровье\n"
        "• Делать бота доступным для всех\n\n"
        
        "*Способы поддержки:*\n\n"
        
        "📱 *СБП (Сбербанк онлайн):*\n"
        "• Номер телефона: `+7 (961) 286-60-11`\n"
        "• Или отсканируйте QR-код (в разработке)\n\n"
        
        "💳 *Перевод на карту:*\n"
        "• Сбербанк: `2202 2082 3823 2608`\n"
        "• Получатель: (укажи своё имя, если хочешь)\n\n"
        
        "🎁 *Бесплатные способы помочь:*\n"
        "• Расскажите о боте друзьям\n"
        "• Оставьте отзыв и предложения\n"
        "• Участвуйте в тестировании новых функций\n\n"
        
        "_Спасибо, что верите в этот проект!_\n"
        "Каждый рубль — шаг к лучшему завтра. 🌱"
    )
    
    # Клавиатура с быстрыми действиями
    from aiogram.utils.keyboard import ReplyKeyboardBuilder
    
    support_keyboard = ReplyKeyboardBuilder()
    support_keyboard.row(
        types.KeyboardButton(text="📱 Открыть СБП"),
        types.KeyboardButton(text="💳 Открыть Сбербанк")
    )
    support_keyboard.row(
        types.KeyboardButton(text="📢 Поделиться с другом"),
        types.KeyboardButton(text="📝 Оставить отзыв")
    )
    support_keyboard.row(
        types.KeyboardButton(text="🏠 Главное меню")
    )
    
    await message.answer(
        support_text,
        parse_mode="Markdown",
        reply_markup=support_keyboard.as_markup(resize_keyboard=True)
    )

# Обработчики действий поддержки
@dp.message(F.text == "📱 Открыть СБП")
async def open_sbp(message: types.Message):
    await message.answer(
        "📱 *СБП (Сбербанк онлайн)*\n\n"
        "Для перевода через СБП:\n\n"
        "1. Откройте Сбербанк онлайн\n"
        "2. Выберите 'Перевод по номеру телефона'\n"
        "3. Введите номер: `+7 (961) 286-60-11`\n"
        "4. Укажите сумму и подтвердите перевод\n\n"
        "Спасибо за поддержку! 💖\n"
        "Это реально помогает проекту развиваться."
    )

@dp.message(F.text == "💳 Открыть Сбербанк")
async def open_sberbank(message: types.Message):
    await message.answer(
        "💳 *Перевод на карту Сбербанк*\n\n"
        "Реквизиты для перевода:\n\n"
        "• Номер карты: `2202 2082 3823 2608`\n"
        "• Банк: Сбербанк\n"
        "• Система: МИР\n\n"
        "Можно перевести:\n"
        "• Через Сбербанк онлайн\n"
        "• Через мобильное приложение\n"
        "• В отделении банка\n\n"
        "Благодарю за доверие и поддержку! 🙏\n"
        "Ваш вклад делает проект лучше."
    )

@dp.message(F.text == "📢 Поделиться с другом")
async def share_with_friend(message: types.Message):
    share_text = (
        "Привет! Хочу поделиться крутым ботом для отслеживания настроения и ментального здоровья:\n\n"
        "🌿 *SoulNote* — твой персональный дневник гармонии\n\n"
        "Что можно делать:\n"
        "• Вести дневник настроения с аналитикой\n"
        "• Отслеживать эмоции и триггеры\n"
        "• Практиковать благодарность каждый день\n"
        "• Получать инсайты о своих паттернах\n\n"
        "Бот бесплатный и очень удобный!\n"
        "Попробуй: @SoulNoteMy_bot\n\n"
        "#ментальноездоровье #саморазвитие #дневник"
    )
    
    await message.answer(
        "📢 *Поделиться с другом*\n\n"
        "Вот текст для отправки:\n\n"
        "---\n"
        f"{share_text}\n"
        "---\n\n"
        "Просто скопируй и отправь другу! 📲\n"
        "Спасибо за распространение добра! 🌸"
    )

# --- ОБРАБОТКА ОТЗЫВОВ ---

# Кнопка "Оставить отзыв"
@dp.message(F.text == "📝 Оставить отзыв")
async def leave_feedback_handler(message: types.Message):
    # Включаем режим отзыва для этого пользователя
    user_feedback_mode[message.from_user.id] = True
    
    await message.answer(
        "📝 *Оставить отзыв*\n\n"
        "Мне очень важно твое мнение!\n\n"
        "Напиши, что тебе нравится в боте, "
        "что можно улучшить, или какие функции хочешь видеть.\n\n"
        "Просто отправь сообщение с отзывом — я обязательно его прочту! ✨\n\n"
        "_(Чтобы отменить, отправь /start или нажми 🏠 Главное меню)_",
        parse_mode="Markdown"
    )

# Обработчик сообщений в режиме отзыва
@dp.message(lambda message: user_feedback_mode.get(message.from_user.id, False))
async def process_feedback_handler(message: types.Message):
    # Если пользователь отправил команду выхода - выходим из режима отзыва
    if message.text in ["/start", "/menu", "🏠 Главное меню"]:
        user_feedback_mode[message.from_user.id] = False
        await start_command(message)
        return
    
    # Сохраняем отзыв в файл
    user_info = f"{message.from_user.id} ({message.from_user.username or 'нет username'})"
    
    try:
        with open("feedback.txt", "a", encoding="utf-8") as f:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} | {user_info} | {message.text}\n")
        
        # Выключаем режим отзыва
        user_feedback_mode[message.from_user.id] = False
        
        # Отправляем подтверждение
        await message.answer(
            "💌 *Отзыв успешно сохранён!*\n\n"
            "Большое спасибо за твоё мнение! 🙏\n"
            "Я обязательно учту его при развитии бота.\n\n"
            "Твои слова помогают делать SoulNote лучше каждый день. 🌱",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        logger.error(f"Ошибка сохранения отзыва: {e}")
        await message.answer(
            "😔 Произошла ошибка при сохранении отзыва.\n"
            "Попробуй ещё раз или напиши позже.",
            reply_markup=get_main_menu()
        )

# --- ОБЩИЙ ОБРАБОТЧИК (в самом конце!) ---
@dp.message()
async def unknown_message_handler(message: types.Message):
    """
    Обрабатывает все сообщения, которые не были обработаны другими обработчиками.
    Должен быть ПОСЛЕДНИМ в цепочке обработчиков.
    """
    # Игнорируем команду /start (уже обработана выше)
    if message.text == "/start":
        return
    
    # Игнорируем команду /menu (уже обработана выше)
    if message.text == "/menu":
        return
    
    # Игнорируем все известные команды (уже обработаны выше)
    known_commands = [
        "📓 Дневник", "📊 Анализ", "✨ Благодарность",
        "🔄 Привычки", "🧭 GPS", "💌 Капсулы",
        "⚙️ Настройки", "🆘 Помощь", "📤 Экспорт",
        "❤️ Поддержать проект", "🏠 Главное меню",
        "📱 Открыть СБП", "💳 Открыть Сбербанк",
        "📢 Поделиться с другом", "📝 Оставить отзыв",
        "📋 Последние записи", "📈 Статистика",
        "📅 За неделю", "📊 График"
    ]
    
    if message.text in known_commands:
        return
    
    # Игнорируем если в режиме отзыва (уже обрабатывается другим хендлером)
    if user_feedback_mode.get(message.from_user.id, False):
        return
    
    # Если это неизвестное сообщение - показываем подсказку
    await message.answer(
        "🤔 Я не совсем понял это сообщение.\n\n"
        "Пожалуйста, используй кнопки меню внизу экрана,\n"
        "или отправь команду /start чтобы открыть главное меню.",
        reply_markup=get_main_menu()
    )

# Запуск бота
async def main():
    logger.info("Бот запускается...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())