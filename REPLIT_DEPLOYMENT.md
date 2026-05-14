# 🚀 Deploying to Replit (24/7 Production VM)

Your agent is now ready for a high-performance deployment on Replit. This setup combines a **FastAPI web server** (for status/health checks) and your **Telegram AI Bot** in a single optimized process.

## 1. Setup on Replit
1. **Create a New Repl**: Log into [Replit](https://replit.com) and create a new Python Repl.
2. **Import Code**: You can either copy-paste these files or use the **GitHub import** feature.
3. **Configure Secrets**:
   Go to the **Secrets** (padlock icon) in the sidebar and add:
   - `TELEGRAM_TOKEN`: Your bot token from @BotFather.
   - `GROQ_API_KEY`: Your Groq API key.
   - `SUPABASE_URL`: Your Supabase URL.
   - `SUPABASE_KEY`: Your Supabase Service Role key.
   - `SERPER_API_KEY`: (If used for research tools).

## 2. Deployment Architecture
- **Web UI**: Replit will automatically detect the web server and provide a public URL. This URL will show a premium "Bot Online" status page.
- **Health Check**: The `/healthz` endpoint is available for monitoring services (like UptimeRobot) if you want extra redundancy.
- **24/7 Deployment**: Replit's **Deployments** feature (usually a paid tier) is recommended for production. If you are on a free tier, the Repl will go to sleep after some inactivity.

## 3. Key Files
- `app.py`: The unified entry point (Web + Bot).
- `.replit` & `replit.nix`: Environment configuration.
- `requirements.txt`: Updated with `fastapi` and `uvicorn`.

## 4. Git Configuration
Since you are moving away from Hugging Face:
1. Initialize a regular git repo: `git init`
2. Add your origin: `git remote add origin <your-repo-url>`
3. Push as usual. Replit integrates seamlessly with GitHub.

## 5. Running
Just hit the **Run** button! Replit will use the command defined in `.replit`:
```bash
python app.py
```

### 🔍 Verification
- **Web UI**: Open the Repl URL (e.g., `https://your-repl-name.user-name.repl.co`) to see the status page.
- **Healthz**: Check `https://your-repl-name.user-name.repl.co/healthz` to confirm the JSON response.
- **Telegram**: Send a message to your bot to ensure it's responding.
