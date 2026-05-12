import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    MessageHandler, ConversationHandler, filters
)
from telegram.request import HTTPXRequest
from routine_data_manager import (
    get_current_class, get_next_class, get_weekly_routine,
    get_faculty_info, get_course_info, get_bus_schedule
)
from user_manager import register_user, get_user_batch, is_admin
from gemini_qa import ask_gemini
from collections import defaultdict, deque
from constants import DEFAULT_BATCH

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging setup


# Fallback batch if a user hasn't registered


# Conversation states for /register
ASKING_BATCH = 1

# ==========================================================
# HELPER
# ==========================================================

def get_batch_for_user(user_id: int) -> str:
    """Return the user's registered batch, or the default."""
    batch = get_user_batch(user_id)
    return batch if batch else DEFAULT_BATCH

# ==========================================================
# /start
# ==========================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f'আসসালামু আলাইকুম, {user_name}! 👋\n'
        f'আমি *MetroMate* — তোমার ক্যাম্পাস সহকারী। 🎓\n\n'
        f'নিচের কমান্ডগুলো ব্যবহার করো:\n\n'
        f'📋 *রেজিস্ট্রেশন*\n'
        f'/register — তোমার ব্যাচ সেট করো\n\n'
        f'📅 *ক্লাস রুটিন*\n'
        f'/class\_current — এখন কোন ক্লাস চলছে\n'
        f'/next\_class — পরবর্তী ক্লাস কোনটি\n'
        f'/weekly\_routine — সাপ্তাহিক রুটিন\n\n'
        f'🔍 *তথ্য অনুসন্ধান*\n'
        f'/faculty\_info\_cse <initial> — শিক্ষকের তথ্য (যেমন: /faculty\_info\_cse NIR)\n'
        f'/course\_info <code> — কোর্সের তথ্য (যেমন: /course\_info OOP)\n'
        f'/bus [স্থান] — বাসের সময়সূচী (যেমন: /bus Tilagor)\n\n'
        f'ℹ️ /about\_us — বট সম্পর্কে জানো\n\n'
        f'💬 অথবা সরাসরি যেকোনো প্রশ্ন টাইপ করো, Gemini AI উত্তর দেবে!',
        parse_mode='Markdown'
    )

# ==========================================================
# /register  (ConversationHandler)
# ==========================================================

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        '📝 তোমার ব্যাচ কোড লিখো (যেমন: CSE-58B, CSE-60D)\n'
        'বাতিল করতে /cancel লিখো।'
    )
    return ASKING_BATCH

async def register_batch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    batch = update.message.text.strip().upper()
    user_id = update.effective_user.id
    student_id = str(user_id)  # using telegram ID as student ID for now

    if register_user(user_id, student_id, batch):
        await update.message.reply_text(
            f'✅ সফলভাবে রেজিস্ট্রেশন সম্পন্ন হয়েছে!\n'
            f'তোমার ব্যাচ: *{batch}*\n\n'
            f'এখন /class\_current বা /weekly\_routine দিয়ে তোমার রুটিন দেখো।',
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text('❌ রেজিস্ট্রেশনে সমস্যা হয়েছে। আবার চেষ্টা করো।')

    return ConversationHandler.END

async def register_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('❌ রেজিস্ট্রেশন বাতিল করা হয়েছে।', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ==========================================================
# /class_current
# ==========================================================

async def class_current_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    batch = get_batch_for_user(user_id)
    response = get_current_class(target_batch=batch)
    await update.message.reply_text(response, parse_mode='Markdown')

# ==========================================================
# /next_class
# ==========================================================

async def next_class_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    batch = get_batch_for_user(user_id)
    response = get_next_class(target_batch=batch)
    await update.message.reply_text(response, parse_mode='Markdown')

# ==========================================================
# /weekly_routine
# ==========================================================

async def weekly_routine_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    batch = get_batch_for_user(user_id)
    response = get_weekly_routine(target_batch=batch)
    await update.message.reply_text(response, parse_mode='Markdown')

# ==========================================================
# /faculty_info_cse
# ==========================================================

async def faculty_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            '⚠️ অনুগ্রহ করে শিক্ষকের ইনিশিয়াল দিন।\n'
            'উদাহরণ: /faculty\_info\_cse NIR',
            parse_mode='Markdown'
        )
        return
    initial = context.args[0]
    response = get_faculty_info(initial)
    await update.message.reply_text(response, parse_mode='Markdown')

# ==========================================================
# /course_info
# ==========================================================

async def course_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            '⚠️ অনুগ্রহ করে কোর্সের কোড দিন।\n'
            'উদাহরণ: /course\_info OOP',
            parse_mode='Markdown'
        )
        return
    code = context.args[0]
    response = get_course_info(code)
    await update.message.reply_text(response, parse_mode='Markdown')

