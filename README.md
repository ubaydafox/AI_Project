# 🤖 MetroMate — Your Campus Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white" />
</p>

**MetroMate** is a smart Telegram bot designed to assist university students with their daily routines, faculty information, and general campus queries using AI.

---

## 🌟 Key Features

- 📅 **Smart Routine**: Get current and next class details instantly.
- 📋 **Weekly Schedule**: View your entire week's routine in a formatted message.
- 👨‍🏫 **Faculty Directory**: Search for faculty details using initials.
- 🚌 **Bus Tracker**: Quick access to university bus schedules.
- 🤖 **Gemini AI Chat**: Ask anything about the campus or your courses, and get AI-powered answers.
- 📝 **User Registration**: Set your batch once and get personalized routine updates.

---

## 🛠️ Technology Stack

- **Backend**: Python (python-telegram-bot)
- **AI**: Google Gemini Pro (Generative AI)
- **Deployment**: Vercel Serverless Functions
- **Data Storage**: JSON (Local/Static)
- **Environment**: Python Dotenv for security

---

## 📂 Project Structure

```text
routine_bot_project/
├── api/                # Vercel Serverless entry point (Webhook)
│   └── index.py        # Webhook handler
├── data/               # JSON data storage
│   ├── routine_data.json
│   ├── faculty_info.json
│   ├── course_info.json
│   ├── bus_info.json
│   └── users.json      # User registration data
├── bot_polling.py      # Local development (Polling mode)
├── constants.py        # Shared configuration and constants
├── routine_data_manager.py # Logic for routine and data retrieval
├── user_manager.py     # Logic for user registration and roles
├── gemini_qa.py        # Gemini AI integration logic
├── vercel.json         # Vercel deployment configuration
└── .env                # Environment variables (HIDDEN/IGNORED)
```

---

## 🚀 Getting Started

### 1. Local Development (Polling)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file and add your keys:
   ```text
   BOT_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_google_api_key
   ```
3. Run the bot:
   ```bash
   python bot_polling.py
   ```

### 2. Vercel Deployment (Webhook)
1. Push the code to GitHub.
2. Connect your repository to Vercel.
3. Add `BOT_TOKEN` and `GEMINI_API_KEY` in Vercel's environment variables.
4. Set your Telegram webhook:
   `https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-project.vercel.app`

---

## 🔒 Security Note
This project uses `.env` to store sensitive tokens. **Never commit your `.env` file to GitHub.** If your tokens were accidentally made public, please:
1. **Rotate your Telegram Token** via @BotFather.
2. **Rotate your Gemini API Key** via Google AI Studio.
3. **Scrub Git History** if necessary using `git filter-repo`.

---

## 👨‍💻 Developers
- **Abu Ubayda**
- **Nahidul Islam Rony**

---
*Made with ❤️ for university students.*
