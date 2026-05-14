import os
import asyncio
import logging
import sys
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import uvicorn

# Import your agent logic
from veriable_agent import run_veriable_agent

# ----------------------------
# 1. LOGGING CONFIG
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8080))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start bot in a background task
    asyncio.create_task(run_bot())
    yield

# ----------------------------
# 2. FASTAPI SETUP
# ----------------------------
app = FastAPI(title="Veriable AI Agent Status", lifespan=lifespan)

# Simple health check endpoint
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Modern Status Page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Veriable AI Agent | Status</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --bg: #0f172a;
                --card-bg: rgba(30, 41, 59, 0.7);
                --text: #f8fafc;
                --accent: #10b981;
            }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Outfit', sans-serif;
                background: var(--bg);
                color: var(--text);
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            .container {
                position: relative;
                width: 100%;
                max-width: 500px;
                padding: 2rem;
                text-align: center;
                z-index: 10;
            }
            .glass-card {
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 3rem 2rem;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                animation: fadeIn 1s ease-out;
            }
            .status-blob {
                width: 80px;
                height: 80px;
                background: var(--accent);
                border-radius: 50%;
                margin: 0 auto 1.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 20px var(--accent);
                animation: pulse 2s infinite;
            }
            .status-blob svg { width: 40px; height: 40px; fill: white; }
            h1 { font-size: 2rem; margin-bottom: 0.5rem; letter-spacing: -0.02em; }
            p { color: #94a3b8; font-weight: 300; }
            .badge {
                display: inline-block;
                margin-top: 1.5rem;
                padding: 0.5rem 1rem;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid var(--accent);
                color: var(--accent);
                border-radius: 100px;
                font-size: 0.875rem;
                font-weight: 600;
            }
            .bg-glow {
                position: absolute;
                width: 400px;
                height: 400px;
                background: radial-gradient(circle, var(--primary), transparent 70%);
                filter: blur(100px);
                opacity: 0.2;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 0;
            }
            @keyframes pulse {
                0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
                70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); }
                100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="bg-glow"></div>
        <div class="container">
            <div class="glass-card">
                <div class="status-blob">
                    <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>
                </div>
                <h1>Veriable AI Agent</h1>
                <p>Service is active and polling Telegram...</p>
                <div class="badge">SYSTEM ONLINE</div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ----------------------------
# 3. TELEGRAM BOT SETUP
# ----------------------------

# Security configuration (ported from your original code)
blocked_phrases = ["ignore previous instructions", "reveal your system prompt", "api key", "supabase"]
sensitive_words = ["api key", "token", "password", "supabase"]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_input = update.message.text
    logger.info(f"Received message: {user_input}")

    # Safety checks
    lower_input = user_input.lower()
    for phrase in blocked_phrases:
        if phrase in lower_input:
            await update.message.reply_text("⚠️ I can't help with that request.")
            return

    try:
        # Run agent (offload to thread as it might be synchronous)
        response = await asyncio.to_thread(run_veriable_agent, user_input)
        
        # Sanitization
        for word in sensitive_words:
            if word in response.lower():
                response = "⚠️ I can't share that information."
                break
        
        await update.message.reply_text(response[:4000])
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text("⚠️ Something went wrong. Please try again later.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# ----------------------------
# 4. RUNNER LOGIC
# ----------------------------

async def run_bot():
    """Start the Telegram bot in the background."""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in environment!")
        return

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("Bot is starting...")
    
    # Use context manager for proper lifecycle management
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Keep it running
        while True:
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    # Start bot in a background task
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    # For local testing, usually Replit uses the 'run' command in .replit
    uvicorn.run(app, host="0.0.0.0", port=PORT)
