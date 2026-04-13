import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from datetime import datetime

# Import your agent
from veriable_agent import run_veriable_agent

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ----------------------------
# SECURITY CONFIG
# ----------------------------

blocked_phrases = [
    "ignore previous instructions",
    "reveal your system prompt",
    "show your prompt",
    "api key",
    "supabase",
    "credentials",
    "internal configuration"
]

sensitive_words = ["api key", "token", "password", "supabase"]


# ----------------------------
# LOGGING FUNCTION
# ----------------------------

def log_interaction(user_input, response):
    with open("agent_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}]\n")
        f.write(f"User: {user_input}\n")
        f.write(f"Agent: {response}\n")
        f.write("-" * 50 + "\n")


# ----------------------------
# MESSAGE HANDLER
# ----------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    print(f"User: {user_input}")

    lower_input = user_input.lower()

    # ----------------------------
    # 1. BLOCK PROMPT INJECTION
    # ----------------------------
    for phrase in blocked_phrases:
        if phrase in lower_input:
            response = "⚠️ I can't help with that request."

            await update.message.reply_text(response)
            log_interaction(user_input, response)
            return

    # ----------------------------
    # 2. HANDLE EMPTY / WEAK INPUT
    # ----------------------------
    if not user_input or len(user_input.strip()) < 5:
        response = "Hmm... I need a bit more detail. Tell me what kind of project or idea you have."

        await update.message.reply_text(response)
        log_interaction(user_input, response)
        return

    # ----------------------------
    # 3. HANDLE VERY LONG INPUT
    # ----------------------------
    if len(user_input) > 1000:
        response = "That’s a lot 😅. Try breaking it into smaller parts so I can help better."

        await update.message.reply_text(response)
        log_interaction(user_input, response)
        return

    # ----------------------------
    # 4. RUN AGENT SAFELY
    # ----------------------------
    try:
        response = run_veriable_agent(user_input)

    except Exception as e:
        print(f"Error: {e}")
        response = "Something went wrong on my end. Try again in a simpler way."

    # ----------------------------
    # 5. OUTPUT SANITIZATION (ANTI-LEAK)
    # ----------------------------
    for word in sensitive_words:
        if word in response.lower():
            response = "⚠️ I can't share that information."
            break

    # ----------------------------
    # 6. HANDLE BAD AGENT OUTPUT
    # ----------------------------
    if not response or len(response.strip()) < 10:
        response = "I’m not sure I understood that. Can you explain your idea a bit more?"

    print(f"Agent: {response}")

    # ----------------------------
    # 7. LOG EVERYTHING
    # ----------------------------
    log_interaction(user_input, response)

    # ----------------------------
    # 8. SEND RESPONSE (Telegram limit)
    # ----------------------------
    await update.message.reply_text(response[:4000])


# ----------------------------
# MAIN FUNCTION
# ----------------------------

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram Bot Running...")
    app.run_polling()


# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    main()