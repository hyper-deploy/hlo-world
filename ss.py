import os
import threading
import requests
from flask import Flask, request, render_template_string
# নিচের লাইনটিতে InlineKeyboardButton এবং WebAppInfo ইমপোর্ট করা হয়েছে
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from instagrapi import Client

# --- আপনার তথ্য এখানে দিন ---
BOT_TOKEN = '8964988842:AAFYXchGL11zb6K2LfOoEAfnO-IxVtGYBKM'
ADMIN_CHAT_ID = '5428249457'
# এখানে আপনার Render ওয়েবসাইটের লাইভ লিংকটি দিন (যেমন: https://my-app.onrender.com)
WEB_APP_URL = 'https://hlo-world.onrender.com/' 
# -----------------------------

# ১. টেলিগ্রাম বট সেটআপ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ওয়েবসাইট ওপেন করার বাটন তৈরি
    keyboard = [
        [InlineKeyboardButton("🌐 ওয়েবসাইট ওপেন করুন", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # বাটনটি মেসেজের সাথে পাঠানো
    await update.message.reply_text(
        "স্বাগতম! নিচের বাটনে ক্লিক করে ওয়েবসাইটে যান।", 
        reply_markup=reply_markup
    )

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

# ... (বাকি ওয়েবসাইটের কোড আগের মতোই থাকবে) ...
