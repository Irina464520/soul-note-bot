from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Создает главное меню как Reply-клавиатуру внизу экрана
    """
    builder = ReplyKeyboardBuilder()
    
    # Первая строка
    builder.row(
        KeyboardButton(text="📓 Дневник"),
        KeyboardButton(text="📊 Анализ"),
        KeyboardButton(text="✨ Благодарность")
    )
    
    # Вторая строка
    builder.row(
        KeyboardButton(text="🔄 Привычки"),
        KeyboardButton(text="🧭 GPS"),
        KeyboardButton(text="💌 Капсулы")
    )
    
    # Третья строка
    builder.row(
        KeyboardButton(text="⚙️ Настройки"),
        KeyboardButton(text="🆘 Помощь"),
        KeyboardButton(text="📤 Экспорт")
    )
    
    # Четвертая строка - только поддержка проекта
    builder.row(KeyboardButton(text="❤️ Поддержать проект"))
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )