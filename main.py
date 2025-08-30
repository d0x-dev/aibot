import requests
import telebot

# ================== CONFIG ==================
BOT_TOKEN = "8320534432:AAFPzKpzxWMAPS7aBBYmW-MuOPnOYvxPDOc"   # Replace with your Telegram Bot Token
NVIDIA_API_KEY = "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"
# =============================================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Function to call NVIDIA API
def chat_with_nvidia(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "nvidia/llama3-chatqa-1.5-8b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error contacting NVIDIA API: {str(e)}"

# /start command
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(
        message,
        "👋 Hello! I'm your NVIDIA AI-powered bot.\n\n"
        "Use the command:\n"
        "`/ai your prompt`\n\n"
        "Example:\n`/ai Write a short poem about the ocean.`",
        parse_mode="Markdown"
    )

# /ai command
@bot.message_handler(commands=['ai'])
def handle_ai(message):
    try:
        # Extract the prompt after /ai
        prompt = message.text[len('/ai'):].strip()

        if not prompt:
            bot.reply_to(message, "❌ Please type something after /ai.\nExample: `/ai Tell me a joke!`", parse_mode="Markdown")
            return

        waiting_msg = bot.reply_to(message, "🧠 Thinking...")

        ai_response = chat_with_nvidia(prompt)

        # If response includes code blocks (```...```), use Markdown mode
        if "```" in ai_response:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=waiting_msg.message_id,
                text=ai_response,
                parse_mode="Markdown"
            )
        else:
            # Normal text response
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=waiting_msg.message_id,
                text=f"🧠 {ai_response}",
                parse_mode="HTML"
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Run the bot
print("🤖 Bot is running...")
bot.polling(none_stop=True)
