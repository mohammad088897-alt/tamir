from datetime import datetime
import json
import os
import random
import threading
import time
import telebot
from telebot import types
from flask import Flask

# ===================== BOT CONFIGURATION =====================
TOKEN = "9247884980:AAFz3cgspjn2ND2lVRSdKQwz4BuFp5qtsKs"
OWNER_ID = 7684105339

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "fonex_data.json"

data = {
    "owners": [OWNER_ID],
    "spam_texts": [],
    "spam_delay": 0.1,
    "target_texts": [
        "You are absolute trash, nobody likes you.",
        "Keep talking, your stupidity is entertaining.",
    ],
    "targets": [],
    "friends": [],
    "enemy_targets": [],
    "enemy_texts": ["Get lost!", "Leave me alone, idiot."],
    "friend_texts": [
        "You're an amazing friend, stay awesome! 🌟",
        "Proud to have a loyal friend like you ❤️",
    ],
    "current_emoji": "🎯",
    "reaction_users": [],
    "target_reaction": "✍",
    "anti_chats": [],
    "reply_texts": ["Hello", "Welcome"],
    "bot_active": True,
}

unauthorized_attempts = {}

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
            for key in loaded_data:
                if key in data:
                    data[key] = loaded_data[key]
    except (json.JSONDecodeError, OSError):
        pass


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_owner(user_id):
    return user_id in data["owners"]


active_spams = {}
active_tofans = {}
active_replies = {}
ping_start_time = time.time()


HELP_TEXT = """
<b>𝙈𝘼𝙉𝙐 / 𝙃𝙀𝙇𝙋 🔥</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>𝙎𝙥𝙖𝙢 :</b> 📤
<code>addspam</code> [text]
<code>delspam</code> [number]
<code>listspam</code>
<code>settimespam</code> [seconds]
<code>start</code> [count] [delay]
<code>stopspam</code>

<b>𝙏𝙖𝙧𝙜𝙚𝙩 :</b> 🎯
<code>targed</code>
<code>deltarged</code> [number]
<code>listtarged</code>
<code>setemoji</code> [emoji]
<code>adtext</code>
<code>tofan</code> [count] [delay]
<code>stoptofan</code>

<b>𝙍𝙚𝙥𝙡𝙮 :</b> ⚠️
<code>reply</code> [count] [delay]
<code>stopreply</code>
<code>textreply</code> [text]
<code>listtextreply</code>
<code>deltextreply</code> [number]

<b>𝙀𝙣𝙚𝙢𝙮 :</b> 🧌
<code>enemy</code>
<code>listenemy</code>
<code>textenemy</code> [text]
<code>enemyremove</code>
<code>clearenemytexts</code>

<b>𝙁𝙧𝙞𝙚𝙣𝙙 :</b> 💞
<code>friend</code>
<code>listfriend</code>
<code>textfriend</code> [text]
<code>friendremove</code>
<code>clearfriendtexts</code>

<b>𝙍𝙚𝙖𝙘𝙩𝙞𝙤𝙣 :</b> ✍
<code>listreaction</code>
<code>addreaction</code> [emoji]
<code>addname</code>
<code>stopreaction</code>

<b>𝙊𝙬𝙣𝙚𝙧 :</b> 👨‍💻
<code>addowner</code>
<code>listowner</code>
<code>ownerremove</code>

<b>𝙂𝙚𝙣𝙚𝙧𝙖𝙡 :</b> 📊
<code>stats</code>
<code>ping</code>
<code>onatacker</code>
<code>offatacker</code>
"""


