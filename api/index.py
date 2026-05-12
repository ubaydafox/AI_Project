import os
import json
import asyncio
import logging
from http.server import BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ConversationHandler, filters
)
from telegram.request import HTTPXRequest

# Import project modules
from routine_data_manager import (
    get_current_class, get_next_class, get_weekly_routine,
    get_faculty_info, get_course_info, get_bus_schedule
)
from user_manager import register_user, get_user_batch
from gemini_qa import ask_gemini
from collections import defaultdict, deque
from constants import DEFAULT_BATCH

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Setup logging
logger = logging.getLogger(__name__)

# Fallback batch helper
def get_batch_for_user(user_id: int) -> str:
    batch = get_user_batch(user_id)
    return batch if batch else DEFAULT_BATCH

# Handler functions
async def start_command(update: Update, context):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f'আসসালামু আলাইকুম, {user_name}! 👋\n'
        f'আমি *MetroMate* — তোমার ক্যাম্পাস সহকারী। 🎓\n\n'
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

ASKING_BATCH = 1

async def register_start(update: Update, context):
    await update.message.reply_text(
        '📝 তোমার ব্যাচ কোড লিখো (যেমন: CSE-58B, CSE-60D)\n'
        'বাতিল করতে /cancel লিখো।'
    )
    return ASKING_BATCH

async def register_batch(update: Update, context):
    batch = update.message.text.strip().upper()
    user_id = update.effective_user.id
    student_id = str(user_id)
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

async def register_cancel(update: Update, context):
    await update.message.reply_text('❌ রেজিস্ট্রেশন বাতিল করা হয়েছে।')
    return ConversationHandler.END

async def class_current_command(update, context):
    user_id = update.effective_user.id
    batch = get_batch_for_user(user_id)
    response = get_current_class(target_batch=batch)
    await update.message.reply_text(response, parse_mode='Markdown')

async def next_class_command(update, context):
    user_id = update.effective_user.id
    batch = get_batch_for_user(user_id)
    response = get_next_class(target_batch=batch)
    await update.message.reply_text(response, parse_mode='Markdown')

async def weekly_routine_command(update, context):
    user_id = update.effective_user.id
    batch = get_batch_for_user(user_id)
    response = get_weekly_routine(target_batch=batch)
    await update.message.reply_text(response, parse_mode='Markdown')

async def faculty_info_command(update, context):
    if not context.args:
        await update.message.reply_text('⚠️ অনুগ্রহ করে শিক্ষকের ইনিশিয়াল দিন।', parse_mode='Markdown')
        return
    initial = context.args[0]
    response = get_faculty_info(initial)
    await update.message.reply_text(response, parse_mode='Markdown')

async def course_info_command(update, context):
    if not context.args:
        await update.message.reply_text('⚠️ অনুগ্রহ করে কোর্সের কোড দিন।', parse_mode='Markdown')
        return
    code = context.args[0]
    response = get_course_info(code)
    await update.message.reply_text(response, parse_mode='Markdown')

async def bus_schedule_command(update, context):
    query = " ".join(context.args) if context.args else None
    response = get_bus_schedule(query)
    await update.message.reply_text(response, parse_mode='Markdown')

async def about_us_command(update, context):
    await update.message.reply_text(
        '*MetroMate — Your Campus Assistant* 🤖\n\n'
        'Made with ❤️ for students.',
        parse_mode='Markdown'
    )

user_histories = defaultdict(lambda: deque(maxlen=5))

async def gemini_message_handler(update, context):
    user_text = update.message.text
    user_id = update.effective_user.id if update.effective_user else update.message.chat_id
    batch = get_batch_for_user(user_id)
    user_histories[user_id].append(("User", user_text))
    history = list(user_histories[user_id])
    answer = ask_gemini(user_text, history=history, user_batch=batch)
    user_histories[user_id].append(("Bot", answer))
    await update.message.reply_text(answer)

# Global Application instance
_app = None

async def get_app():
    global _app
    if _app is None:
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN is not set in environment variables.")
            return None
            
        # Configure request with timeouts
        request = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=30.0,
            write_timeout=30.0,
            connect_timeout=30.0
        )
        
        _app = Application.builder().token(BOT_TOKEN).request(request).build()
        
        register_conv = ConversationHandler(
            entry_points=[CommandHandler("register", register_start)],
            states={ASKING_BATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_batch)]},
            fallbacks=[CommandHandler("cancel", register_cancel)],
        )
        _app.add_handler(register_conv)
        _app.add_handler(CommandHandler("start", start_command))
        _app.add_handler(CommandHandler("class_current", class_current_command))
        _app.add_handler(CommandHandler("next_class", next_class_command))
        _app.add_handler(CommandHandler("weekly_routine", weekly_routine_command))
        _app.add_handler(CommandHandler("faculty_info_cse", faculty_info_command))
        _app.add_handler(CommandHandler("course_info", course_info_command))
        _app.add_handler(CommandHandler("bus", bus_schedule_command))
        _app.add_handler(CommandHandler("about_us", about_us_command))
        _app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), gemini_message_handler))
        
        await _app.initialize()
    return _app

# Vercel entry point
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update_data = json.loads(post_data.decode('utf-8'))

            async def process():
                app = await get_app()
                if app:
                    update = Update.de_json(update_data, app.bot)
                    await app.process_update(update)
                else:
                    logger.error("Failed to initialize Telegram Application")

            asyncio.run(process())

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running")
