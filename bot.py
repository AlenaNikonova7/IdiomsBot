import os
import random
import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация (используем переменные окружения)
TOKEN = os.getenv("BOT_TOKEN")

# Если токен не найден в переменных окружения, попробуем прочитать из .env файла
if not TOKEN:
    try:
        # Попытка загрузить из .env файла напрямую
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if key == 'BOT_TOKEN':
                        TOKEN = value
                        break
    except FileNotFoundError:
        pass

if not TOKEN:
    logger.error("❌ BOT_TOKEN not found!")
    # Не падаем сразу, возможно, токен будет задан позже
    TOKEN = ""

# Категории идиом с эмодзи
CATEGORIES = {
    "business": "🏢 Business - деловые идиомы",
    "everyday": "🏠 Everyday - повседневные выражения", 
    "emotions": "😊 Emotions - эмоции и характер",
    "quick": "⚡ Quick & Easy - простые и частые",
    "communication": "💬 Communication - общение и разговор",
    "all": "🌈 All - все категории"
}

# ============ ВСТРОЕННЫЕ ДАННЫЕ ИДИОМ ============
# ВСТАВЬТЕ СЮДА ВЕСЬ ВАШ КОД С ИДИОМАМИ БЕЗ ИЗМЕНЕНИЙ
# ALL_IDIOMS_DATA = { ... }
ALL_IDIOMS_DATA = {
    "business": [
        {
            "idiom": "Think outside the box",
            "meaning": "Мыслить нестандартно",
            "example": "We need to think outside the box to solve this marketing problem."
        },
        {
            "idiom": "Get the ball rolling",
            "meaning": "Начать процесс",
            "example": "Let's get the ball rolling on the new project tomorrow."
        },
        {
            "idiom": "Low-hanging fruit",
            "meaning": "Легкая цель/задача",
            "example": "Let's start with the low-hanging fruit to show quick results."
        },
        {
            "idiom": "Move the needle",
            "meaning": "Оказать значительное влияние",
            "example": "This campaign needs to move the needle on our sales figures."
        },
        {
            "idiom": "Boil the ocean",
            "meaning": "Пытаться сделать невозможное",
            "example": "Trying to please everyone is like trying to boil the ocean."
        },
        {
            "idiom": "Circle back",
            "meaning": "Вернуться к вопросу позже",
            "example": "Let's circle back to this discussion next week."
        },
        {
            "idiom": "Touch base",
            "meaning": "Связаться, обсудить кратко",
            "example": "I'll touch base with you after the meeting."
        },
        {
            "idiom": "On the same page",
            "meaning": "Быть в согласии",
            "example": "We need to make sure everyone is on the same page about the deadline."
        },
        {
            "idiom": "Bandwidth",
            "meaning": "Время, возможности, ресурсы",
            "example": "I don't have the bandwidth to take on another project right now."
        },
        {
            "idiom": "Deep dive",
            "meaning": "Детальное изучение",
            "example": "We need to do a deep dive into the customer feedback data."
        },
        {
            "idiom": "Drill down",
            "meaning": "Углубиться в детали",
            "example": "Let's drill down into the specific cost breakdown."
        },
        {
            "idiom": "Elephant in the room",
            "meaning": "Очевидная проблема, которую все игнорируют",
            "example": "The budget deficit is the elephant in the room that nobody wants to discuss."
        },
        {
            "idiom": "Get your ducks in a row",
            "meaning": "Подготовиться, организовать все должным образом",
            "example": "We need to get our ducks in a row before the investor meeting."
        },
        {
            "idiom": "Hit the ground running",
            "meaning": "Начать работать эффективно с самого начала",
            "example": "The new manager hit the ground running from her first day."
        },
        {
            "idiom": "In the pipeline",
            "meaning": "В процессе разработки/планирования",
            "example": "We have several new products in the pipeline for next year."
        },
        {
            "idiom": "Learning curve",
            "meaning": "Сложность освоения нового",
            "example": "The software has a steep learning curve but it's very powerful."
        },
        {
            "idiom": "Move the goalposts",
            "meaning": "Менять условия/требования",
            "example": "Every time we meet the target, they move the goalposts."
        },
        {
            "idiom": "Par for the course",
            "meaning": "Обычное, ожидаемое дело",
            "example": "Delays are par for the course in this industry."
        },
        {
            "idiom": "Put all your eggs in one basket",
            "meaning": "Рисковать всем в одном деле",
            "example": "Investing all our money in one stock is putting all eggs in one basket."
        },
        {
            "idiom": "Raise the bar",
            "meaning": "Устанавливать более высокие стандарты",
            "example": "Our competitors have really raised the bar with their new product."
        },
        {
            "idiom": "Read between the lines",
            "meaning": "Понимать скрытый смысл",
            "example": "You need to read between the lines in his email to understand what he really wants."
        },
        {
            "idiom": "Reinvent the wheel",
            "meaning": "Тратить время на изобретение уже существующего",
            "example": "Let's not reinvent the wheel; we can use the existing template."
        },
        {
            "idiom": "Silver bullet",
            "meaning": "Простое решение сложной проблемы",
            "example": "There's no silver bullet for increasing productivity overnight."
        },
        {
            "idiom": "Step up to the plate",
            "meaning": "Взять на себя ответственность",
            "example": "Someone needs to step up to the plate and lead this project."
        },
        {
            "idiom": "Think on your feet",
            "meaning": "Быстро принимать решения в непредвиденных ситуациях",
            "example": "Good salespeople need to think on their feet during client meetings."
        },
        {
            "idiom": "Throw under the bus",
            "meaning": "Предать, подставить кого-то",
            "example": "He threw his colleague under the bus to save his own job."
        },
        {
            "idiom": "Trial balloon",
            "meaning": "Пробный шар, тестирование реакции",
            "example": "The CEO floated a trial balloon about potential layoffs."
        },
        {
            "idiom": "Win-win situation",
            "meaning": "Ситуация, выгодная всем",
            "example": "The partnership created a win-win situation for both companies."
        },
        {
            "idiom": "At the end of the day",
            "meaning": "В конечном счете",
            "example": "At the end of the day, customer satisfaction is what matters most."
        },
        {
            "idiom": "Ballpark figure",
            "meaning": "Приблизительная оценка, примерная цифра",
            "example": "Can you give me a ballpark figure for the project cost?"
        },
        {
            "idiom": "Cut corners",
            "meaning": "Делать что-то некачественно, чтобы сэкономить",
            "example": "If we cut corners on materials, the product won't last long."
        },
        {
            "idiom": "Get down to business",
            "meaning": "Приступить к делу",
            "example": "Let's skip the small talk and get down to business."
        },
        {
            "idiom": "Go the extra mile",
            "meaning": "Делать больше, чем требуется",
            "example": "She always goes the extra mile to help her clients."
        },
        {
            "idiom": "In the loop",
            "meaning": "В курсе дел",
            "example": "Please keep me in the loop about any changes to the schedule."
        },
        {
            "idiom": "Learning the ropes",
            "meaning": "Осваивать основы работы",
            "example": "The new intern is still learning the ropes."
        },
        {
            "idiom": "On the back burner",
            "meaning": "Временно отложенный",
            "example": "We've put the expansion plans on the back burner for now."
        },
        {
            "idiom": "Pick up the slack",
            "meaning": "Делать работу за других",
            "example": "When John was sick, everyone had to pick up the slack."
        },
        {
            "idiom": "Pull strings",
            "meaning": "Использовать связи",
            "example": "He pulled some strings to get the contract approved quickly."
        },
        {
            "idiom": "Put on the back burner",
            "meaning": "Отложить на потом",
            "example": "Let's put this issue on the back burner until next quarter."
        },
        {
            "idiom": "Square one",
            "meaning": "Начальная точка",
            "example": "The system crashed, so we're back to square one."
        },
        {
            "idiom": "Take the helm",
            "meaning": "Взять руководство",
            "example": "Sarah will take the helm while the manager is on vacation."
        },
        {
            "idiom": "Think big",
            "meaning": "Ставить амбициозные цели",
            "example": "We need to think big if we want to compete globally."
        },
        {
            "idiom": "Touch and go",
            "meaning": "Рискованная, неопределенная ситуация",
            "example": "The negotiations were touch and go for several hours."
        },
        {
            "idiom": "Up to speed",
            "meaning": "В курсе дела, полностью информирован",
            "example": "I'll bring you up to speed on the project during our meeting."
        },
        {
            "idiom": "Wheelhouse",
            "meaning": "Область компетенции",
            "example": "Digital marketing is really in her wheelhouse."
        },
        {
            "idiom": "Zero in on",
            "meaning": "Сосредоточиться на чем-то конкретном",
            "example": "We need to zero in on our target market."
        },
        {
            "idiom": "Ahead of the curve",
            "meaning": "Опережающий тенденции",
            "example": "Their company is always ahead of the curve with new technology."
        },
        {
            "idiom": "Bite the bullet",
            "meaning": "Решиться на неприятное действие",
            "example": "We'll have to bite the bullet and cut costs."
        },
        {
            "idiom": "Crunch time",
            "meaning": "Критический момент",
            "example": "It's crunch time - we have to finish by tomorrow."
        },
        {
            "idiom": "Dot the i's and cross the t's",
            "meaning": "Проверить все детали",
            "example": "Before we submit, let's dot the i's and cross the t's."
        }
    ],
    "communication": [
        {
            "idiom": "Beat around the bush",
            "meaning": "Ходить вокруг да около, не говорить прямо",
            "example": "Stop beating around the bush and tell me what you really think."
        },
        {
            "idiom": "Get straight to the point",
            "meaning": "Перейти сразу к сути дела",
            "example": "Let's get straight to the point - we need to cut costs."
        },
        {
            "idiom": "Read between the lines",
            "meaning": "Понимать скрытый смысл",
            "example": "You need to read between the lines to understand what he's really saying."
        },
        {
            "idiom": "Talk someone's ear off",
            "meaning": "Заговаривать до смерти, очень много говорить",
            "example": "My uncle talked my ear off about his fishing trip for two hours."
        },
        {
            "idiom": "Hold your tongue",
            "meaning": "Прикусить язык, промолчать",
            "example": "I had to hold my tongue during the meeting to avoid an argument."
        },
        {
            "idiom": "Spill the beans",
            "meaning": "Выболтать секрет, раскрыть информацию",
            "example": "Who spilled the beans about the surprise party?"
        },
        {
            "idiom": "Let the cat out of the bag",
            "meaning": "Выдать секрет случайно",
            "example": "I accidentally let the cat out of the bag about their engagement."
        },
        {
            "idiom": "Break the ice",
            "meaning": "Разрядить обстановку, начать разговор",
            "example": "He told a joke to break the ice at the awkward dinner."
        },
        {
            "idiom": "Cut to the chase",
            "meaning": "Перейти к самому важному",
            "example": "I don't have much time, so let's cut to the chase."
        },
        {
            "idiom": "Speak of the devil",
            "meaning": "Лёгок на помине",
            "example": "Speak of the devil - we were just talking about you!"
        },
        {
            "idiom": "Give someone a piece of your mind",
            "meaning": "Высказать все, что думаешь",
            "example": "I'm going to give him a piece of my mind about his behavior."
        },
        {
            "idiom": "Bite your tongue",
            "meaning": "Сдержаться и не сказать чего-то",
            "example": "I had to bite my tongue when she made that rude comment."
        },
        {
            "idiom": "Speak volumes",
            "meaning": "Многое сказать, быть очень показательным",
            "example": "Her silence spoke volumes about her true feelings."
        },
        {
            "idiom": "Talk turkey",
            "meaning": "Говорить серьезно и прямо",
            "example": "It's time to talk turkey about our business partnership."
        },
        {
            "idiom": "Shoot the breeze",
            "meaning": "Болтать о пустяках",
            "example": "We spent the afternoon shooting the breeze on the porch."
        },
        {
            "idiom": "Hear it through the grapevine",
            "meaning": "Узнать по слухам",
            "example": "I heard it through the grapevine that they're getting divorced."
        },
        {
            "idiom": "Get the wrong end of the stick",
            "meaning": "Неправильно понять",
            "example": "You've got the wrong end of the stick - I never said that."
        },
        {
            "idiom": "Put words in someone's mouth",
            "meaning": "Приписывать кому-то слова, которых он не говорил",
            "example": "Don't put words in my mouth - that's not what I said."
        },
        {
            "idiom": "Talk behind someone's back",
            "meaning": "Сплетничать за спиной",
            "example": "I hate it when people talk behind my back."
        },
        {
            "idiom": "Speak the same language",
            "meaning": "Понимать друг друга",
            "example": "We speak the same language when it comes to business ethics."
        },
        {
            "idiom": "Keep someone in the loop",
            "meaning": "Держать в курсе дел",
            "example": "Please keep me in the loop about any changes to the project."
        },
        {
            "idiom": "Get your wires crossed",
            "meaning": "Неправильно понять друг друга",
            "example": "We must have gotten our wires crossed about the meeting time."
        },
        {
            "idiom": "Talk at cross purposes",
            "meaning": "Говорить о разном, не понимать друг друга",
            "example": "We were talking at cross purposes the whole time."
        },
        {
            "idiom": "Break your silence",
            "meaning": "Нарушить молчание, заговорить",
            "example": "After years of silence, she finally broke her silence about the incident."
        },
        {
            "idiom": "Speak off the cuff",
            "meaning": "Говорить без подготовки, импровизировать",
            "example": "He gave an amazing speech completely off the cuff."
        },
        {
            "idiom": "Mince words",
            "meaning": "Смягчать выражения, говорить не прямо",
            "example": "I won't mince words - your work has been terrible lately."
        },
        {
            "idiom": "Talk shop",
            "meaning": "Говорить о работе в нерабочее время",
            "example": "Let's not talk shop during dinner - we're here to relax."
        },
        {
            "idiom": "Have a word with someone",
            "meaning": "Поговорить с кем-то (обычно серьезно)",
            "example": "I need to have a word with you about your punctuality."
        },
        {
            "idiom": "Get a word in edgewise",
            "meaning": "Вставить слово в разговор",
            "example": "She talks so much, I can't get a word in edgewise."
        },
        {
            "idiom": "Speak your mind",
            "meaning": "Говорить то, что думаешь",
            "example": "I appreciate that you always speak your mind honestly."
        },
        {
            "idiom": "Talk in circles",
            "meaning": "Ходить вокруг да около в разговоре",
            "example": "Stop talking in circles and give me a straight answer."
        },
        {
            "idiom": "Break it to someone gently",
            "meaning": "Сообщить плохие новости мягко",
            "example": "How should I break it to her gently that she didn't get the job?"
        },
        {
            "idiom": "Hush-hush",
            "meaning": "Секретный, конфиденциальный",
            "example": "The project is very hush-hush - don't tell anyone."
        },
        {
            "idiom": "Spill your guts",
            "meaning": "Выложить все, исповедаться",
            "example": "After a few drinks, he spilled his guts about his problems."
        },
        {
            "idiom": "Put it bluntly",
            "meaning": "Сказать прямо, без обиняков",
            "example": "To put it bluntly, your proposal is not good enough."
        },
        {
            "idiom": "Talk through your hat",
            "meaning": "Говорить чепуху, нести вздор",
            "example": "He's talking through his hat - he knows nothing about the subject."
        },
        {
            "idiom": "Have the gift of the gab",
            "meaning": "Иметь дар красноречия",
            "example": "Salespeople need to have the gift of the gab."
        },
        {
            "idiom": "Speak too soon",
            "meaning": "Сказать что-то преждевременно",
            "example": "I spoke too soon - the problem turned out to be more serious."
        },
        {
            "idiom": "Keep it under your hat",
            "meaning": "Держать в секрете",
            "example": "This information is confidential, so keep it under your hat."
        },
        {
            "idiom": "Talk someone into something",
            "meaning": "Уговорить кого-то сделать что-то",
            "example": "She talked me into going to the party even though I was tired."
        },
        {
            "idiom": "Talk someone out of something",
            "meaning": "Отговорить кого-то от чего-то",
            "example": "I tried to talk him out of quitting his job."
        },
        {
            "idiom": "Speak your piece",
            "meaning": "Высказать свое мнение",
            "example": "Everyone should have a chance to speak their piece."
        },
        {
            "idiom": "Get through to someone",
            "meaning": "Достучаться до кого-то, быть понятым",
            "example": "I can't seem to get through to him - he just won't listen."
        },
        {
            "idiom": "Talk nineteen to the dozen",
            "meaning": "Болтать без остановки",
            "example": "She was talking nineteen to the dozen about her vacation."
        },
        {
            "idiom": "Speak with forked tongue",
            "meaning": "Лгать, говорить неправду",
            "example": "Don't trust him - he speaks with forked tongue."
        },
        {
            "idiom": "Break the news",
            "meaning": "Сообщить новость",
            "example": "How should we break the news to the children?"
        },
        {
            "idiom": "Talk big",
            "meaning": "Хвастаться, преувеличивать",
            "example": "He talks big, but he rarely delivers on his promises."
        },
        {
            "idiom": "Speak out of turn",
            "meaning": "Высказаться невпопад, не к месту",
            "example": "I apologize if I spoke out of turn during the meeting."
        },
        {
            "idiom": "Get something off your chest",
            "meaning": "Высказаться, облегчить душу",
            "example": "I need to get this off my chest - I made a mistake."
        },
        {
            "idiom": "Talk the talk",
            "meaning": "Говорить правильно, но не обязательно действовать",
            "example": "He talks the talk, but can he walk the walk?"
        },
        {
            "idiom": "Speak in riddles",
            "meaning": "Говорить загадками",
            "example": "Stop speaking in riddles and tell me what you mean."
        },
        {
            "idiom": "Break your word",
            "meaning": "Нарушить обещание",
            "example": "I never break my word - you can trust me."
        },
        {
            "idiom": "Talk sense into someone",
            "meaning": "Убедить кого-то быть разумным",
            "example": "Someone needs to talk some sense into him before he makes a mistake."
        },
        {
            "idiom": "Speak highly of someone",
            "meaning": "Хорошо отзываться о ком-то",
            "example": "Your former boss speaks very highly of you."
        },
        {
            "idiom": "Get the message across",
            "meaning": "Донести мысль",
            "example": "I'm trying to get the message across that we need to work harder."
        },
        {
            "idiom": "Talk yourself into a corner",
            "meaning": "Загнать себя в угол словами",
            "example": "Be careful not to talk yourself into a corner during negotiations."
        },
        {
            "idiom": "Speak from experience",
            "meaning": "Говорить на основе собственного опыта",
            "example": "I speak from experience when I say that starting a business is hard."
        },
        {
            "idiom": "Break into conversation",
            "meaning": "Вмешаться в разговор",
            "example": "It's rude to break into other people's conversations."
        },
        {
            "idiom": "Talk until you're blue in the face",
            "meaning": "Говорить до посинения, безрезультатно",
            "example": "You can talk until you're blue in the face, but I won't change my mind."
        },
        {
            "idiom": "Speak your truth",
            "meaning": "Говорить свою правду",
            "example": "It's important to speak your truth, even when it's difficult."
        },
        {
            "idiom": "Get straight from the horse's mouth",
            "meaning": "Узнать из первых рук",
            "example": "I got the news straight from the horse's mouth - the CEO told me himself."
        },
        {
            "idiom": "Talk a mile a minute",
            "meaning": "Говорить очень быстро",
            "example": "She was so excited she was talking a mile a minute."
        },
        {
            "idiom": "Speak with one voice",
            "meaning": "Говорить единогласно",
            "example": "The team needs to speak with one voice on this issue."
        },
        {
            "idiom": "Break the silence",
            "meaning": "Прервать молчание",
            "example": "The awkward silence was finally broken by the phone ringing."
        },
        {
            "idiom": "Talk out of both sides of your mouth",
            "meaning": "Говорить противоречивые вещи",
            "example": "Politicians often talk out of both sides of their mouths."
        },
        {
            "idiom": "Speak now or forever hold your peace",
            "meaning": "Выскажись сейчас или молчи навсегда",
            "example": "If anyone has any objections, speak now or forever hold your peace."
        }
    ],
    "emotions": [
        {
            "idiom": "On cloud nine",
            "meaning": "На седьмом небе",
            "example": "She was on cloud nine after getting the promotion."
        },
        {
            "idiom": "Down in the dumps",
            "meaning": "В подавленном настроении",
            "example": "He's been down in the dumps since his dog passed away."
        },
        {
            "idiom": "Cool as a cucumber",
            "meaning": "Спокойный как удав",
            "example": "Even during the emergency, she remained cool as a cucumber."
        },
        {
            "idiom": "Bite someone's head off",
            "meaning": "Резко ответить, наброситься",
            "example": "Don't bite my head off, I was just asking a question!"
        },
        {
            "idiom": "Over the moon",
            "meaning": "Невероятно счастлив",
            "example": "She was over the moon when she found out she was pregnant."
        },
        {
            "idiom": "Feeling blue",
            "meaning": "Грустить",
            "example": "I've been feeling blue since my friend moved away."
        },
        {
            "idiom": "On pins and needles",
            "meaning": "В сильном волнении",
            "example": "I was on pins and needles waiting for the test results."
        },
        {
            "idiom": "Like a bear with a sore head",
            "meaning": "Очень раздраженный",
            "example": "Don't talk to him this morning - he's like a bear with a sore head."
        },
        {
            "idiom": "Walking on air",
            "meaning": "Быть счастливым, окрыленным",
            "example": "After their first kiss, he was walking on air for days."
        },
        {
            "idiom": "At the end of one's rope",
            "meaning": "На пределе, больше нет сил терпеть",
            "example": "After the third night without sleep, I'm at the end of my rope."
        },
        {
            "idiom": "Bursting with joy",
            "meaning": "Переполненный радостью",
            "example": "She was bursting with joy when she saw her surprise birthday party."
        },
        {
            "idiom": "Down in the mouth",
            "meaning": "Печальный, унылый",
            "example": "He's been down in the mouth ever since he lost his job."
        },
        {
            "idiom": "Fit to be tied",
            "meaning": "Очень рассерженный",
            "example": "When he saw the mess, he was fit to be tied."
        },
        {
            "idiom": "Get cold feet",
            "meaning": "Испугаться в последний момент",
            "example": "He got cold feet and canceled the wedding the day before."
        },
        {
            "idiom": "Get off on the wrong foot",
            "meaning": "Начать плохо",
            "example": "We got off on the wrong foot, but now we're good friends."
        },
        {
            "idiom": "Give someone the creeps",
            "meaning": "Вызывать неприятное чувство",
            "example": "That old house gives me the creeps."
        },
        {
            "idiom": "Have a heart of gold",
            "meaning": "Быть очень добрым",
            "example": "My grandmother has a heart of gold - she helps everyone."
        },
        {
            "idiom": "Have butterflies in your stomach",
            "meaning": "Волноваться",
            "example": "I always have butterflies in my stomach before a big presentation."
        },
        {
            "idiom": "Hit the roof",
            "meaning": "Сильно разозлиться",
            "example": "My dad hit the roof when he saw the car damage."
        },
        {
            "idiom": "Keep a stiff upper lip",
            "meaning": "Сохранять самообладание",
            "example": "Even though he was scared, he kept a stiff upper lip."
        },
        {
            "idiom": "Like a deer in headlights",
            "meaning": "Оцепенеть от страха/удивления",
            "example": "When they asked her the question, she was like a deer in headlights."
        },
        {
            "idiom": "Lose your temper",
            "meaning": "Выходить из себя",
            "example": "I'm sorry I lost my temper earlier."
        },
        {
            "idiom": "On edge",
            "meaning": "Нервный, взволнованный",
            "example": "I've been on edge all day waiting for the phone call."
        },
        {
            "idiom": "On top of the world",
            "meaning": "На вершине счастья",
            "example": "After winning the championship, the team was on top of the world."
        },
        {
            "idiom": "Out of sorts",
            "meaning": "В плохом настроении",
            "example": "I'm feeling out of sorts today - maybe I'm getting sick."
        },
        {
            "idiom": "Pull yourself together",
            "meaning": "Взять себя в руки",
            "example": "Pull yourself together - you can do this!"
        },
        {
            "idiom": "Shake like a leaf",
            "meaning": "Дрожать от страха",
            "example": "When I heard the noise, I was shaking like a leaf."
        },
        {
            "idiom": "Smile from ear to ear",
            "meaning": "Сильно улыбаться",
            "example": "When she saw her grades, she was smiling from ear to ear."
        },
        {
            "idiom": "Sweat bullets",
            "meaning": "Сильно нервничать",
            "example": "I was sweating bullets during the entire job interview."
        },
        {
            "idiom": "Tear your hair out",
            "meaning": "Быть в отчаянии",
            "example": "I've been tearing my hair out trying to fix this computer problem."
        },
        {
            "idiom": "Tickle pink",
            "meaning": "Быть очень довольным",
            "example": "She was tickled pink with her birthday present."
        },
        {
            "idiom": "Walking on eggshells",
            "meaning": "Быть очень осторожным",
            "example": "Ever since their argument, I've been walking on eggshells around them."
        },
        {
            "idiom": "Wearing your heart on your sleeve",
            "meaning": "Открыто показывать чувства",
            "example": "She always wears her heart on her sleeve, so you know exactly how she feels."
        },
        {
            "idiom": "With a heavy heart",
            "meaning": "С тяжелым сердцем",
            "example": "With a heavy heart, I must announce my resignation."
        },
        {
            "idiom": "A chip on your shoulder",
            "meaning": "Обиженный на весь мир",
            "example": "He's had a chip on his shoulder ever since he was passed over for promotion."
        },
        {
            "idiom": "All ears",
            "meaning": "Весь внимание",
            "example": "Tell me what happened - I'm all ears."
        },
        {
            "idiom": "Beside yourself",
            "meaning": "Вне себя от эмоций",
            "example": "She was beside herself with worry when her son didn't come home."
        },
        {
            "idiom": "Black mood",
            "meaning": "Очень плохое настроение",
            "example": "He's in one of his black moods today - better leave him alone."
        },
        {
            "idiom": "Blow your top",
            "meaning": "Взорваться от гнева",
            "example": "When he saw the mess, he blew his top."
        },
        {
            "idiom": "Cheer up",
            "meaning": "Развеселиться",
            "example": "Cheer up! Things will get better."
        },
        {
            "idiom": "Cold-blooded",
            "meaning": "Хладнокровный, безэмоциональный",
            "example": "It was a cold-blooded murder."
        },
        {
            "idiom": "Cry your eyes out",
            "meaning": "Громко плакать",
            "example": "She cried her eyes out at the end of the movie."
        },
        {
            "idiom": "Feeling under the weather",
            "meaning": "Плохо себя чувствовать",
            "example": "I'm feeling under the weather, so I'm going to stay home."
        },
        {
            "idiom": "Fly off the handle",
            "meaning": "Внезапно разозлиться",
            "example": "He flies off the handle at the smallest things."
        },
        {
            "idiom": "Get carried away",
            "meaning": "Увлечься, потерять контроль",
            "example": "I got carried away and spent too much money."
        },
        {
            "idiom": "Get on someone's nerves",
            "meaning": "Действовать кому-то на нервы",
            "example": "His constant humming is getting on my nerves."
        },
        {
            "idiom": "Go to pieces",
            "meaning": "Распасться на части (эмоционально)",
            "example": "She went to pieces when she heard the bad news."
        },
        {
            "idiom": "Green with envy",
            "meaning": "Зеленый от зависти",
            "example": "When she saw her friend's new car, she was green with envy."
        },
        {
            "idiom": "Have a soft spot for",
            "meaning": "Испытывать слабость к",
            "example": "I have a soft spot for stray animals."
        },
        {
            "idiom": "Hot-headed",
            "meaning": "Вспыльчивый",
            "example": "He's too hot-headed to be a good manager."
        },
        {
            "idiom": "In high spirits",
            "meaning": "В приподнятом настроении",
            "example": "The team was in high spirits after their victory."
        },
        {
            "idiom": "Jump for joy",
            "meaning": "Прыгать от радости",
            "example": "The children were jumping for joy when school was canceled."
        },
        {
            "idiom": "Let your hair down",
            "meaning": "Расслабиться, отдохнуть",
            "example": "It's Friday night - time to let your hair down!"
        },
        {
            "idiom": "Lighten up",
            "meaning": "Расслабиться, не принимать близко к сердцу",
            "example": "Lighten up! It's just a game."
        },
        {
            "idiom": "Lose your cool",
            "meaning": "Потерять самообладание",
            "example": "I'm sorry I lost my cool during the meeting."
        }
    ],
    "everyday": [
        {
            "idiom": "Break the ice",
            "meaning": "Разрядить обстановку",
            "example": "He told a funny story to break the ice at the party."
        },
        {
            "idiom": "Piece of cake",
            "meaning": "Очень просто",
            "example": "The test was a piece of cake for her."
        },
        {
            "idiom": "Cost an arm and a leg",
            "meaning": "Очень дорого",
            "example": "This new phone costs an arm and a leg."
        },
        {
            "idiom": "Break a leg",
            "meaning": "Ни пуха ни пера",
            "example": "Break a leg on your performance tonight!"
        },
        {
            "idiom": "Hit the hay",
            "meaning": "Идти спать",
            "example": "I'm exhausted, I'm going to hit the hay."
        },
        {
            "idiom": "Let the cat out of the bag",
            "meaning": "Выдать секрет",
            "example": "He accidentally let the cat out of the bag about the surprise party."
        },
        {
            "idiom": "Once in a blue moon",
            "meaning": "Очень редко",
            "example": "He only visits his parents once in a blue moon."
        },
        {
            "idiom": "Spill the beans",
            "meaning": "Выдать секрет, раскрыть информацию",
            "example": "Come on, spill the beans about what happened!"
        },
        {
            "idiom": "The ball is in your court",
            "meaning": "Теперь ваш ход, ваша очередь действовать",
            "example": "I've made my offer, now the ball is in your court."
        },
        {
            "idiom": "Under the weather",
            "meaning": "Нездоровиться, плохо себя чувствовать",
            "example": "I'm feeling a bit under the weather today."
        },
        {
            "idiom": "Burn the midnight oil",
            "meaning": "Работать допоздна",
            "example": "She's been burning the midnight oil to finish her thesis."
        },
        {
            "idiom": "Hit the nail on the head",
            "meaning": "Попасть в точку",
            "example": "You really hit the nail on the head with that analysis."
        },
        {
            "idiom": "Bite off more than you can chew",
            "meaning": "Взять на себя больше, чем можешь сделать",
            "example": "I think I bit off more than I can chew with this project."
        },
        {
            "idiom": "Cry over spilled milk",
            "meaning": "Переживать из-за того, что уже произошло",
            "example": "There's no use crying over spilled milk - let's just fix the problem."
        },
        {
            "idiom": "Cut to the chase",
            "meaning": "Перейти к сути дела",
            "example": "Let's cut to the chase - how much will it cost?"
        },
        {
            "idiom": "Get out of hand",
            "meaning": "Выйти из-под контроля",
            "example": "The party got completely out of hand last night."
        },
        {
            "idiom": "Give someone the cold shoulder",
            "meaning": "Игнорировать кого-то",
            "example": "She's been giving me the cold shoulder since our argument."
        },
        {
            "idiom": "Go with the flow",
            "meaning": "Принимать события такими, какие они есть",
            "example": "I don't have a plan, I'm just going with the flow."
        },
        {
            "idiom": "Hang in there",
            "meaning": "Держаться, не сдаваться",
            "example": "I know it's tough, but just hang in there a bit longer."
        },
        {
            "idiom": "In hot water",
            "meaning": "В неприятной ситуации",
            "example": "He's in hot water with his boss for being late again."
        },
        {
            "idiom": "Jump on the bandwagon",
            "meaning": "Присоединиться к популярному делу",
            "example": "Everyone's jumping on the bandwagon and buying electric cars."
        },
        {
            "idiom": "Kill two birds with one stone",
            "meaning": "Сделать два дела одновременно",
            "example": "By studying during my commute, I kill two birds with one stone."
        },
        {
            "idiom": "Let sleeping dogs lie",
            "meaning": "Не будить лиха",
            "example": "I decided to let sleeping dogs lie and not bring up the old argument."
        },
        {
            "idiom": "Miss the boat",
            "meaning": "Упустить возможность",
            "example": "If we don't order now, we'll miss the boat on the discount."
        },
        {
            "idiom": "On the ball",
            "meaning": "Внимательный, эффективный",
            "example": "You need to be on the ball during the exam."
        },
        {
            "idiom": "Pull someone's leg",
            "meaning": "Подшучивать над кем-то",
            "example": "I'm just pulling your leg - of course I'll help you move."
        },
        {
            "idiom": "Rain on someone's parade",
            "meaning": "Испортить кому-то удовольствие",
            "example": "I don't want to rain on your parade, but we're over budget."
        },
        {
            "idiom": "Sit on the fence",
            "meaning": "Занимать нейтральную позицию",
            "example": "You can't sit on the fence forever - you need to make a decision."
        },
        {
            "idiom": "Speak of the devil",
            "meaning": "Лёгок на помине",
            "example": "Speak of the devil - we were just talking about you!"
        },
        {
            "idiom": "Take with a grain of salt",
            "meaning": "Относиться скептически",
            "example": "Take his advice with a grain of salt - he's not an expert."
        },
        {
            "idiom": "Through thick and thin",
            "meaning": "В хорошие и плохие времена",
            "example": "They've stayed together through thick and thin."
        },
        {
            "idiom": "Turn over a new leaf",
            "meaning": "Начать новую жизнь",
            "example": "After the holidays, I'm turning over a new leaf and getting healthy."
        },
        {
            "idiom": "Up in the air",
            "meaning": "Неопределенный, нерешенный",
            "example": "Our vacation plans are still up in the air."
        },
        {
            "idiom": "When pigs fly",
            "meaning": "Никогда",
            "example": "He'll clean his room when pigs fly."
        },
        {
            "idiom": "Your guess is as good as mine",
            "meaning": "Я тоже не знаю",
            "example": "When will it be ready? Your guess is as good as mine."
        },
        {
            "idiom": "A blessing in disguise",
            "meaning": "Скрытое благо",
            "example": "Losing that job was a blessing in disguise - I found a better one."
        },
        {
            "idiom": "Add fuel to the fire",
            "meaning": "Усугублять ситуацию",
            "example": "Don't add fuel to the fire by arguing back."
        },
        {
            "idiom": "Beat around the bush",
            "meaning": "Ходить вокруг да около",
            "example": "Stop beating around the bush and tell me what you want."
        },
        {
            "idiom": "Bite the dust",
            "meaning": "Потерпеть неудачу",
            "example": "Another small business bites the dust."
        },
        {
            "idiom": "Blow off steam",
            "meaning": "Выпускать пар",
            "example": "After work, I go to the gym to blow off steam."
        },
        {
            "idiom": "Call it a day",
            "meaning": "Заканчивать работу",
            "example": "It's getting late, let's call it a day."
        },
        {
            "idiom": "Cut someone some slack",
            "meaning": "Быть менее строгим",
            "example": "Cut him some slack - it's his first day."
        },
        {
            "idiom": "Get a taste of your own medicine",
            "meaning": "Попасть в ту же ситуацию",
            "example": "Now he knows what it feels like - he got a taste of his own medicine."
        },
        {
            "idiom": "Get your act together",
            "meaning": "Взять себя в руки",
            "example": "You need to get your act together if you want to pass the exam."
        },
        {
            "idiom": "Give the benefit of the doubt",
            "meaning": "Дать шанс",
            "example": "I'll give him the benefit of the doubt this time."
        },
        {
            "idiom": "Hit the sack",
            "meaning": "Идти спать",
            "example": "It's midnight, time to hit the sack."
        },
        {
            "idiom": "In the same boat",
            "meaning": "В одинаковой ситуации",
            "example": "We're all in the same boat with these budget cuts."
        },
        {
            "idiom": "It takes two to tango",
            "meaning": "Оба виноваты",
            "example": "Don't blame only her - it takes two to tango."
        },
        {
            "idiom": "Keep an eye on",
            "meaning": "Присматривать за",
            "example": "Can you keep an eye on my bag while I use the restroom?"
        },
        {
            "idiom": "Make a long story short",
            "meaning": "Короче говоря",
            "example": "To make a long story short, we missed the flight."
        },
        {
            "idiom": "No pain, no gain",
            "meaning": "Без труда не вытащишь и рыбку из пруда",
            "example": "The workout was hard, but no pain, no gain."
        },
        {
            "idiom": "On the house",
            "meaning": "За счет заведения",
            "example": "Your first drink is on the house."
        }
    ],
    "quick": [
        {
            "idiom": "It's raining cats and dogs",
            "meaning": "Льет как из ведра",
            "example": "Take an umbrella, it's raining cats and dogs outside."
        },
        {
            "idiom": "Beat around the bush",
            "meaning": "Ходить вокруг да около",
            "example": "Stop beating around the bush and tell me what happened."
        },
        {
            "idiom": "Hit the nail on the head",
            "meaning": "Попасть в точку",
            "example": "You hit the nail on the head with that analysis."
        },
        {
            "idiom": "Let the cat out of the bag",
            "meaning": "Выдать секрет",
            "example": "Don't let the cat out of the bag about the surprise party!"
        },
        {
            "idiom": "Once in a blue moon",
            "meaning": "Очень редко",
            "example": "He only visits once in a blue moon."
        },
        {
            "idiom": "A piece of cake",
            "meaning": "Очень просто",
            "example": "The test was a piece of cake for her."
        },
        {
            "idiom": "Break a leg",
            "meaning": "Ни пуха ни пера",
            "example": "Break a leg on your performance tonight!"
        },
        {
            "idiom": "Cost an arm and a leg",
            "meaning": "Очень дорого",
            "example": "That car costs an arm and a leg."
        },
        {
            "idiom": "Cry over spilled milk",
            "meaning": "Переживать о прошлом",
            "example": "Don't cry over spilled milk - what's done is done."
        },
        {
            "idiom": "Cut corners",
            "meaning": "Делать некачественно",
            "example": "If we cut corners, the product won't last."
        },
        {
            "idiom": "Get out of hand",
            "meaning": "Выйти из-под контроля",
            "example": "The party got out of hand last night."
        },
        {
            "idiom": "Give someone the cold shoulder",
            "meaning": "Игнорировать кого-то",
            "example": "She's been giving me the cold shoulder."
        },
        {
            "idiom": "Go the extra mile",
            "meaning": "Делать больше, чем нужно",
            "example": "She always goes the extra mile for her clients."
        },
        {
            "idiom": "Hang in there",
            "meaning": "Держаться",
            "example": "Hang in there, things will get better."
        },
        {
            "idiom": "Hit the hay/sack",
            "meaning": "Идти спать",
            "example": "I'm tired, I'm going to hit the hay."
        },
        {
            "idiom": "In hot water",
            "meaning": "В неприятностях",
            "example": "He's in hot water with his boss."
        },
        {
            "idiom": "Kill two birds with one stone",
            "meaning": "Сделать два дела одновременно",
            "example": "By exercising during lunch, I kill two birds with one stone."
        },
        {
            "idiom": "Let sleeping dogs lie",
            "meaning": "Не будить лиха",
            "example": "I decided to let sleeping dogs lie."
        },
        {
            "idiom": "Miss the boat",
            "meaning": "Упустить возможность",
            "example": "If we don't order now, we'll miss the boat."
        },
        {
            "idiom": "On the ball",
            "meaning": "Внимательный",
            "example": "You need to be on the ball during the exam."
        },
        {
            "idiom": "Pull someone's leg",
            "meaning": "Подшучивать",
            "example": "I'm just pulling your leg!"
        },
        {
            "idiom": "Speak of the devil",
            "meaning": "Лёгок на помине",
            "example": "Speak of the devil - we were just talking about you!"
        },
        {
            "idiom": "The last straw",
            "meaning": "Последняя капля",
            "example": "That was the last straw - I quit!"
        },
        {
            "idiom": "Through thick and thin",
            "meaning": "В хорошие и плохие времена",
            "example": "They've been together through thick and thin."
        },
        {
            "idiom": "Turn a blind eye",
            "meaning": "Закрывать глаза на что-то",
            "example": "The manager turned a blind eye to the problem."
        },
        {
            "idiom": "Under the weather",
            "meaning": "Нездоровиться",
            "example": "I'm feeling under the weather today."
        },
        {
            "idiom": "When pigs fly",
            "meaning": "Никогда",
            "example": "He'll clean his room when pigs fly."
        },
        {
            "idiom": "A blessing in disguise",
            "meaning": "Скрытое благо",
            "example": "Losing that job was a blessing in disguise."
        },
        {
            "idiom": "Add fuel to the fire",
            "meaning": "Усугублять ситуацию",
            "example": "Don't add fuel to the fire by arguing."
        },
        {
            "idiom": "Bite the bullet",
            "meaning": "Решиться на неприятное",
            "example": "We'll have to bite the bullet and tell him."
        },
        {
            "idiom": "Call it a day",
            "meaning": "Заканчивать работу",
            "example": "It's 5 PM, let's call it a day."
        },
        {
            "idiom": "Cut to the chase",
            "meaning": "Перейти к сути",
            "example": "Let's cut to the chase - how much?"
        },
        {
            "idiom": "Every cloud has a silver lining",
            "meaning": "Нет худа без добра",
            "example": "Every cloud has a silver lining - at least now I have more free time."
        },
        {
            "idiom": "Get a taste of your own medicine",
            "meaning": "Попасть в ту же ситуацию",
            "example": "Now he got a taste of his own medicine."
        },
        {
            "idiom": "Give the benefit of the doubt",
            "meaning": "Дать шанс",
            "example": "I'll give him the benefit of the doubt."
        },
        {
            "idiom": "In the same boat",
            "meaning": "В одинаковой ситуации",
            "example": "We're all in the same boat here."
        },
        {
            "idiom": "It takes two to tango",
            "meaning": "Оба виноваты",
            "example": "Remember, it takes two to tango."
        },
        {
            "idiom": "Keep an eye on",
            "meaning": "Присматривать",
            "example": "Can you keep an eye on my bag?"
        },
        {
            "idiom": "Let bygones be bygones",
            "meaning": "Простить и забыть",
            "example": "Let's let bygones be bygones and start fresh."
        },
        {
            "idiom": "Make a long story short",
            "meaning": "Короче говоря",
            "example": "To make a long story short, we missed the flight."
        },
        {
            "idiom": "No pain, no gain",
            "meaning": "Без труда не вытащишь и рыбку из пруда",
            "example": "No pain, no gain - keep exercising!"
        },
        {
            "idiom": "On the house",
            "meaning": "За счет заведения",
            "example": "Your first drink is on the house."
        },
        {
            "idiom": "Practice makes perfect",
            "meaning": "Повторение - мать учения",
            "example": "Keep practicing - practice makes perfect."
        },
        {
            "idiom": "Read between the lines",
            "meaning": "Понимать скрытый смысл",
            "example": "You need to read between the lines."
        },
        {
            "idiom": "Rome wasn't built in a day",
            "meaning": "Москва не сразу строилась",
            "example": "Be patient - Rome wasn't built in a day."
        },
        {
            "idiom": "See eye to eye",
            "meaning": "Быть согласным",
            "example": "We don't always see eye to eye."
        },
        {
            "idiom": "Take it easy",
            "meaning": "Успокоиться",
            "example": "Take it easy, everything will be fine."
        },
        {
            "idiom": "The best of both worlds",
            "meaning": "Все преимущества",
            "example": "Working from home gives me the best of both worlds."
        },
        {
            "idiom": "Time flies",
            "meaning": "Время летит",
            "example": "Time flies when you're having fun!"
        },
        {
            "idiom": "You can't judge a book by its cover",
            "meaning": "Встречают по одежке",
            "example": "Don't judge him by his appearance - you can't judge a book by its cover."
        },
        {
            "idiom": "Your guess is as good as mine",
            "meaning": "Я тоже не знаю",
            "example": "When will it arrive? Your guess is as good as mine."
        }
    ]
}
# Глобальная переменная со всеми идиомами
ALL_IDIOMS = {}