# ==========================================================
# /bus
# ==========================================================

async def bus_schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args) if context.args else None
    response = get_bus_schedule(query)
    await update.message.reply_text(response, parse_mode='Markdown')

# ==========================================================
# /about_us
# ==========================================================

async def about_us_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '*MetroMate — Your Campus Assistant* 🤖\n\n'
        'MetroMate একটি স্মার্ট টেলিগ্রাম বট যা তোমাকে ক্যাম্পাসের দৈনন্দিন '
        'প্রয়োজনে সাহায্য করার জন্য তৈরি করা হয়েছে।\n\n'
        '✅ ক্লাস রুটিন ও পরবর্তী ক্লাস\n'
        '✅ ফ্যাকাল্টি ও কোর্স তথ্য\n'
        '✅ বাসের সময়সূচী\n'
        '✅ Gemini AI দিয়ে যেকোনো প্রশ্নের উত্তর\n\n'
        '👨‍💻 Developed by *Abu Ubayda & Nahidul Islam Rony*\n'
        'Made with ❤️ for students.',
        parse_mode='Markdown'
    )

# ==========================================================
# Gemini AI — free text handler
# ==========================================================

user_histories: dict = defaultdict(lambda: deque(maxlen=5))

async def gemini_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    user_id = update.effective_user.id if update.effective_user else update.message.chat_id
    batch = get_batch_for_user(user_id)

    user_histories[user_id].append(("User", user_text))
    wait_msg = await update.message.reply_text("⏳ একটু অপেক্ষা করুন...")

    history = list(user_histories[user_id])
    answer = ask_gemini(user_text, history=history, user_batch=batch)

    user_histories[user_id].append(("Bot", answer))

    try:
        await wait_msg.delete()
    except Exception:
        pass

    await update.message.reply_text(answer)

# ==========================================================
# main
# ==========================================================

def main() -> None:
    if not BOT_TOKEN:
        print("❌ ত্রুটি: BOT_TOKEN পাওয়া যায়নি। .env ফাইল চেক করুন।")
        return

    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=30.0,
        write_timeout=30.0,
        connect_timeout=30.0
    )

    application = Application.builder().token(BOT_TOKEN).request(request).build()

    # Registration conversation
    register_conv = ConversationHandler(
        entry_points=[CommandHandler("register", register_start)],
        states={
            ASKING_BATCH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register_batch)
            ],
        },
        fallbacks=[CommandHandler("cancel", register_cancel)],
    )

    # Add all handlers
    application.add_handler(register_conv)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("class_current", class_current_command))
    application.add_handler(CommandHandler("next_class", next_class_command))
    application.add_handler(CommandHandler("weekly_routine", weekly_routine_command))
    application.add_handler(CommandHandler("faculty_info_cse", faculty_info_command))
    application.add_handler(CommandHandler("course_info", course_info_command))
    application.add_handler(CommandHandler("bus", bus_schedule_command))
    application.add_handler(CommandHandler("about_us", about_us_command))
    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), gemini_message_handler)
    )

    print("🚀 MetroMate চালু হয়েছে! Ctrl+C চাপলে বন্ধ হবে।")
    application.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()