@bot.message_handler(
    func=lambda m: m.text is not None
    and m.text.strip().lower() in ["help", "panel", ".help", "منو", "manu"]
)
def show_panel(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    bot.send_message(
        message.chat.id, HELP_TEXT, parse_mode="HTML"
    )


# ===================== ON / OFF ATACKER =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "onatacker")
def turn_on_bot(message):
    if not is_owner(message.from_user.id):
        return
    data["bot_active"] = True
    save_data()
    bot.reply_to(message, "<b>🟢 𝘽𝙤𝙩 𝙞𝙨 𝙣𝙤𝙬 𝙊𝙉!</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "offatacker")
def turn_off_bot(message):
    if not is_owner(message.from_user.id):
        return
    data["bot_active"] = False
    save_data()
    bot.reply_to(message, "<b>🔴 𝘽𝙤𝙩 𝙞𝙨 𝙣𝙤𝙬 𝙊𝙁𝙁!</b>", parse_mode="HTML")


# ===================== SPAM =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("addspam"))
def add_spam(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(message, "<b>⚠️ 𝙒𝙖𝙧𝙣𝙞𝙣𝙜: 𝙏𝙚𝙭𝙩 𝙧𝙚𝙦𝙪𝙞𝙧𝙚𝙙.</b>", parse_mode="HTML")
        return
    data["spam_texts"].append(text)
    save_data()
    bot.reply_to(message, f"<b>✅ 𝘼𝙙𝙙𝙚𝙙. 𝙏𝙤𝙩𝙖𝙡: {len(data['spam_texts'])}</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("delspam"))
def del_spam(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "<b>⚠️ 𝙐𝙨𝙖𝙜𝙚: delspam [𝙣𝙪𝙢𝙗𝙚𝙧]</b>", parse_mode="HTML")
        return
    idx = int(parts[1]) - 1
    if 0 <= idx < len(data["spam_texts"]):
        data["spam_texts"].pop(idx)
        save_data()
        bot.reply_to(message, "<b>🗑️ 𝘿𝙚𝙡𝙚𝙩𝙚𝙙.</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "<b>❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙞𝙣𝙙𝙚𝙭.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "listspam")
def list_spam(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not data["spam_texts"]:
        bot.reply_to(message, "<b>📂 𝙀𝙢𝙥𝙩𝙮.</b>", parse_mode="HTML")
        return
    text = "<b>📋 𝙎𝙥𝙖𝙢 𝙇𝙞𝙨𝙩:</b>\n" + "\n".join([f"{i}. {t}" for i, t in enumerate(data["spam_texts"], 1)])
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("settimespam"))
def set_time_spam(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "<b>⚠️ 𝙐𝙨𝙖𝙜𝙚: settimespam [𝙨𝙚𝙘𝙤𝙣𝙙𝙨]</b>", parse_mode="HTML")
        return
    try:
        data["spam_delay"] = float(parts[1])
        save_data()
        bot.reply_to(message, f"<b>⏱️ 𝘿𝙚𝙡𝙖𝙮 𝙨𝙚𝙩 𝙩𝙤 {data['spam_delay']}𝙨.</b>", parse_mode="HTML")
    except ValueError:
        bot.reply_to(message, "<b>❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙣𝙪𝙢𝙗𝙚𝙧.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("start") and not m.text.strip().lower().startswith("starttofan"))
def start_spam(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not data["spam_texts"]:
        bot.reply_to(message, "<b>⚠️ 𝙉𝙤 𝙨𝙥𝙖𝙢 𝙩𝙚𝙭𝙩𝙨.</b>", parse_mode="HTML")
        return

    parts = message.text.split()
    count = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 10
    delay = float(parts[2]) if len(parts) >= 3 and parts[2].replace(".", "", 1).isdigit() else data["spam_delay"]

    chat_id = message.chat.id
    active_spams[chat_id] = True

    def spam_worker():
        sent = 0
        while sent < count and active_spams.get(chat_id, False):
            try:
                bot.send_message(chat_id, random.choice(data["spam_texts"]))
                sent += 1
                time.sleep(delay if delay > 0 else 0.0001)
            except Exception:
                time.sleep(0.001)

    threading.Thread(target=spam_worker, daemon=True).start()
    bot.reply_to(message, f"<b>🚀 𝙎𝙩𝙖𝙧𝙩𝙚𝙙! 𝘾𝙤𝙪𝙣𝙩: {count} | 𝘿𝙚𝙡𝙖𝙮: {delay}𝙨</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() in ["stopspam", "stop"])
def stop_all_in_chat(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    chat_id = message.chat.id
    active_spams[chat_id] = False
    active_tofans[chat_id] = False
    active_replies[chat_id] = False
    bot.reply_to(message, "<b>⛔ 𝘼𝙡𝙡 𝙖𝙘𝙩𝙞𝙫𝙞𝙩𝙞𝙚𝙨 𝙨𝙩𝙤𝙥𝙥𝙚𝙙 𝙞𝙣 𝙩𝙝𝙞𝙨 𝙘𝙝𝙖𝙩.</b>", parse_mode="HTML")


# ===================== REPLY SYSTEM =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("reply") and not m.text.strip().lower().startswith("replytext"))
def start_reply_cmd(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "<b>⚠️ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙢𝙚𝙨𝙨𝙖𝙜𝙚.</b>", parse_mode="HTML")
        return

    parts = message.text.split()
    count = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 10
    delay = float(parts[2]) if len(parts) >= 3 and parts[2].replace(".", "", 1).isdigit() else 1.0

    chat_id = message.chat.id
    target_msg_id = message.reply_to_message.message_id
    active_replies[chat_id] = True

    def reply_worker():
        sent = 0
        while sent < count and active_replies.get(chat_id, False):
            try:
                txt = random.choice(data["reply_texts"]) if data["reply_texts"] else "Auto Reply"
                bot.send_message(chat_id, txt, reply_to_message_id=target_msg_id)
                sent += 1
                time.sleep(delay if delay > 0 else 0.1)
            except Exception:
                time.sleep(0.5)

    threading.Thread(target=reply_worker, daemon=True).start()
    bot.reply_to(message, f"<b>🔄 𝙍𝙚𝙥𝙡𝙮 𝙨𝙩𝙖𝙧𝙩𝙚𝙙! 𝘾𝙤𝙪𝙣𝙩: {count} | 𝘿𝙚𝙡𝙖𝙮: {delay}𝙨</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "stopreply")
def stop_reply_cmd(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    chat_id = message.chat.id
    active_replies[chat_id] = False
    bot.reply_to(message, "<b>⛔ 𝙍𝙚𝙥𝙡𝙮 𝙨𝙩𝙤𝙥𝙥𝙚𝙙 𝙞𝙣 𝙩𝙝𝙞𝙨 𝙘𝙝𝙖𝙩.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("textreply"))
def text_reply_cmd(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(message, "<b>⚠️ 𝙐𝙨𝙖𝙜𝙚: textreply [𝙩𝙚𝙭𝙩]</b>", parse_mode="HTML")
        return
    data["reply_texts"].append(text)
    save_data()
    bot.reply_to(message, f"<b>✅ 𝙉𝙚𝙬 𝙧𝙚𝙥𝙡𝙮 𝙩𝙚𝙭𝙩 𝙖𝙙𝙙𝙚𝙙. 𝙏𝙤𝙩𝙖𝙡: {len(data['reply_texts'])}</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "listtextreply")
def list_text_reply(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not data["reply_texts"]:
        bot.reply_to(message, "<b>📂 𝙍𝙚𝙥𝙡𝙮 𝙩𝙚𝙭𝙩𝙨 𝙡𝙞𝙨𝙩 𝙞𝙨 𝙚𝙢𝙥𝙩𝙮.</b>", parse_mode="HTML")
        return
    text = "<b>💬 𝙍𝙚𝙥𝙡𝙮 𝙏𝙚𝙭𝙩𝙨 𝙇𝙞𝙨𝙩:</b>\n" + "\n".join([f"{i}. {t}" for i, t in enumerate(data["reply_texts"], 1)])
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("deltextreply"))
def del_text_reply(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "<b>⚠️ 𝙐𝙨𝙖𝙜𝙚: deltextreply [𝙣𝙪𝙢𝙗𝙚𝙧]</b>", parse_mode="HTML")
        return
    idx = int(parts[1]) - 1
    if 0 <= idx < len(data["reply_texts"]):
        removed = data["reply_texts"].pop(idx)
        save_data()
        bot.reply_to(message, f"<b>🗑️ 𝘿𝙚𝙡𝙚𝙩𝙚𝙙: {removed}</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "<b>❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙞𝙣𝙙𝙚𝙭.</b>", parse_mode="HTML")


# ===================== TARGET =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() in ["targed", "target"])
def add_target(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙪𝙨𝙚𝙧.</b>", parse_mode="HTML")
        return
    tid = message.reply_to_message.from_user.id
    if tid not in data["targets"]:
        data["targets"].append(tid)
        save_data()
    bot.reply_to(message, "<b>🎯 𝙏𝙖𝙧𝙜𝙚𝙩 𝙖𝙙𝙙𝙚𝙙.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("deltarged"))
def del_target(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    
    parts = message.text.split()
    if len(parts) == 2 and parts[1].isdigit():
        idx = int(parts[1]) - 1
        if 0 <= idx < len(data["targets"]):
            removed_tid = data["targets"].pop(idx)
            save_data()
            bot.reply_to(message, f"<b>🗑️ 𝙏𝙖𝙧𝙜𝙚𝙩 𝙧𝙚𝙢𝙤𝙫𝙚𝙙 (𝙄𝘿: {removed_tid}).</b>", parse_mode="HTML")
        else:
            bot.reply_to(message, "<b>❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙞𝙣𝙙𝙚𝙭.</b>", parse_mode="HTML")
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        tid = message.reply_to_message.from_user.id
        if tid in data["targets"]:
            data["targets"].remove(tid)
            save_data()
            bot.reply_to(message, "<b>🗑️ 𝙏𝙖𝙧𝙜𝙚𝙩 𝙧𝙚𝙢𝙤𝙫𝙚𝙙.</b>", parse_mode="HTML")
        else:
            bot.reply_to(message, "<b>❌ 𝙉𝙤𝙩 𝙞𝙣 𝙩𝙖𝙧𝙜𝙚𝙩 𝙡𝙞𝙨𝙩.</b>", parse_mode="HTML")
        return

    bot.reply_to(message, "<b>⚠️ 𝙐𝙨𝙖𝙜𝙚: deltarged [𝙣𝙪𝙢𝙗𝙚𝙧]</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "listtarged")
def list_target(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not data["targets"]:
        bot.reply_to(message, "<b>📂 𝙏𝙖𝙧𝙜𝙚𝙩 𝙡𝙞𝙨𝙩 𝙞𝙨 𝙚𝙢𝙥𝙩𝙮.</b>", parse_mode="HTML")
        return
    
    emoji = data["current_emoji"]
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    list_str = f"<b>🎯 𝙏𝙖𝙧𝙜𝙚𝙩 𝙇𝙞𝙨𝙩 ({len(data['targets'])} 𝙪𝙨𝙚𝙧𝙨):</b>\n"
    for i, tid in enumerate(data["targets"], 1):
        list_str += f"<b>{i}. 𝙄𝘿:</b> <code>{tid}</code>\n"
        markup.add(types.InlineKeyboardButton(f"{emoji} 𝙋𝙧𝙤𝙛𝙞𝙡𝙚 {i} ({tid})", url=f"tg://user?id={tid}"))
        
    bot.reply_to(message, list_str, parse_mode="HTML", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("setemoji"))
def set_emoji(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "<b>⚠️ 𝙐𝙨𝙖𝙜𝙚: setemoji [𝙚𝙢𝙤𝙟𝙞]</b>", parse_mode="HTML")
        return
    data["current_emoji"] = parts[1].strip()
    save_data()
    bot.reply_to(message, f"<b>✅ 𝙀𝙢𝙤𝙟𝙞 𝙪𝙥𝙙𝙖𝙩𝙚𝙙: {data['current_emoji']}</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "adtext")
def ad_text(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙩𝙚𝙭𝙩 𝙤𝙧 𝙛𝙞𝙡𝙚.</b>", parse_mode="HTML")
        return

    target_msg = message.reply_to_message
    content_text = ""
    if target_msg.document:
        try:
            file_info = bot.get_file(target_msg.document.file_id)
            content_text = bot.download_file(file_info.file_path).decode("utf-8")
        except Exception as e:
            bot.reply_to(message, f"<b>❌ 𝙀𝙧𝙧𝙤𝙧: {e}</b>", parse_mode="HTML")
            return
    elif target_msg.text:
        content_text = target_msg.text
    else:
        bot.reply_to(message, "<b>❌ 𝙉𝙤 𝙩𝙚𝙭𝙩 𝙛𝙤𝙪𝙣𝙙.</b>", parse_mode="HTML")
        return

    new_lines = [l.strip() for l in content_text.splitlines() if l.strip()]
    if not new_lines:
        bot.reply_to(message, "<b>❌ 𝙀𝙢𝙥𝙩𝙮 𝙡𝙞𝙣𝙚𝙨.</b>", parse_mode="HTML")
        return

    data["target_texts"] = new_lines
    save_data()
    bot.reply_to(message, f"<b>✅ 𝙏𝙚𝙭𝙩𝙨 𝙪𝙥𝙙𝙖𝙩𝙚𝙙 ({len(new_lines)} 𝙡𝙞𝙣𝙚𝙨).</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("tofan"))
def start_tofan(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not data["targets"]:
        bot.reply_to(message, "<b>⚠️ 𝙉𝙤 𝙩𝙖𝙧𝙜𝙚𝙩𝙨 𝙛𝙤𝙪𝙣𝙙.</b>", parse_mode="HTML")
        return

    parts = message.text.split()
    count = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 10
    delay = float(parts[2]) if len(parts) >= 3 and parts[2].replace(".", "", 1).isdigit() else 0.1

    chat_id = message.chat.id
    active_tofans[chat_id] = True
    emoji = data["current_emoji"]

    def tofan_worker():
        sent = 0
        while sent < count and active_tofans.get(chat_id, False):
            try:
                txt = random.choice(data["target_texts"])
                target_links = "".join([f"<a href='tg://user?id={tid}'>{emoji}</a>" for tid in data["targets"]])
                formatted_text = f"{txt}\n\n{target_links}"
                bot.send_message(chat_id, formatted_text, parse_mode="HTML")
                sent += 1
                time.sleep(delay if delay > 0 else 0.0001)
            except Exception:
                time.sleep(0.001)

    threading.Thread(target=tofan_worker, daemon=True).start()
    bot.reply_to(message, f"<b>🎯 𝙏𝙤𝙛𝙖𝙣 𝙨𝙩𝙖𝙧𝙩𝙚𝙙! 𝘾𝙤𝙪𝙣𝙩: {count} | 𝘿𝙚𝙡𝙖𝙮: {delay}𝙨</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "stoptofan")
def stop_tofan(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    active_tofans[message.chat.id] = False
    bot.reply_to(message, "<b>⛔ 𝙏𝙤𝙛𝙖𝙣 𝙨𝙩𝙤𝙥𝙥𝙚𝙙.</b>", parse_mode="HTML")


# ===================== ENEMY =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "enemy")
def add_enemy(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙪𝙨𝙚𝙧.</b>", parse_mode="HTML")
        return
    tid = message.reply_to_message.from_user.id
    if tid not in data["enemy_targets"]:
        data["enemy_targets"].append(tid)
        save_data()
    bot.reply_to(message, "<b>🧌 𝙀𝙣𝙚𝙢𝙮 𝙖𝙙𝙙𝙚𝙙.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "listenemy")
def list_enemy(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not data["enemy_targets"]:
        bot.reply_to(message, "<b>📂 𝙀𝙢𝙥𝙩𝙮.</b>", parse_mode="HTML")
        return
    bot.reply_to(message, "<b>🧌 𝙀𝙣𝙚𝙢𝙞𝙚𝙨:</b>\n" + "\n".join(map(str, data["enemy_targets"])), parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("textenemy"))
def text_enemy(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(message, "<b>💬 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚𝙨:</b>\n" + "\n".join([f"- {t}" for t in data["enemy_texts"]]), parse_mode="HTML")
        return
    data["enemy_texts"].append(text)
    save_data()
    bot.reply_to(message, "<b>✅ 𝙀𝙣𝙚𝙢𝙮 𝙩𝙚𝙭𝙩 𝙖𝙙𝙙𝙚𝙙.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "clearenemytexts")
def clear_enemy_texts(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    data["enemy_texts"] = []
    save_data()
    bot.reply_to(message, "<b>🧹 𝙀𝙣𝙚𝙢𝙮 𝙩𝙚𝙭𝙩𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "enemyremove")
def remove_enemy(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙪𝙨𝙚𝙧.</b>", parse_mode="HTML")
        return
    tid = message.reply_to_message.from_user.id
    if tid in data["enemy_targets"]:
        data["enemy_targets"].remove(tid)
        save_data()
        bot.reply_to(message, "<b>🗑️ 𝙀𝙣𝙚𝙢𝙮 𝙧𝙚𝙢𝙤𝙫𝙚𝙙.</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "<b>❌ 𝙉𝙤𝙩 𝙛𝙤𝙪𝙣𝙙.</b>", parse_mode="HTML")


# ===================== FRIEND =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "friend")
def add_friend(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙪𝙨𝙚𝙧.</b>", parse_mode="HTML")
        return
    tid = message.reply_to_message.from_user.id
    if tid not in data["friends"]:
        data["friends"].append(tid)
        save_data()
    bot.reply_to(message, "<b>💞 𝙁𝙧𝙞𝙚𝙣𝙙 𝙖𝙙𝙙𝙚𝙙.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "listfriend")
def list_friend(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not data["friends"]:
        bot.reply_to(message, "<b>📂 𝙀𝙢𝙥𝙩𝙮.</b>", parse_mode="HTML")
        return
    bot.reply_to(message, "<b>💞 𝙁𝙧𝙞𝙚𝙣𝙙𝙨:</b>\n" + "\n".join(map(str, data["friends"])), parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("textfriend"))
def text_friend(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(message, "<b>💬 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚𝙨:</b>\n" + "\n".join([f"- {t}" for t in data["friend_texts"]]), parse_mode="HTML")
        return
    data["friend_texts"].append(text)
    save_data()
    bot.reply_to(message, "<b>✅ 𝙁𝙧𝙞𝙚𝙣𝙙 𝙩𝙚𝙭𝙩 𝙖𝙙𝙙𝙚𝙙.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "clearfriendtexts")
def clear_friend_texts(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    data["friend_texts"] = []
    save_data()
    bot.reply_to(message, "<b>🧹 𝙁𝙧𝙞𝙚𝙣𝙙 𝙩𝙚𝙭𝙩𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "friendremove")
def remove_friend(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙪𝙨𝙚𝙧.</b>", parse_mode="HTML")
        return
    tid = message.reply_to_message.from_user.id
    if tid in data["friends"]:
        data["friends"].remove(tid)
        save_data()
        bot.reply_to(message, "<b>🗑️ 𝙁𝙧𝙞𝙚𝙣𝙙 𝙧𝙚𝙢𝙤𝙫𝙚𝙙.</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "<b>❌ 𝙉𝙤𝙩 𝙛𝙤𝙪𝙣𝙙.</b>", parse_mode="HTML")


# ===================== REACTION =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "listreaction")
def list_reaction(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    reactions = ["👍", "👎", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🙏", "👌", "🕊", "🤡", "🥱", "😍", "❤‍🔥", "💯", "🤣", "⚡", "🏆", "💔", "🤨", "💋", "🖕", "😈", "🤓", "👻", "👀", "✍", "🤗", "🗿"]
    bot.reply_to(message, f"<b>✍️ 𝙍𝙚𝙖𝙘𝙩𝙞𝙤𝙣𝙨:</b>\n" + " ".join(reactions) + f"\n<b>𝘾𝙪𝙧𝙧𝙚𝙣𝙩: {data['target_reaction']}</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower().startswith("addreaction"))
def add_reaction(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "<b>⚠️ 𝙐𝙨𝙖𝙜𝙚: addreaction [𝙚𝙢𝙤𝙟𝙞]</b>", parse_mode="HTML")
        return
    data["target_reaction"] = parts[1].strip()
    save_data()
    bot.reply_to(message, f"<b>✅ 𝙍𝙚𝙖𝙘𝙩𝙞𝙤𝙣 𝙨𝙚𝙩 𝙩𝙤: {data['target_reaction']}</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "addname")
def add_name_reaction(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙪𝙨𝙚𝙧.</b>", parse_mode="HTML")
        return
    tid = message.reply_to_message.from_user.id
    if tid not in data["reaction_users"]:
        data["reaction_users"].append(tid)
        save_data()
    bot.reply_to(message, "<b>✍️ 𝙐𝙨𝙚𝙧 𝙖𝙙𝙙𝙚𝙙 𝙛𝙤𝙧 𝙧𝙚𝙖𝙘𝙩𝙞𝙤𝙣.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "stopreaction")
def stop_reaction(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    data["reaction_users"] = []
    save_data()
    bot.reply_to(message, "<b>⛔ 𝙍𝙚𝙖𝙘𝙩𝙞𝙤𝙣𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙.</b>", parse_mode="HTML")


# ===================== OWNER =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() in ["addowner", "addowmer"])
def add_owner(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙪𝙨𝙚𝙧.</b>", parse_mode="HTML")
        return
    new_owner = message.reply_to_message.from_user.id
    if new_owner not in data["owners"]:
        data["owners"].append(new_owner)
        save_data()
        bot.reply_to(message, f"<b>👑 𝙊𝙬𝙣𝙚𝙧 𝙖𝙙𝙙𝙚𝙙: {new_owner}</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "<b>ℹ️ 𝘼𝙡𝙧𝙚𝙖𝙙𝙮 𝙖𝙣 𝙤𝙬𝙣𝙚𝙧.</b>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "listowner")
def list_owner(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    bot.reply_to(message, "<b>👨‍💻 𝙊𝙬𝙣𝙚𝙧𝙨:</b>\n" + "\n".join(map(str, data["owners"])), parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "ownerremove")
def remove_owner(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "<b>⚠️ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙤𝙬𝙣𝙚𝙧.</b>", parse_mode="HTML")
        return
    target_id = message.reply_to_message.from_user.id
    if target_id == OWNER_ID:
        bot.reply_to(message, "<b>❌ 𝘾𝙖𝙣𝙣𝙤𝙩 𝙧𝙚𝙢𝙤𝙫𝙚 𝙢𝙖𝙞𝙣 𝙢𝙖𝙨𝙩𝙚𝙧!</b>", parse_mode="HTML")
        return
    if target_id in data["owners"]:
        data["owners"].remove(target_id)
        save_data()
        bot.reply_to(message, "<b>🗑️ 𝙊𝙬𝙣𝙚𝙧 𝙧𝙚𝙢𝙤𝙫𝙚𝙙.</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "<b>❌ 𝙉𝙤𝙩 𝙞𝙣 𝙡𝙞𝙨𝙩.</b>", parse_mode="HTML")


# ===================== GENERAL =====================
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "stats")
def stats_cmd(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    text = (
        f"<b>📊 𝙎𝙏𝘼𝙏𝙎</b>\n"
        f"<b>👥 𝙊𝙬𝙣𝙚𝙧𝙨:</b> {len(data['owners'])}\n"
        f"<b>🎯 𝙏𝙖𝙧𝙜𝙚𝙩𝙨:</b> {len(data['targets'])}\n"
        f"<b>💞 𝙁𝙧𝙞𝙚𝙣𝙙𝙨:</b> {len(data['friends'])}\n"
        f"<b>🧌 𝙀𝙣𝙚𝙢𝙞𝙚𝙨:</b> {len(data['enemy_targets'])}\n"
        f"<b>✍️ 𝙍𝙚𝙖𝙘𝙩𝙞𝙤𝙣𝙨:</b> {len(data['reaction_users'])}\n"
        f"<b>📤 𝙎𝙥𝙖𝙢𝙨:</b> {len(data['spam_texts'])}"
    )
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() == "ping")
def ping_cmd(message):
    if not is_owner(message.from_user.id) or not data["bot_active"]:
        return
    start = time.time()
    sent = bot.reply_to(message, "<b>🌐 𝙋𝙞𝙣𝙜𝙞𝙣𝙜...</b>", parse_mode="HTML")
    latency = round((time.time() - start) * 1000, 2)
    bot.edit_message_text(
        f"🌐 𝙋𝙞𝙣𝙜 : <code>{latency}𝙢𝙨</code>",
        chat_id=sent.chat.id,
        message_id=sent.message_id,
        parse_mode="HTML",
    )


# ===================== UNIVERSAL TRACKER =====================
@bot.message_handler(
    func=lambda m: True,
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "sticker",
    ],
)
def universal_message_tracker(message):
    if not message.chat or not message.from_user:
        return

    sender_id = message.from_user.id
    me_id = bot.get_me().id

    if sender_id == me_id:
        return

    if not data["bot_active"]:
        return

    if sender_id in data["friends"] and data["friend_texts"]:
        try:
            bot.reply_to(message, random.choice(data["friend_texts"]))
        except Exception:
            pass

    if sender_id in data["enemy_targets"] and data["enemy_texts"]:
        try:
            bot.reply_to(message, random.choice(data["enemy_texts"]))
        except Exception:
            pass

    if sender_id in data["reaction_users"]:
        try:
            bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[types.ReactionTypeEmoji(emoji=data["target_reaction"])]
            )
        except Exception:
            pass


# ===================== FLASK WEB SERVER (FOR RENDER PORT) =====================
app = Flask(__name__)

@app.route('/')
def home():
    return "𝙁𝙊𝙉𝙀𝙓 𝘽𝙤𝙩 𝙞𝙨 𝙖𝙘𝙩𝙞𝙫𝙚 𝙖𝙣𝙙 𝙧𝙪𝙣𝙣𝙞𝙣𝙜!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# اجرای وب‌سرور در پس‌زمینه برای ماندگاری روی رندر
threading.Thread(target=run_web, daemon=True).start()

print("𝙁𝙊𝙉𝙀𝙓 𝙗𝙤𝙩 𝙞𝙨 𝙧𝙪𝙣𝙣𝙞𝙣𝙜 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮...")
bot.infinity_polling(skip_pending=True)
