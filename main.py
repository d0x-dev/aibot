import requests
import telebot
import re

# ================== CONFIG ==================
BOT_TOKEN = "8320534432:AAFPzKpzxWMAPS7aBBYmW-MuOPnOYvxPDOc"   # Replace with your Telegram Bot Token
NVIDIA_API_KEY = "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"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================== NVIDIA API ==================
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

# ================== SYNTAX HIGHLIGHTER ==================
def highlight_code(code: str, lang: str = "generic") -> str:
    """Adds very simple syntax highlighting for different languages"""

    if lang == "python":
        keywords = r"\b(def|class|return|if|else|elif|for|while|try|except|import|from|as|with|pass|break|continue|in|not|and|or|is|lambda|yield|True|False|None)\b"
    elif lang in ["js", "javascript"]:
        keywords = r"\b(function|return|if|else|for|while|var|let|const|try|catch|import|from|export|new|this|class|extends|super|true|false|null|undefined)\b"
    elif lang in ["cpp", "c++", "c"]:
        keywords = r"\b(int|float|double|char|void|bool|return|if|else|for|while|class|struct|public|private|protected|include|namespace|using|new|delete|true|false)\b"
    else:
        keywords = r"\b(return|if|else|for|while|class|function|true|false|null|None)\b"  # fallback

    # Bold keywords
    code = re.sub(keywords, r"<b>\1</b>", code)

    # Italic numbers
    code = re.sub(r"\b(\d+)\b", r"<i>\1</i>", code)

    # Italic strings
    code = re.sub(r"(\".*?\"|'.*?')", r"<i>\1</i>", code)

    return code

# ================== TELEGRAM HANDLERS ==================
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(
        message,
        "👋 Hello! I'm your NVIDIA AI-powered bot.<br><br>"
        "Use the command:<br>"
        "<b>/ai your prompt</b><br><br>"
        "Example:<br><pre>/ai Write Python code to say hello</pre>"
    )

@bot.message_handler(commands=['ai'])
def handle_ai(message):
    try:
        # Extract prompt after /ai
        prompt = message.text[len('/ai'):].strip()

        if not prompt:
            bot.reply_to(
                message,
                "❌ Please type something after /ai.<br>Example: <pre>/ai Tell me a joke!</pre>"
            )
            return

        waiting_msg = bot.reply_to(message, "🧠 Thinking...")

        ai_response = chat_with_nvidia(prompt)

        # --- Handle code blocks ---
        if "```" in ai_response:
            # Detect language if specified
            match = re.search(r"```([a-zA-Z0-9+]*)", ai_response)
            lang = match.group(1).lower() if match else "generic"

            # Remove ``` and language markers
            clean_response = re.sub(r"```[a-zA-Z0-9+]*\n?", "", ai_response)
            clean_response = clean_response.replace("```", "").strip()

            # Highlight based on language
            highlighted = highlight_code(clean_response, lang)

            formatted_response = f"<pre>{highlighted}</pre>"
        else:
            formatted_response = ai_response

        # Send formatted response
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=waiting_msg.message_id,
            text=f"🧠 {formatted_response}",
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ================== RUN BOT ==================
print("🤖 Bot is running...")
bot.polling(none_stop=True)
