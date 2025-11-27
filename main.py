import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest
from routine_data_manager import get_current_class, get_weekly_routine, get_faculty_info, get_course_info, get_bus_schedule
from gemini_qa import ask_gemini
from collections import defaultdict, deque

# .env ফাইল থেকে টোকেন লোড করা
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# আপনার ডিফল্ট ব্যাচ সেট করুন
DEFAULT_BATCH = "CSE-58B" # আপনার ব্যাচ কোড এখানে পরিবর্তন করুন

# ==========================================================
# কমান্ড হ্যান্ডলার ফাংশনসমূহ
# ==========================================================

# /start কমান্ড
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f'আসসালামু আলাইকুম, {user_name}! \nআমি MetroMate. ক্যাম্পাসের প্রয়োজনীয় ইনফো তুমি আমার কাছে থেকে জানতে নিচের কমান্ড ফলো করো।\n\n'
        f'ব্যবহারের জন্য নিচের কমান্ডগুলো ব্যবহার করুন:\n'
        f'/start - এই মেসেজটি দেখাবে\n'
        f'/class_current - বর্তমানে কোন ক্লাস চলছে তা জানাবে\n'
        f'/weekly_routine - আপনার ব্যাচের সাপ্তাহিক রুটিন দেখাবে\n'
        f'/faculty_info_cse <initial> - শিক্ষকের পূর্ণ নাম ও তথ্য জানাবে (যেমন: /faculty_info_cse NIR)\n'
        f'/faculty_info_cse <initial> - শিক্ষকের পূর্ণ নাম ও তথ্য জানাবে (যেমন: /faculty_info_cse NIR)\n'
        f'/course_info <code_name> - কোর্সের পূর্ণ নাম ও তথ্য জানাবে (যেমন: /course_info OOP)\n'
        f'/bus - বাসের সময়সূচী জানাবে (যেমন: /bus বা /bus Dhanmondi)\n'
        f'/about_us - বট সম্পর্কে বিস্তারিত জানুন'
    )

# /class_current কমান্ড
async def class_current_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # এখানে ডিফল্ট ব্যাচ ব্যবহার করা হচ্ছে। আপনি চাইলে ইউজার থেকে ব্যাচ ইনপুট নিতে পারেন।
    response = get_current_class(target_batch=DEFAULT_BATCH)
    await update.message.reply_text(response, parse_mode='Markdown')

# /weekly_routine কমান্ড
async def weekly_routine_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # এখানে ডিফল্ট ব্যাচ ব্যবহার করা হচ্ছে।
    response = get_weekly_routine(target_batch=DEFAULT_BATCH)
    await update.message.reply_text(response, parse_mode='Markdown')

# /faculty_info_cse <initial> কমান্ড
async def faculty_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # কমান্ডের পরের অংশ (initial) বের করা
    if not context.args:
        await update.message.reply_text("অনুগ্রহ করে শিক্ষকের ইনিশিয়াল দিন। যেমন: /faculty_info_cse NIR")
        return
        
    initial = context.args[0]
    response = get_faculty_info(initial)
    await update.message.reply_text(response, parse_mode='Markdown')

# /course_info <code_name> কমান্ড
async def course_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # কমান্ডের পরের অংশ (course code) বের করা
    if not context.args:
        await update.message.reply_text("অনুগ্রহ করে কোর্সের কোড দিন। যেমন: /course_info OOP")
        return
        
    code = context.args[0]
    response = get_course_info(code)
    await update.message.reply_text(response, parse_mode='Markdown')

# /bus কমান্ড
async def bus_schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args) if context.args else None
    response = get_bus_schedule(query)
    await update.message.reply_text(response, parse_mode='Markdown')

# /about_us কমান্ড
async def about_us_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*MetroMate - Your Campus Assistant*\n\n"
        "MetroMate একটি স্মার্ট বট যা আপনাকে ক্যাম্পাসের দৈনন্দিন প্রয়োজনে সাহায্য করার জন্য তৈরি করা হয়েছে।\n"
        "এটি আপনাকে ক্লাসের রুটিন, ফ্যাকাল্টি ইনফো এবং বাসের শিডিউল সম্পর্কে তথ্য দিতে পারে।\n\n"
        "Developed by *Abu Ubayda & Nahidul Islam Rony*\n\n"
        "Developed with ❤️ for students.",
        parse_mode='Markdown'
    )

# ==========================================================
# মূল ফাংশন: বট চালু করা
# ==========================================================

def main() -> None:
    if not BOT_TOKEN:
        print("❌ ত্রুটি: BOT_TOKEN পাওয়া যায়নি। .env ফাইল চেক করুন।")
        return

    # Request অবজেক্ট তৈরি করা (টাইমআউট বাড়ানোর জন্য)
    request = HTTPXRequest(connection_pool_size=8, read_timeout=30.0, write_timeout=30.0, connect_timeout=30.0)

    # Application তৈরি করা
    application = Application.builder().token(BOT_TOKEN).request(request).build()

    # কমান্ড হ্যান্ডলারগুলো যুক্ত করা
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("class_current", class_current_command))
    application.add_handler(CommandHandler("weekly_routine", weekly_routine_command))
    application.add_handler(CommandHandler("faculty_info_cse", faculty_info_command))
    application.add_handler(CommandHandler("course_info", course_info_command))
    application.add_handler(CommandHandler("bus", bus_schedule_command))
    application.add_handler(CommandHandler("about_us", about_us_command))

    # Store short-term context: user_id -> deque of (role, message)
    user_histories = defaultdict(lambda: deque(maxlen=5))  # keep last 5 exchanges per user

    # Any text message: Gemini AI answer
    async def gemini_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_text = update.message.text
        user_id = update.effective_user.id if update.effective_user else update.message.chat_id
        # Add user message to history
        user_histories[user_id].append(("User", user_text))
        wait_msg = await update.message.reply_text("⏳ একটু অপেক্ষা করুন...")
        # Pass recent history to Gemini
        history = list(user_histories[user_id])
        answer = ask_gemini(user_text, history=history)
        # Add bot answer to history
        user_histories[user_id].append(("Bot", answer))
        # Delete the wait message and send only the answer
        try:
            await wait_msg.delete()
        except Exception:
            pass
        await update.message.reply_text(answer)

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), gemini_message_handler))

    # বট শুরু করা (এটি চলতে থাকবে যতক্ষণ না আপনি স্টপ করেন)
    print("🚀 বট চালু হয়েছে! Ctrl+C চাপলে বন্ধ হবে।")
    application.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()