# ============ ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ ============

def load_all_idioms() -> Dict[str, List[Dict]]:
    """Загружает идиомы из встроенных данных"""
    print("📦 Загрузка идиом из встроенных данных...")
    
    # Создаем копию данных, чтобы не менять оригинал
    all_idioms = {}
    for category, idioms in ALL_IDIOMS_DATA.items():
        all_idioms[category] = idioms.copy()
    
    # Создаем категорию "all" со всеми идиомами
    all_idioms_list = []
    for category, idioms in all_idioms.items():
        if category != "all":  # Пропускаем пока категорию "all"
            for idiom in idioms:
                # Убедимся, что категория указана
                idiom['category'] = category
            all_idioms_list.extend(idioms)
    
    all_idioms["all"] = all_idioms_list
    
    # Выводим информацию о загрузке
    total_all = 0
    for category, idioms in all_idioms.items():
        if category != "all":
            count = len(idioms)
            total_all += count
            category_name = CATEGORIES.get(category, category)
            print(f"✅ {category_name}: {count} идиом")
    
    print(f"📊 Всего идиом: {total_all}")
    
    return all_idioms

# ============ СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ ============

user_stats = defaultdict(lambda: {
    'studied': set(),  # изученные идиомы (по названию)
    'correct': 0,
    'total': 0,
    'mistakes': set(),  # идиомы, где были ошибки
    'by_category': defaultdict(lambda: {'studied': 0, 'total': 0})
})

# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

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

def create_keyboard(choices: List[str]) -> InlineKeyboardMarkup:
    keyboard = []
    for i, choice in enumerate(choices):
        display_text = choice[:35] + "..." if len(choice) > 35 else choice
        keyboard.append([InlineKeyboardButton(display_text, callback_data=str(i))])
    return InlineKeyboardMarkup(keyboard)

def create_category_keyboard(mode: str = "study") -> InlineKeyboardMarkup:
    keyboard = []
    
    # Создаем кнопки для всех категорий
    for category_key, category_name in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(
            category_name, 
            callback_data=f"{mode}_{category_key}"
        )])
    
    return InlineKeyboardMarkup(keyboard)

# ============ ОБРАБОТЧИКИ КОМАНД ============

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

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats_data = user_stats[user_id]
    total_idioms = len(ALL_IDIOMS["all"])
    studied_count = len(stats_data['studied'])
    
    if stats_data['total'] > 0:
        accuracy = (stats_data['correct'] / stats_data['total']) * 100
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
        studied_in_cat = stats_data['by_category'][cat_key]['studied']
        
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
{stats_data['correct']} из {stats_data['total']} правильных
({accuracy:.1f}%)

📁 *Прогресс по категориям:*
{chr(10).join(category_stats)}

💡 *Совет:* Продолжайте в том же духе!
"""
    
    keyboard = [
        [InlineKeyboardButton("🎯 Продолжить изучение", callback_data="change_category")],
        [InlineKeyboardButton("🔄 Повторить изученное", callback_data="review_menu")]
    ]
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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

# ============ ОБРАБОТЧИКИ CALLBACK ============

async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    try:
        if "_" not in data:
            await query.edit_message_text("❌ Неверный выбор")
            return
        
        mode, category = data.split("_", 1)
        
        if mode not in ["study", "review"] or category not in CATEGORIES:
            await query.edit_message_text("❌ Неверный выбор категории")
            return
    except Exception as e:
        logger.error(f"Error parsing callback data: {e}")
        await query.edit_message_text("❌ Ошибка обработки запроса")
        return
    
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
    context.user_data['question_count'] = 1
    
    await query.edit_message_text(
        f"{question}\n\n{direction_icon}",
        parse_mode='Markdown',
        reply_markup=create_keyboard(choices)
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    try:
        choice_index = int(query.data)
    except ValueError:
        await query.edit_message_text("❌ Ошибка в данных")
        return
    
    # Получаем данные из контекста
    correct_answer = context.user_data.get('correct_answer')
    choices = context.user_data.get('current_choices', [])
    explanation = context.user_data.get('current_explanation', '')
    category = context.user_data.get('current_category', 'all')
    mode = context.user_data.get('current_mode', 'study')
    direction = context.user_data.get('current_direction', 'en_to_ru')
    category_name = context.user_data.get('current_category_name', 'Все категории')
    
    if not correct_answer or not choices or choice_index >= len(choices):
        await query.edit_message_text("❌ Ошибка данных. Попробуйте начать заново.")
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

async def handle_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "show_stats":
        # Показываем статистику
        stats_data = user_stats[user_id]
        total_idioms = len(ALL_IDIOMS["all"])
        studied_count = len(stats_data['studied'])
        
        if stats_data['total'] > 0:
            accuracy = (stats_data['correct'] / stats_data['total']) * 100
        else:
            accuracy = 0
        
        progress_percent = (studied_count / total_idioms * 100) if total_idioms > 0 else 0
        filled = int(progress_percent / 10)
        progress_bar = "▓" * filled + "░" * (10 - filled)
        
        message = f"""
