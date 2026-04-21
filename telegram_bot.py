import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import your agent
from veriable_agent import run_veriable_agent
import logging
import sys

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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
    log_entry = f"\n[{datetime.now()}]\nUser: {user_input}\nAgent: {response}\n" + ("-" * 50)
    
    # Still write to file (optional)
    try:
        with open("agent_logs.txt", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        logger.error(f"Failed to write to log file: {e}")

    # CRITICAL: Also print to console for Hugging Face logs
    print(f"--- INTERACTION LOG ---\n{log_entry}", flush=True)


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
    try:
        await update.message.reply_text(response[:4000])
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        # Try one more time with a smaller timeout
        await update.message.reply_text(response[:4000], write_timeout=60)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Notify user if it's a message update
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ I'm having a bit of trouble connecting to my brain (network timeout). "
                "I've logged the issue, please try again in a few seconds!"
            )
        except:
            pass # If we can't even send the error, nothing much we can do


# ----------------------------
# HEALTH CHECK SERVER (FOR HUGGING FACE)
# ----------------------------

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def log_message(self, format, *args):
        return  # Keep logs clean

def run_health_check_server():
    server = HTTPServer(("0.0.0.0", 7860), HealthCheckHandler)
    print("✅ Health check server started on port 7860")
    server.serve_forever()

# ----------------------------
# MAIN FUNCTION
# ----------------------------

def main():
    # Start health check server in background
    threading.Thread(target=run_health_check_server, daemon=True).start()

    # Build app with significantly increased timeouts for stable Hugging Face hosting
    app = ApplicationBuilder() \
        .token(TELEGRAM_TOKEN) \
        .read_timeout(60) \
        .connect_timeout(60) \
        .write_timeout(60) \
        .pool_timeout(60) \
        .build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    print("🤖 Telegram Bot Running...", flush=True)
    logger.info("Bot polling started with high-timeout configuration...")
    app.run_polling()


# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    main()