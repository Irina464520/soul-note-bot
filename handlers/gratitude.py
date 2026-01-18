from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from keyboards.main_menu import get_main_menu

# Состояния для дневника благодарности
class GratitudeStates(StatesGroup):
    waiting_for_gratitude_1 = State()  # Первая благодарность
    waiting_for_gratitude_2 = State()  # Вторая благодарность  
    waiting_for_gratitude_3 = State()  # Третья благодарность
    confirmation = State()            # Подтверждение

# Начинаем запись благодарностей
async def start_gratitude_entry(message: types.Message, state: FSMContext):
    await message.answer(
        "✨ *Дневник благодарности*\n\n"
        "Каждый день находить моменты благодарности — "
        "это практика, которая меняет восприятие мира.\n\n"
        "За что ты благодарен сегодня? (Первый пункт):",
        parse_mode="Markdown",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(GratitudeStates.waiting_for_gratitude_1)

# Клавиатура для пропуска
def get_skip_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="⏭ Пропустить"))
    builder.row(
        types.KeyboardButton(text="🚫 Отмена"),
        types.KeyboardButton(text="🏠 Главное меню")
    )
    return builder.as_markup(resize_keyboard=True)

# Обработчик первой благодарности
async def process_gratitude_1(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await return_to_main_menu(message, state)
        return
        
    if message.text == "🚫 Отмена":
        await cancel_gratitude_entry(message, state)
        return
    
    if message.text == "⏭ Пропустить":
        await state.update_data(gratitude_1=None)
    else:
        await state.update_data(gratitude_1=message.text)
    
    await message.answer(
        "Отлично! А за что ещё? (Второй пункт):",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(GratitudeStates.waiting_for_gratitude_2)

# Обработчик второй благодарности
async def process_gratitude_2(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await return_to_main_menu(message, state)
        return
        
    if message.text == "🚫 Отмена":
        await cancel_gratitude_entry(message, state)
        return
    
    if message.text == "⏭ Пропустить":
        await state.update_data(gratitude_2=None)
    else:
        await state.update_data(gratitude_2=message.text)
    
    await message.answer(
        "Замечательно! И последнее на сегодня (Третий пункт):",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(GratitudeStates.waiting_for_gratitude_3)

# Обработчик третьей благодарности
async def process_gratitude_3(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await return_to_main_menu(message, state)
        return
        
    if message.text == "🚫 Отмена":
        await cancel_gratitude_entry(message, state)
        return
    
    if message.text == "⏭ Пропустить":
        await state.update_data(gratitude_3=None)
    else:
        await state.update_data(gratitude_3=message.text)
    
    # Показываем превью
    await show_gratitude_preview(message, state)

# Показываем превью перед сохранением
async def show_gratitude_preview(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    preview_text = "✨ *Твои благодарности на сегодня:*\n\n"
    
    gratitudes = []
    for i in range(1, 4):
        gratitude = data.get(f'gratitude_{i}')
        if gratitude:
            gratitudes.append(f"{i}. {gratitude}")
        else:
            gratitudes.append(f"{i}. (пропущено)")
    
    preview_text += "\n".join(gratitudes)
    preview_text += "\n\nВсё верно?"
    
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
    await state.set_state(GratitudeStates.confirmation)

# Обработчик подтверждения
async def process_gratitude_confirmation(message: types.Message, state: FSMContext):
    if message.text == "🏠 Главное меню":
        await return_to_main_menu(message, state)
        return
        
    if message.text == "✅ Да, сохранить":
        data = await state.get_data()
        
        # Сохраняем в файл
        with open("gratitude_diary.txt", "a", encoding="utf-8") as f:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_id = message.from_user.id
            
            f.write(f"{timestamp} | {user_id} | ")
            for i in range(1, 4):
                gratitude = data.get(f'gratitude_{i}', 'пропущено')
                f.write(f"Благодарность {i}: {gratitude} | ")
            f.write("\n")
        
        # Статистика
        gratitudes_count = sum(1 for i in range(1, 4) if data.get(f'gratitude_{i}'))
        
        await message.answer(
            f"✨ *Благодарности сохранены!*\n\n"
            f"Сегодня ты нашел {gratitudes_count} повода для благодарности.\n\n"
            f"_Исследования показывают, что регулярная практика благодарности:\n"
            f"• Улучшает сон на 25%\n"
            f"• Снижает уровень стресса\n"
            f"• Повышает общее чувство счастья_\n\n"
            f"Спасибо, что уделяешь время этой важной практике! 💖",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        
        await state.clear()
        
    elif message.text == "✏️ Редактировать":
        # Начинаем заново
        await start_gratitude_entry(message, state)
        
    elif message.text == "🚫 Отменить":
        await cancel_gratitude_entry(message, state)

# Возврат в главное меню
async def return_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Возвращаемся в главное меню...",
        reply_markup=get_main_menu()
    )

# Отмена записи
async def cancel_gratitude_entry(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Запись благодарностей отменена.\n"
        "Всегда можно начать заново!",
        reply_markup=get_main_menu()
    )