📊 *Ваша статистика*

🎯 *Общий прогресс:*
{progress_bar} {progress_percent:.0f}%
{studied_count} из {total_idioms} идиом изучено

📈 *Точность ответов:*
{stats_data['correct']} из {stats_data['total']} правильных
({accuracy:.1f}%)
"""
        
        current_mode = context.user_data.get('current_mode', 'study')
        keyboard = [
            [InlineKeyboardButton("➡️ Продолжить", callback_data=f"continue_{context.user_data.get('current_category', 'all')}")]
        ]
        await query.edit_message_text(message, parse_mode='Markdown', 
                                     reply_markup=InlineKeyboardMarkup(keyboard))
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
    
    elif data in ["review_menu", "study_menu"]:
        # Возврат в меню выбора категории
        mode = data.split("_")[0]
        await query.edit_message_text(
            f"📁 Выберите категорию для {'изучения' if mode == 'study' else 'повторения'}:",
            parse_mode='Markdown',
            reply_markup=create_category_keyboard(mode)
        )
        return
    
    elif data.startswith("continue_"):
        # Продолжаем в той же категории
        try:
            category = data.split("_", 1)[1]
        except IndexError:
            category = "all"
        
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

# ============ ОСНОВНАЯ ФУНКЦИЯ ============

def main():
    print("=" * 60)
    print("🎓 Бот для изучения английских идиом")
    print("=" * 60)
    
    # Проверяем наличие токена
    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN not found!")
        print("ℹ️ Please set BOT_TOKEN environment variable")
        return
    
    # Загружаем идиомы
    global ALL_IDIOMS
    ALL_IDIOMS = load_all_idioms()
    
    print(f"\n📊 Всего идиом: {len(ALL_IDIOMS['all'])}")
    print("=" * 60)
    
    try:
        # Создаем приложение
        application = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("study", study))
        application.add_handler(CommandHandler("review", review))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("help", help_command))
        
        # Добавляем обработчики callback-запросов
        application.add_handler(CallbackQueryHandler(
            handle_category_selection, 
            pattern=r"^(study|review)_"
        ))
        
        application.add_handler(CallbackQueryHandler(
            handle_continue,
            pattern=r"^(continue_|change_category|show_stats|review_menu|study_menu)"
        ))
        
        application.add_handler(CallbackQueryHandler(
            handle_answer,
            pattern=r"^\d+$"
        ))
        
        print("🤖 Бот запущен и готов к работе!")
        print("=" * 60)
        print("📱 Перейдите в Telegram и начните с команды /start")
        print("=" * 60)
        
        # ЗАПУСК БОТА - ВАЖНО!
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
# ============ ЗАПУСК ПРОГРАММЫ ============
if __name__ == "__main__":
    main()