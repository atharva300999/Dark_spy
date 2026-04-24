import random
import string
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_USER_ID, BOT_TOKEN

def is_admin(user_id):
    return user_id == ADMIN_USER_ID

async def create_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /createcode <points> <max_uses>\nExample: /createcode 10 100")
        return
    
    points = int(args[0])
    max_uses = int(args[1])
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO gift_codes (code, points, max_uses) VALUES (?, ?, ?)", (code, points, max_uses))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(f"✅ Code created!\n\n`{code}`\nPoints: {points}\nMax uses: {max_uses}", parse_mode="Markdown")

async def add_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /addpoints <user_id> <points>")
        return
    
    user_id = int(args[0])
    points = int(args[1])
    
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(f"✅ Added {points} points to user {user_id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    
    from telegram.ext import Application
    app = Application.builder().token(BOT_TOKEN).build()
    
    success = 0
    for user in users:
        try:
            await app.bot.send_message(user[0], f"📢 {msg}")
            success += 1
        except:
            pass
    
    await update.message.reply_text(f"✅ Sent to {success} users")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT SUM(points) FROM users")
    total_points = c.fetchone()[0] or 0
    conn.close()
    
    await update.message.reply_text(f"📊 **STATS**\n\n👥 Users: {total_users}\n⭐ Total Points: {total_points}", parse_mode="Markdown")
