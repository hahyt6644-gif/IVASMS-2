# -*- coding: utf-8 -*-
# Importing necessary libraries
import asyncio
import re
import httpx
from bs4 import BeautifulSoup
import time
import json
import os
import traceback
from urllib.parse import urljoin
from datetime import datetime, timedelta, timezone
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# --- Flask Server (For Render Port Binding) ---
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is awake and running!"

def run_flask():
    # Render assigns a port dynamically via the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    # run(host="0.0.0.0") exposes the server to the outside world
    app.run(host="0.0.0.0", port=port)

# --- Configuration (Fill in your details) ---
YOUR_BOT_TOKEN = "8390809275:AAH9XsUo7b8e2l2BzqTp3NTEzXBy2FXq_UI"

# ==================== Multiple Admin IDs ====================
ADMIN_CHAT_IDS = ["6300396130"]
# ==========================================================

# Old chat IDs kept for the first run
INITIAL_CHAT_IDS = ["-1005256664442"] 

LOGIN_URL = "https://www.ivasms.com/login"
BASE_URL = "https://www.ivasms.com/"
SMS_API_ENDPOINT = "https://www.ivasms.com/portal/sms/received/getsms"

USERNAME = "tele545tele@gmail.com"
PASSWORD = "amitkr545"

# Increased interval to 30 seconds to prevent overlapping instances
POLLING_INTERVAL_SECONDS = 30 
STATE_FILE = "processed_sms_ids.json" 
CHAT_IDS_FILE = "chat_ids.json"

INLINE_BUTTONS = [
    InlineKeyboardButton("📱 NUMBER CHANNEL", url="https://t.me/mrafrixtech"),
    InlineKeyboardButton("BACKUP CHANNEL", url="https://t.me/auroratechinc"),
    InlineKeyboardButton("OTP GROUP", url="https://t.me/afrixotpgc"),
    InlineKeyboardButton("CONTACT DEV", url="https://t.me/jaden_afrix"),
]

