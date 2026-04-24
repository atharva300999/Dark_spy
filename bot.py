import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_USER_ID
from database import init_db, get_user, create_user, update_points, verify_user
from api_calls import tg_to_number, gst_lookup, vehicle_lookup, ifsc_lookup
from keyboards import get_join_keyboard, get_main_keyboard, get_services_keyboard, get_back_keyboard

logging.basicConfig(level=logging.INFO)

# Messages
WELCOME_MSG = """🙋‍♂ **WELCOME**

━━━━━━━━━━━━━━━━━━
🔒 You must join the private channel first!
Click the button below and then tap CHECK
━━━━━━━━━━━━━━━━━━"""

VERIFIED_MSG = """✅ **VERIFIED!**

Welcome {first_name}! 🎉"""

MAIN_MSG = """👑 **MAIN MENU**

⭐ Your Points: {points}

🔍 Use buttons below to use services"""

SERVICE_MSG = """🔮 **SELECT SERVICE**

Cost: 1 point per lookup"""

RESULT_MSG = """✅ **RESULT**

━━━━━━━━━━━━━━━━━━
{result}
━━━━━━━━━━━━━━━━━━
⚡ Powered by Madara"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u = get_user(user.id)
    if not u:
        create_user(user.id, user.first_name, user.username or "")
        u = get_user(user.id)
    
    if not u["join_verified"]:
        await update.message.reply_text(WELCOME_MSG, reply_markup=get_join_keyboard())
    else:
        await update.message.reply_text(MAIN_MSG.format(points=u["points"]), reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    u = get_user(user_id)
    
    if query.data == "check":
        verify_user(user_id)
        await query.edit_text(VERIFIED_MSG.format(first_name=query.from_user.first_name))
        await query.message.reply_text(MAIN_MSG.format(points=u["points"]), reply_markup=get_main_keyboard())
    
    elif query.data == "main":
        await query.edit_text(MAIN_MSG.format(points=u["points"]), reply_markup=get_main_keyboard())
    
    elif query.data == "services":
        await query.edit_text(SERVICE_MSG, reply_markup=get_services_keyboard())
    
    elif query.data == "balance":
        await query.edit_text(f"💰 **YOUR BALANCE**\n\n⭐ Points: {u['points']}", reply_markup=get_main_keyboard())
    
    elif query.data == "help":
        await query.edit_text("ℹ️ **HELP**\n\nCommands:\n/start - Main menu\n/services - All services\n/balance - Check points\n/redeem - Gift code", reply_markup=get_main_keyboard())
    
    elif query.data in ["tg", "vehicle", "gst", "ifsc"]:
        if u["points"] < 1:
            await query.edit_text("❌ Insufficient points! Need 1 point.", reply_markup=get_main_keyboard())
            return
        context.user_data["service"] = query.data
        msgs = {"tg": "Send Telegram ID:", "vehicle": "Send Vehicle Number:", "gst": "Send GST Number:", "ifsc": "Send IFSC Code:"}
        await query.edit_text(msgs[query.data], reply_markup=get_back_keyboard())
    
    elif query.data == "redeem":
        context.user_data["awaiting_code"] = True
        await query.edit_text("🎁 Send your gift code:", reply_markup=get_back_keyboard())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    u = get_user(user_id)
    
    if not u["join_verified"]:
        await update.message.reply_text("❌ Please join the channel first!")
        return
    
    if context.user_data.get("awaiting_code"):
        code = update.message.text.strip()
        conn = sqlite3.connect("bot_data.db")
        c = conn.cursor()
        c.execute("SELECT points, max_uses, used_count FROM gift_codes WHERE code = ?", (code,))
        row = c.fetchone()
        if row and row[2] < row[1]:
            c.execute("UPDATE gift_codes SET used_count = used_count + 1 WHERE code = ?", (code,))
            update_points(user_id, row[0])
            conn.commit()
            await update.message.reply_text(f"✅ Redeemed {row[0]} points!", reply_markup=get_main_keyboard())
        else:
            await update.message.reply_text("❌ Invalid or expired code!", reply_markup=get_main_keyboard())
        conn.close()
        context.user_data["awaiting_code"] = False
        return
    
    service = context.user_data.get("service")
    if service:
        if u["points"] < 1:
            await update.message.reply_text("❌ Insufficient points!")
            return
        
        update_points(user_id, -1)
        query = update.message.text.strip()
        
        if service == "tg":
            result = tg_to_number(query)
        elif service == "gst":
            result = gst_lookup(query)
        elif service == "vehicle":
            result = vehicle_lookup(query)
        elif service == "ifsc":
            result = ifsc_lookup(query)
        else:
            result = "Unknown service"
        
        await update.message.reply_text(RESULT_MSG.format(result=result), reply_markup=get_services_keyboard())
        context.user_data["service"] = None

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_code"] = True
    await update.message.reply_text("🎁 Send your gift code:")

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
