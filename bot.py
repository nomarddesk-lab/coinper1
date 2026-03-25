import os
import threading
import asyncio
from datetime import datetime
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Web Server for Render.com ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Gari Bot is active!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Content (Korean Learning Material for English) ---

LEARNING_CONTENT = [
    # Day 1: Introduction & The "Gari" Concept
    "저희 채널의 이름인 'Gari'는 이웃이 서로를 돕는 것처럼 여러분 곁에 가까이 있겠다는 우리의 목표를 담고 있습니다. 단순히 정보를 전달하는 것이 아니라, 여러분이 '학습 과정'(Gari)을 통해 숙련될 때까지 함께 걸어갑니다.\n\n무엇이 다른가요?\n- 회화 중심: 실제 일상생활에서 바로 사용하는 영어에 집중합니다.\n- 라이브 수업: 궁금한 점을 묻고 발음을 교정받는 대화형 세션입니다.\n- 지원 커뮤니티: 서로 돕고 성장하는 클럽입니다.\n\n환영 선물: 첫 1,000명의 구독자에게는 라이브 수업이 무료로 제공됩니다!",
    
    # Day 2: Why English in 2026?
    "2026년에 영어가 왜 당신의 성공의 열쇠일까요?\n\n오늘날의 세계에서 영어는 더 이상 선택이 아닌 개인적, 전문적 성장을 위한 필수 요소입니다. 과학, 비즈니스, 그리고 글로벌 소통의 언어이기 때문입니다.\n\n많은 사람들이 실제 상호작용이 부족해 수년 동안 공부해도 결과를 얻지 못합니다. Gari 채널은 단순한 이론이 아닌 실제 적용에 집중하는 환경을 통해 이러한 현실을 바꿉니다.\n\n채널의 첫 1,000명 가입자에게 주어지는 무료 기회를 놓치지 마세요!",
    
    # Day 3: Apps vs. Real Practice
    "언어 앱만으로는 유창해지기에 부족한 이유가 무엇일까요?\n\n앱으로 문법은 이해하는데 막상 말하려고 하면 입이 떨어지지 않았던 적이 있나요? 이유는 간단합니다. 언어는 사회적 실천이기 때문입니다. 앱은 정보는 주지만 실제 대화에서 필요한 자신감은 주지 못합니다.\n\nGari의 비전:\n- 즉각적인 교정: 라이브 세션에서 틀린 부분을 바로 잡아드립니다.\n- 단순화된 정보: 영어를 직관적이고 명확하게 설명합니다.\n- 대화형 환경: 그룹 학습을 통해 수줍음을 없앱니다.\n\n선착순 1,000명 한정!"
]

QUIZ_DATA = [
    {
        "question": "'Gari'라는 이름의 주요 목적은 무엇인가요?",
        "options": ["이웃처럼 가까이서 돕기 위해", "전자제품 판매", "배달 서비스"],
        "correct": 0
    },
    {
        "question": "Gari에 따르면 기존 앱에 부족한 점은 무엇인가요?",
        "options": ["예쁜 디자인", "사회적 실천과 자신감", "단어의 양"],
        "correct": 1
    },
    {
        "question": "누가 무료 라이브 수업을 들을 수 있나요?",
        "options": ["모두가 영원히", "아무도 없음", "선착순 1,000명 가입자"],
        "correct": 2
    }
]

# --- Bot Logic ---
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}
    
    # Menu in Korean
    keyboard = [
        ["학습 시작하기 📖", "오늘의 퀴즈 🧠"],
        ["오늘은 여기까지 ✋"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "Gari 학습 봇에 오신 것을 환영합니다! 🏠\n\n"
        "여러분의 유창한 영어 실력을 위해 한 걸음씩 함께하겠습니다.\n"
        "아래 메뉴에서 옵션을 선택하여 시작해 보세요."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}

    if text == "학습 시작하기 📖":
        current_day = user_progress[user_id]["day"]
        today = str(datetime.now().date())
        
        if user_progress[user_id]["last_learned_date"] == today:
            await update.message.reply_text("오늘의 레슨을 이미 완료하셨습니다! 내일 다시 만나요. ✨")
            return

        if current_day < len(LEARNING_CONTENT):
            await update.message.reply_text(LEARNING_CONTENT[current_day])
            user_progress[user_id]["day"] += 1
            user_progress[user_id]["last_learned_date"] = today
        else:
            await update.message.reply_text("준비된 모든 레슨을 완료하셨습니다! 새로운 소식을 기다려 주세요.")

    elif text == "오늘의 퀴즈 🧠":
        current_quiz_idx = user_progress[user_id]["quiz_day"]
        
        if current_quiz_idx < len(QUIZ_DATA):
            q = QUIZ_DATA[current_quiz_idx]
            buttons = [[InlineKeyboardButton(opt, callback_data=f"quiz_{idx}")] for idx, opt in enumerate(q["options"])]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(f"퀴즈 질문:\n\n{q['question']}", reply_markup=reply_markup)
        else:
            await update.message.reply_text("모든 퀴즈를 완료하셨습니다! 참 잘하셨어요.")

    elif text == "오늘은 여기까지 ✋":
        await update.message.reply_text("잠시 휴식을 취하세요! 내일 다시 여정을 이어가길 기다릴게요. ☕")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    current_quiz_idx = user_progress[user_id]["quiz_day"]
    if current_quiz_idx >= len(QUIZ_DATA):
        return

    selected_option = int(query.data.split("_")[1])
    if selected_option == QUIZ_DATA[current_quiz_idx]["correct"]:
        feedback = "정답입니다! ✅\n\n"
    else:
        feedback = "아쉽네요! 하지만 좋은 시도였습니다.\n\n"
    
    feedback += "학습이 아주 잘 진행되고 있습니다. 내일 새로운 질문으로 만나요! 🌟"
    user_progress[user_id]["quiz_day"] += 1
    await query.edit_message_text(text=feedback)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("CRITICAL ERROR: TELEGRAM_TOKEN environment variable is missing.")
        exit(1)
    
    print("Starting Gari Bot (Korean Version)...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.run_polling()