# List of countries
COUNTRY_FLAGS = {
    "Afghanistan": "🇦🇫", "Albania": "🇦🇱", "Algeria": "🇩🇿", "Andorra": "🇦🇩", "Angola": "🇦🇴",
    "Argentina": "🇦🇷", "Armenia": "🇦🇲", "Australia": "🇦🇺", "Austria": "🇦🇹", "Azerbaijan": "🇦🇿",
    "Bahrain": "🇧🇭", "Bangladesh": "🇧🇩", "Belarus": "🇧🇾", "Belgium": "🇧🇪", "Benin": "🇧🇯",
    "Bhutan": "🇧🇹", "Bolivia": "🇧🇴", "Brazil": "🇧🇷", "Bulgaria": "🇧🇬", "Burkina Faso": "🇧🇫",
    "Cambodia": "🇰🇭", "Cameroon": "🇨🇲", "Canada": "🇨🇦", "Chad": "🇹🇩", "Chile": "🇨🇱",
    "China": "🇨🇳", "Colombia": "🇨🇴", "Congo": "🇨🇬", "Croatia": "🇭🇷", "Cuba": "🇨🇺",
    "Cyprus": "🇨🇾", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰", "Egypt": "🇪🇬", "Estonia": "🇪🇪",
    "Ethiopia": "🇪🇹", "Finland": "🇫🇮", "France": "🇫🇷", "Gabon": "🇬🇦", "Gambia": "🇬🇲",
    "Georgia": "🇬🇪", "Germany": "🇩🇪", "Ghana": "🇬🇭", "Greece": "🇬🇷", "Guatemala": "🇬🇹",
    "Guinea": "🇬🇳", "Haiti": "🇭🇹", "Honduras": "🇭🇳", "Hong Kong": "🇭🇰", "Hungary": "🇭🇺",
    "Iceland": "🇮🇸", "India": "🇮🇳", "Indonesia": "🇮🇩", "Iran": "🇮🇷", "Iraq": "🇮🇶",
    "Ireland": "🇮🇪", "Israel": "🇮🇱", "Italy": "🇮🇹", "IVORY COAST": "🇨🇮", "Ivory Coast": "🇨🇮", "Jamaica": "🇯🇲",
    "Japan": "🇯🇵", "Jordan": "🇯🇴", "Kazakhstan": "🇰🇿", "Kenya": "🇰🇪", "Kuwait": "🇰🇼",
    "Kyrgyzstan": "🇰🇬", "Laos": "🇱🇦", "Latvia": "🇱🇻", "Lebanon": "🇱🇧", "Liberia": "🇱🇷",
    "Libya": "🇱🇾", "Lithuania": "🇱🇹", "Luxembourg": "🇱🇺", "Madagascar": "🇲🇬", "Malaysia": "🇲🇾",
    "Mali": "🇲🇱", "Malta": "🇲🇹", "Mexico": "🇲🇽", "Moldova": "🇲🇩", "Monaco": "🇲🇨",
    "Mongolia": "🇲🇳", "Montenegro": "🇲🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿", "Myanmar": "🇲🇲",
    "Namibia": "🇳🇦", "Nepal": "🇳🇵", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Nicaragua": "🇳🇮",
    "Niger": "🇳🇪", "Nigeria": "🇳🇬", "North Korea": "🇰🇵", "North Macedonia": "🇲🇰", "Norway": "🇳🇴",
    "Oman": "🇴🇲", "Pakistan": "🇵🇰", "Panama": "🇵🇦", "Paraguay": "🇵🇾", "Peru": "🇵🇪",
    "Philippines": "🇵🇭", "Poland": "🇵🇱", "Portugal": "🇵🇹", "Qatar": "🇶🇦", "Romania": "🇷🇴",
    "Russia": "🇷🇺", "Rwanda": "🇷🇼", "Saudi Arabia": "🇸🇦", "Senegal": "🇸🇳", "Serbia": "🇷🇸",
    "Sierra Leone": "🇸🇱", "Singapore": "🇸🇬", "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Somalia": "🇸🇴",
    "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Spain": "🇪🇸", "Sri Lanka": "🇱🇰", "Sudan": "🇸🇩",
    "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Syria": "🇸🇾", "Taiwan": "🇹🇼", "Tajikistan": "🇹🇯",
    "Tanzania": "🇹🇿", "Thailand": "🇹🇭", "TOGO": "🇹🇬", "Tunisia": "🇹🇳", "Turkey": "🇹🇷",
    "Turkmenistan": "🇹🇲", "Uganda": "🇺🇬", "Ukraine": "🇺🇦", "United Arab Emirates": "🇦🇪", "United Kingdom": "🇬🇧",
    "United States": "🇺🇸", "Uruguay": "🇺🇾", "Uzbekistan": "🇺🇿", "Venezuela": "🇻🇪", "Vietnam": "🇻🇳",
    "Yemen": "🇾🇪", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼", "Unknown Country": "🏴‍☠️"
}

# Service Keywords
SERVICE_KEYWORDS = {
    "Facebook": ["facebook"], "Google": ["google", "gmail"], "WhatsApp": ["whatsapp"], "Telegram": ["telegram"],
    "Instagram": ["instagram"], "Amazon": ["amazon"], "Netflix": ["netflix"], "LinkedIn": ["linkedin"],
    "Microsoft": ["microsoft", "outlook", "live.com"], "Apple": ["apple", "icloud"], "Twitter": ["twitter"],
    "Snapchat": ["snapchat"], "TikTok": ["tiktok"], "Discord": ["discord"], "Signal": ["signal"],
    "Viber": ["viber"], "IMO": ["imo"], "PayPal": ["paypal"], "Binance": ["binance"],
    "Uber": ["uber"], "Bolt": ["bolt"], "Airbnb": ["airbnb"], "Yahoo": ["yahoo"],
    "Steam": ["steam"], "Blizzard": ["blizzard"], "Foodpanda": ["foodpanda"], "Pathao": ["pathao"],
    "Messenger": ["messenger", "meta"], "Gmail": ["gmail", "google"], "YouTube": ["youtube", "google"],
    "X": ["x", "twitter"], "eBay": ["ebay"], "AliExpress": ["aliexpress"], "Alibaba": ["alibaba"],
    "Flipkart": ["flipkart"], "Outlook": ["outlook", "microsoft"], "Skype": ["skype", "microsoft"],
    "Spotify": ["spotify"], "iCloud": ["icloud", "apple"], "Stripe": ["stripe"], "Cash App": ["cash app", "square cash"],
    "Venmo": ["venmo"], "Zelle": ["zelle"], "Wise": ["wise", "transferwise"], "Coinbase": ["coinbase"],
    "KuCoin": ["kucoin"], "Bybit": ["bybit"], "OKX": ["okx"], "Huobi": ["huobi"],
    "Kraken": ["kraken"], "MetaMask": ["metamask"], "Epic Games": ["epic games", "epicgames"],
    "PlayStation": ["playstation", "psn"], "Xbox": ["xbox", "microsoft"], "Twitch": ["twitch"],
    "Reddit": ["reddit"], "ProtonMail": ["protonmail", "proton"], "Zoho": ["zoho"], "Quora": ["quora"],
    "StackOverflow": ["stackoverflow"], "Indeed": ["indeed"], "Upwork": ["upwork"], "Fiverr": ["fiverr"],
    "Glassdoor": ["glassdoor"], "Booking.com": ["booking.com", "booking"], "Careem": ["careem"],
    "Swiggy": ["swiggy"], "Zomato": ["zomato"], "McDonald's": ["mcdonalds", "mcdonald's"],
    "KFC": ["kfc"], "Nike": ["nike"], "Adidas": ["adidas"], "Shein": ["shein"], "OnlyFans": ["onlyfans"],
    "Tinder": ["tinder"], "Bumble": ["bumble"], "Grindr": ["grindr"], "Line": ["line"],
    "WeChat": ["wechat"], "VK": ["vk", "vkontakte"], "Unknown": ["unknown"]
}

