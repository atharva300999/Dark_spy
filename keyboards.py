from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import PRIVATE_CHANNEL_LINK

def get_join_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔒 Join Private Channel", url=PRIVATE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Check", callback_data="check")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔍 Services", callback_data="services")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_services_keyboard():
    keyboard = [
        [InlineKeyboardButton("📲 TG ID → Number", callback_data="tg")],
        [InlineKeyboardButton("🚗 Vehicle", callback_data="vehicle")],
        [InlineKeyboardButton("📜 GST", callback_data="gst")],
        [InlineKeyboardButton("🏦 IFSC", callback_data="ifsc")],
        [InlineKeyboardButton("🔙 Back", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="services")]])
