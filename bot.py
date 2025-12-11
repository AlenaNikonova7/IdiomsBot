import json
import os
import random
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Конфигурация
TOKEN = os.getenv("BOT_TOKEN")
DATA_FOLDER = "data"

# Категории идиом с эмодзи
CATEGORIES = {
    "business": "🏢 Business - деловые идиомы",
    "everyday": "🏠 Everyday - повседневные выражения", 
    "emotions": "😊 Emotions - эмоции и характер",
    "quick": "⚡ Quick & Easy - простые и частые",
    "communication": "💬 Communication - общение и разговор",
    "all": "🌈 All - все категории"
}

# Структура для хранения статистики пользователей
user_stats = defaultdict(lambda: {
    'studied': set(),  # изученные идиомы (по названию)
    'correct': 0,
    'total': 0,
    'mistakes': set(),  # идиомы, где были ошибки
    'by_category': defaultdict(lambda: {'studied': 0, 'total': 0})
})

# Загрузка всех идиом из JSON файлов
def load_all_idioms() -> Dict[str, List[Dict]]:
    all_idioms = {}
    
    # Загружаем каждую категорию
    for category_key in CATEGORIES:
        if category_key == "all":
            continue
            
        filename = f"{category_key}_idioms.json"
        filepath = os.path.join(DATA_FOLDER, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    all_idioms[category_key] = json.load(f)
                    print(f"✅ Загружено {len(all_idioms[category_key])} идиом из {filename}")
            except Exception as e:
                print(f"❌ Ошибка загрузки {filename}: {e}")
                all_idioms[category_key] = []
        else:
            print(f"⚠️ Файл {filename} не найден!")
            all_idioms[category_key] = []
    
    # Создаем категорию "all" со всеми идиомами
    all_idioms_list = []
    for category, idioms in all_idioms.items():
        for idiom in idioms:
            idiom['category'] = category
        all_idioms_list.extend(idioms)
    
    all_idioms["all"] = all_idioms_list
    
    return all_idioms

# Глобальная переменная со всеми идиомами
ALL_IDIOMS = load_all_idioms()

# Получение списка идиом для пользователя
def get_idioms_for_user(user_id: int, category: str, mode: str = "study") -> List[Dict]:
    if category not in ALL_IDIOMS:
        return []
    
    idioms = ALL_IDIOMS[category]
    
    if mode == "study":
        # Для изучения: еще не изученные + те, где были ошибки
        studied = user_stats[user_id]['studied']
        mistakes = user_stats[user_id]['mistakes']
        
        filtered_idioms = []
        for idiom in idioms:
            idiom_name = idiom['idiom']
            if idiom_name not in studied or idiom_name in mistakes:
                filtered_idioms.append(idiom)
        
        return filtered_idioms
    else:  # review
        # Для повторения: только изученные
        studied = user_stats[user_id]['studied']
        return [idiom for idiom in idioms if idiom['idiom'] in studied]

# Создание вопроса
def create_question(user_id: int, category: str, mode: str = "study", 
                   direction: str = "en_to_ru") -> Tuple[Optional[str], Optional[List[str]], Optional[str], Optional[str]]:
    idioms = get_idioms_for_user(user_id, category, mode)
    
    if not idioms:
        return None, None, None, None
    
    # Выбираем случайную идиому
    correct_idiom = random.choice(idioms)
    
    # Получаем все идиомы для выбора неправильных вариантов
    all_category_idioms = ALL_IDIOMS[category] if category != "all" else ALL_IDIOMS["all"]
    
    # Выбираем 3 случайные неправильные идиомы
    other_idioms = [idiom for idiom in all_category_idioms 
                   if idiom['idiom'] != correct_idiom['idiom']]
    
    if len(other_idioms) < 3:
        wrong_choices = other_idioms
    else:
        wrong_choices = random.sample(other_idioms, 3)
    
    if direction == "en_to_ru":
        # Английская идиома -> выбор русского перевода
        question = f"*{correct_idiom['idiom']}*\n\nЧто означает?"
        
        choices = [correct_idiom['meaning']]
        choices.extend([idiom['meaning'] for idiom in wrong_choices])
        
        correct_answer = correct_idiom['meaning']
        example = correct_idiom.get('example', '')
        explanation = f"💡 *Пример:* {example}" if example else ""
    else:  # ru_to_en
        # Русский перевод -> выбор английской идиомы
        question = f"*{correct_idiom['meaning']}*\n\nКак сказать по-английски?"
        
        choices = [correct_idiom['idiom']]
        choices.extend([idiom['idiom'] for idiom in wrong_choices])
        
        correct_answer = correct_idiom['idiom']
        example = correct_idiom.get('example', '')
        explanation = f"💡 *Пример:* {example}" if example else ""
    
    # Перемешиваем варианты ответов
    random.shuffle(choices)
    
    # Добавляем категорию в вопрос
    category_name = CATEGORIES.get(category, 'Все категории')
    question = f"{category_name}\n\n{question}"
    
    return question, choices, correct_answer, explanation

# Создание клавиатуры с вариантами ответов
def create_keyboard(choices: List[str]) -> InlineKeyboardMarkup:
    keyboard = []
    for i, choice in enumerate(choices):  # ТОЛЬКО ЭТО
        display_text = choice[:35] + "..." if len(choice) > 35 else choice
        keyboard.append([InlineKeyboardButton(display_text, callback_data=str(i))])
    return InlineKeyboardMarkup(keyboard)

# Клавиатура выбора категории
def create_category_keyboard(mode: str = "study") -> InlineKeyboardMarkup:
    keyboard = []
    
    # Текст для заголовка
    mode_text = "изучения" if mode == "study" else "повторения"
    
    # Создаем кнопки для всех категорий
    for category_key, category_name in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(
            category_name, 
            callback_data=f"{mode}_{category_key}"
        )])
    
    return InlineKeyboardMarkup(keyboard)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    welcome_text = f"""
🎓 *Добро пожаловать, {user.first_name}!*

🇬🇧 *Изучайте английские идиомы легко и эффективно!*

📚 *Доступные категории:*
{CATEGORIES['business']}
{CATEGORIES['everyday']}
{CATEGORIES['emotions']}  
{CATEGORIES['quick']}
{CATEGORIES['communication']}
{CATEGORIES['all']}

🎯 *Основные команды:*
/study - Начать изучение 📖
/review - Повторить изученное 🔄
/stats - Посмотреть статистику 📊
/help - Помощь и инструкции ❓

💡 *Совет:* Начните с конкретной категории или выберите "Все категории" для разнообразия!
"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Команда /study
async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
📖 *Режим изучения*

Выберите категорию для изучения новых идиом:

• 🆕 Будут показаны *новые идиомы*
• 🔄 Будут повторяться *идиомы с ошибками*
• 🎯 Можно выбрать *конкретную категорию* или *все сразу*

👇 Выберите категорию:
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=create_category_keyboard("study")
    )

# Команда /review
async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем, есть ли изученные идиомы
    studied_count = len(user_stats[user_id]['studied'])
    
    if studied_count == 0:
        await update.message.reply_text(
            "📝 *У вас пока нет изученных идиом!*\n\n"
            "Начните с команды /study чтобы изучить первые идиомы.",
            parse_mode='Markdown'
        )
        return
    
    welcome_text = """