# Service Emojis
SERVICE_EMOJIS = {
    "Telegram": "📩", "WhatsApp": "🟢", "Facebook": "📘", "Instagram": "📸", "Messenger": "💬",
    "Google": "🔍", "Gmail": "✉️", "YouTube": "▶️", "Twitter": "🐦", "X": "❌",
    "TikTok": "🎵", "Snapchat": "👻", "Amazon": "🛒", "eBay": "📦", "AliExpress": "📦",
    "Alibaba": "🏭", "Flipkart": "📦", "Microsoft": "🪟", "Outlook": "📧", "Skype": "📞",
    "Netflix": "🎬", "Spotify": "🎶", "Apple": "🍏", "iCloud": "☁️", "PayPal": "💰",
    "Stripe": "💳", "Cash App": "💵", "Venmo": "💸", "Zelle": "🏦", "Wise": "🌐",
    "Binance": "🪙", "Coinbase": "🪙", "KuCoin": "🪙", "Bybit": "📈", "OKX": "🟠",
    "Huobi": "🔥", "Kraken": "🐙", "MetaMask": "🦊", "Discord": "🗨️", "Steam": "🎮",
    "Epic Games": "🕹️", "PlayStation": "🎮", "Xbox": "🎮", "Twitch": "📺", "Reddit": "👽",
    "Yahoo": "🟣", "ProtonMail": "🔐", "Zoho": "📬", "Quora": "❓", "StackOverflow": "🧑‍💻",
    "LinkedIn": "💼", "Indeed": "📋", "Upwork": "🧑‍💻", "Fiverr": "💻", "Glassdoor": "🔎",
    "Airbnb": "🏠", "Booking.com": "🛏️", "Uber": "🚗", "Lyft": "🚕", "Bolt": "🚖",
    "Careem": "🚗", "Swiggy": "🍔", "Zomato": "🍽️", "Foodpanda": "🍱",
    "McDonald's": "🍟", "KFC": "🍗", "Nike": "👟", "Adidas": "👟", "Shein": "👗",
    "OnlyFans": "🔞", "Tinder": "🔥", "Bumble": "🐝", "Grindr": "😈", "Signal": "🔐",
    "Viber": "📞", "Line": "💬", "WeChat": "💬", "VK": "🌐", "Unknown": "❓"
}

# --- Utility Functions ---
def get_utc_now():
    return datetime.now(timezone.utc)

def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, 'w') as f:
            json.dump(INITIAL_CHAT_IDS, f)
        return INITIAL_CHAT_IDS
    try:
        with open(CHAT_IDS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return INITIAL_CHAT_IDS

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, 'w') as f:
        json.dump(chat_ids, f, indent=4)

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

def load_processed_ids():
    if not os.path.exists(STATE_FILE): return set()
    try:
        with open(STATE_FILE, 'r') as f: return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError): return set()

def save_processed_id(sms_id):
    processed_ids = load_processed_ids()
    processed_ids.add(sms_id)
    with open(STATE_FILE, 'w') as f: json.dump(list(processed_ids), f)

# --- Telegram Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    keyboard = [[INLINE_BUTTONS[0]], [INLINE_BUTTONS[1]], [INLINE_BUTTONS[2]], [INLINE_BUTTONS[3]]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if str(user_id) in ADMIN_CHAT_IDS:
        await update.message.reply_text(
            "Welcome Admin!\nYou can use the following commands:\n"
            "/add_chat <chat_id> - Add a new chat ID\n"
            "/remove_chat <chat_id> - Remove a chat ID\n"
            "/list_chats - List all chat IDs",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("Sorry, you are not authorized to use this bot.", reply_markup=reply_markup)

async def add_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    try:
        new_chat_id = context.args[0]
        chat_ids = load_chat_ids()
        if new_chat_id not in chat_ids:
            chat_ids.append(new_chat_id)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"✅ Chat ID {new_chat_id} successfully added.")
        else:
            await update.message.reply_text(f"⚠️ This chat ID ({new_chat_id}) is already in the list.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid format. Use: /add_chat <chat_id>")

async def remove_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    try:
        chat_id_to_remove = context.args[0]
        chat_ids = load_chat_ids()
        if chat_id_to_remove in chat_ids:
            chat_ids.remove(chat_id_to_remove)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"✅ Chat ID {chat_id_to_remove} successfully removed.")
        else:
            await update.message.reply_text(f"🤔 This chat ID ({chat_id_to_remove}) was not found in the list.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid format. Use: /remove_chat <chat_id>")

async def list_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    
    chat_ids = load_chat_ids()
    if chat_ids:
        message = "📜 Currently registered chat IDs are:\n"
        for cid in chat_ids:
            message += f"- `{escape_markdown(str(cid))}`\n"
        try:
            await update.message.reply_text(message, parse_mode='MarkdownV2')
        except Exception as e:
            plain_message = "📜 Currently registered chat IDs are:\n" + "\n".join(map(str, chat_ids))
            await update.message.reply_text(plain_message)
    else:
        await update.message.reply_text("No chat IDs registered.")

# --- Scraping Logic ---
async def fetch_sms_from_api(client: httpx.AsyncClient, headers: dict, csrf_token: str):
    all_messages = []
    try:
        today = get_utc_now()
        start_date = today - timedelta(days=1)
        from_date_str, to_date_str = start_date.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y')
        first_payload = {'from': from_date_str, 'to': to_date_str, '_token': csrf_token}
        summary_response = await client.post(SMS_API_ENDPOINT, headers=headers, data=first_payload)
        summary_response.raise_for_status()
        summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
        group_divs = summary_soup.find_all('div', {'class': 'pointer'})
        if not group_divs: return []
        
        group_ids = [re.search(r"getDetials\('(.+?)'\)", div.get('onclick', '')).group(1) for div in group_divs if re.search(r"getDetials\('(.+?)'\)", div.get('onclick', ''))]
        numbers_url = urljoin(BASE_URL, "portal/sms/received/getsms/number")
        sms_url = urljoin(BASE_URL, "portal/sms/received/getsms/number/sms")

        for group_id in group_ids:
            numbers_payload = {'start': from_date_str, 'end': to_date_str, 'range': group_id, '_token': csrf_token}
            numbers_response = await client.post(numbers_url, headers=headers, data=numbers_payload)
            numbers_soup = BeautifulSoup(numbers_response.text, 'html.parser')
            number_divs = numbers_soup.select("div[onclick*='getDetialsNumber']")
            if not number_divs: continue
            phone_numbers = [div.text.strip() for div in number_divs]
            
            for phone_number in phone_numbers:
                sms_payload = {'start': from_date_str, 'end': to_date_str, 'Number': phone_number, 'Range': group_id, '_token': csrf_token}
                sms_response = await client.post(sms_url, headers=headers, data=sms_payload)
                sms_soup = BeautifulSoup(sms_response.text, 'html.parser')
                final_sms_cards = sms_soup.find_all('div', class_='card-body')
                
                for card in final_sms_cards:
                    sms_text_p = card.find('p', class_='mb-0')
                    if sms_text_p:
                        sms_text = sms_text_p.get_text(separator='\n').strip()
                        date_str = get_utc_now().strftime('%Y-%m-%d %