🔄 *Режим повторения*

Выберите категорию для повторения изученных идиом:

• ✅ Будут показаны *только изученные* идиомы
• 📈 Помогает *закрепить знания*
• 🎯 Можно выбрать *конкретную категорию* или *все сразу*

👇 Выберите категорию:
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=create_category_keyboard("review")
    )

# Обработка выбора категории
async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    mode, category = data.split("_", 1)
    category_name = CATEGORIES.get(category, "Все категории")
    
    # Сохраняем выбранную категорию и режим
    context.user_data['current_category'] = category
    context.user_data['current_mode'] = mode
    context.user_data['current_category_name'] = category_name
    
    # Случайно выбираем направление перевода
    direction = random.choice(['en_to_ru', 'ru_to_en'])
    
    # Создаем вопрос
    question, choices, correct_answer, explanation = create_question(
        user_id, category, mode, direction
    )
    
    if not question:
        if mode == "study":
            message = f"""
🎉 *Поздравляем!*

Вы успешно изучили *все идиомы* в категории:
{category_name}

Выберите другую категорию или перейдите в режим /review для повторения!
"""
        else:
            message = f"""
📝 *Пока нет изученных идиом*

В категории {category_name} пока нет изученных идиом.

Начните изучение с команды /study!
"""
        
        keyboard = [[InlineKeyboardButton("📁 Выбрать категорию", callback_data=f"{mode}_menu")]]
        await query.edit_message_text(message, parse_mode='Markdown', 
                                     reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Сохраняем данные в контексте
    context.user_data['correct_answer'] = correct_answer
    context.user_data['current_direction'] = direction
    context.user_data['current_explanation'] = explanation
    context.user_data['current_choices'] = choices
    context.user_data['current_category'] = category
    
    # Показываем иконку направления
    direction_icon = "🇬🇧 → 🇷🇺" if direction == "en_to_ru" else "🇷🇺 → 🇬🇧"
    
    # Добавляем счетчик вопросов
    question_number = context.user_data.get('question_count', 1)
    context.user_data['question_count'] = question_number + 1
    
    await query.edit_message_text(
        f"{question}\n\n{direction_icon}",
        parse_mode='Markdown',
        reply_markup=create_keyboard(choices)
    )

# Обработка ответов
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    choice_index = int(query.data)
    
    # Получаем данные из контекста
    correct_answer = context.user_data.get('correct_answer')
    choices = context.user_data.get('current_choices', [])
    explanation = context.user_data.get('current_explanation', '')
    category = context.user_data.get('current_category', 'all')
    mode = context.user_data.get('current_mode', 'study')
    direction = context.user_data.get('current_direction', 'en_to_ru')
    category_name = context.user_data.get('current_category_name', 'Все категории')
    
    if not correct_answer or not choices:
        await query.edit_message_text("❌ Ошибка. Попробуйте начать заново.")
        return
    
    # Определяем, правильный ли ответ
    user_answer = choices[choice_index]
    is_correct = user_answer == correct_answer
    
    # Обновляем статистику
    user_stats[user_id]['total'] += 1
    
    # Находим идиому по правильному ответу
    correct_idiom = None
    idioms_list = ALL_IDIOMS[category]
    
    for idiom in idioms_list:
        if direction == "en_to_ru" and idiom['meaning'] == correct_answer:
            correct_idiom = idiom
            break
        elif direction == "ru_to_en" and idiom['idiom'] == correct_answer:
            correct_idiom = idiom
            break
    
    if is_correct:
        user_stats[user_id]['correct'] += 1
        
        # Если это изучение и ответ правильный, добавляем в изученные
        if mode == "study" and correct_idiom:
            user_stats[user_id]['studied'].add(correct_idiom['idiom'])
            user_stats[user_id]['mistakes'].discard(correct_idiom['idiom'])
            
            # Обновляем статистику по категориям
            idiom_category = correct_idiom.get('category', category)
            user_stats[user_id]['by_category'][idiom_category]['studied'] += 1
        
        result_icon = "✅"
        result_text = "*Отлично! Правильный ответ!*"
        result_color = "🟢"
    else:
        # Если ошибка, добавляем в список ошибок
        if correct_idiom:
            user_stats[user_id]['mistakes'].add(correct_idiom['idiom'])
        
        result_icon = "❌"
        result_text = "*Не совсем верно*"
        result_color = "🔴"
    
    # Показываем результат
    result_message = f"""
{result_color} **Результат:**
{result_icon} {result_text}

📖 **Правильный ответ:**
*{correct_answer}*

{explanation}

{category_name}
"""
    
    # Добавляем кнопки для продолжения
    keyboard = [
        [InlineKeyboardButton("➡️ Следующий вопрос", callback_data=f"continue_{category}")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="show_stats")],
        [InlineKeyboardButton("📁 Сменить категорию", callback_data="change_category")]
    ]
    
    await query.edit_message_text(
        result_message,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработка кнопок продолжения
async def handle_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "show_stats":
        await show_stats_inline(query, user_id)
        return
    elif data == "change_category":
        # Возвращаем к выбору категории
        current_mode = context.user_data.get('current_mode', 'study')
        mode_text = "изучения" if current_mode == "study" else "повторения"
        
        await query.edit_message_text(
            f"📁 *Выберите категорию для {mode_text}:*",
            parse_mode='Markdown',
            reply_markup=create_category_keyboard(current_mode)
        )
        return
    elif data.endswith("_menu"):
        # Возврат в меню выбора категории
        mode = data.split("_")[0]
        await query.edit_message_text(
            "📁 Выберите категорию:",
            parse_mode='Markdown',
            reply_markup=create_category_keyboard(mode)
        )
        return
    
    # Продолжаем в той же категории
    _, category = data.split("_", 1)
    
    mode = context.user_data.get('current_mode', 'study')
    direction = random.choice(['en_to_ru', 'ru_to_en'])
    
    question, choices, correct_answer, explanation = create_question(
        user_id, category, mode, direction
    )
    
    if not question:
        category_name = CATEGORIES.get(category, 'Все категории')
        
        if mode == "study":
            message = f"""
🎉 *Поздравляем!*

Вы успешно изучили *все идиомы* в категории:
{category_name}

Выберите другую категорию или перейдите в режим /review для повторения!
"""
        else:
            message = f"""
📝 *Пока нет изученных идиом*

В категории {category_name} пока нет изученных идиом.

Начните изучение с команды /study!
"""
        
        keyboard = [[InlineKeyboardButton("📁 Выбрать категорию", callback_data="change_category")]]
        await query.edit_message_text(message, parse_mode='Markdown', 
                                     reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Сохраняем данные
    context.user_data['correct_answer'] = correct_answer
    context.user_data['current_direction'] = direction
    context.user_data['current_explanation'] = explanation
    context.user_data['current_choices'] = choices
    context.user_data['current_category'] = category
    context.user_data['current_category_name'] = CATEGORIES.get(category, 'Все категории')
    
    # Показываем иконку направления
    direction_icon = "🇬🇧 → 🇷🇺" if direction == "en_to_ru" else "🇷🇺 → 🇬🇧"
    
    await query.edit_message_text(
        f"{question}\n\n{direction_icon}",
        parse_mode='Markdown',
        reply_markup=create_keyboard(choices)
    )

# Показать статистику (inline)
async def show_stats_inline(query, user_id: int):
    stats = user_stats[user_id]
    total_idioms = len(ALL_IDIOMS["all"])
    studied_count = len(stats['studied'])
    
    if stats['total'] > 0:
        accuracy = (stats['correct'] / stats['total']) * 100
        if accuracy >= 80:
            accuracy_emoji = "🔥"
        elif accuracy >= 60:
            accuracy_emoji = "⭐"
        else:
            accuracy_emoji = "📈"
    else:
        accuracy = 0
        accuracy_emoji = "📊"
    
    # Прогресс-бар
    progress_percent = (studied_count / total_idioms * 100) if total_idioms > 0 else 0
    filled = int(progress_percent / 10)
    progress_bar = "▓" * filled + "░" * (10 - filled)
    
    # Статистика по категориям
    category_stats = []
    for cat_key, cat_name in CATEGORIES.items():
        if cat_key == "all":
            continue
        
        total_in_cat = len(ALL_IDIOMS.get(cat_key, []))
        studied_in_cat = stats['by_category'][cat_key]['studied']
        
        if total_in_cat > 0:
            percentage = (studied_in_cat / total_in_cat) * 100
            if percentage == 100:
                emoji = "🎯"
            elif percentage >= 50:
                emoji = "✅"
            else:
                emoji = "📚"
            
            category_stats.append(f"{emoji} {cat_name}: {studied_in_cat}/{total_in_cat}")
    
    message = f"""
📊 *Ваша статистика*

🎯 *Общий прогресс:*
{progress_bar} {progress_percent:.0f}%
{studied_count} из {total_idioms} идиом изучено

{accuracy_emoji} *Точность ответов:*
{stats['correct']} из {stats['total']} правильных
({accuracy:.1f}%)

📁 *Прогресс по категориям:*
{chr(10).join(category_stats)}

💡 *Совет:* Продолжайте в том же духе!
"""
    
    keyboard = [
        [InlineKeyboardButton("🎯 Продолжить изучение", callback_data="change_category")],
        [InlineKeyboardButton("🔄 Повторить изученное", callback_data="review_menu")]
    ]
    
    await query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Команда /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_stats_inline(update.message, update.effective_user.id)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
❓ *Помощь и инструкции*

🎯 *Как работает бот:*
1. Выберите команду /study для изучения новых идиом
2. Выберите команду /review для повторения изученных
3. Отвечайте на вопросы, выбирая правильный вариант
4. Следите за своим прогрессом с помощью /stats

📚 *Типы вопросов:*
• 🇬🇧 → 🇷🇺 *Английская идиома* → *русский перевод*
• 🇷🇺 → 🇬🇧 *Русский перевод* → *английская идиома*

📁 *Категории идиом:*
🏢 Business - деловые идиомы
🏠 Everyday - повседневные выражения  
😊 Emotions - эмоции и характер
⚡ Quick & Easy - простые и частые
💬 Communication - общение и разговор
🌈 All - все категории смешанно

💡 *Советы для эффективного обучения:*
• Начинайте с конкретных категорий
• Регулярно повторяйте изученное
• Не бойтесь ошибаться - ошибки помогают учиться!
• Используйте примеры для лучшего запоминания

📊 *Статистика показывает:*
• Общий прогресс изучения
• Точность ваших ответов
• Прогресс по каждой категории

Удачи в изучении английских идиом! 🎓
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Основная функция
def main():
    print("=" * 60)
    print("🎓 Бот для изучения английских идиом")
    print("=" * 60)
    
    # Выводим информацию о загруженных данных
    total_all = 0
    for category, idioms in ALL_IDIOMS.items():
        if category != "all":
            count = len(idioms)
            total_all += count
            category_name = CATEGORIES.get(category, category)
            print(f"{category_name}: {count} идиом")
    
    print(f"\n📊 Всего идиом: {total_all}")
    print("=" * 60)
    print("🤖 Бот запущен и готов к работе!")
    print("=" * 60)
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("study", study))
    application.add_handler(CommandHandler("review", review))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("help", help_command))
    
    # Добавляем обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(handle_category_selection, pattern="^(study|review)_"))
    application.add_handler(CallbackQueryHandler(handle_continue, pattern="^(continue_|change_category|show_stats|review_menu|study_menu)"))
    application.add_handler(CallbackQueryHandler(handle_answer))
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()