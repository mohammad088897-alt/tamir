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
OWNER_ID = 7684105339  # Your Telegram ID

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "fonex_data.json"

# Default Database Structure
data = {
    "owners": [OWNER_ID],
    "spam_texts": [],
    "spam_delay": 0.1,
    "target_texts": [
        "You are absolute trash, nobody likes you.",
        "Keep talking, your stupidity is entertaining.",
    ],
    "targets": [],  # List of user IDs
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
ping_start_time = time.time()


HELP_TEXT = """
<b>FONEX HELP 🔥</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Spam :</b> 📤
/addspam
/delspam [number]
/listspam
/settimespam [seconds]
/start [count] [delay]

<b>Target :</b> 🎯
/targed
/deltarged [number یا Reply]
/listtarged
/setemoji [emoji]
/adtext
/tofan [count] [delay]
/stoptofan

<b>Enemy :</b> 🧌
/enemy
/listenemy
/textenemy [text]
/enemyremove
/clear_enemy_texts

<b>Friend :</b> 💞
/friend
/listfriend
/textfriend [text]
/friendremove
/clear_friend_texts

<b>Reaction :</b> ✍
/listReaction
/addReaction [emoji]
/addname
/stopReaction

<b>Fun :</b> 😁 (Available for everyone)
/fon
/fall
/jok
/fack (Reply to message - Owner only)
/hak (Reply to user - Owner only)
/matrix
/radar

<b>Owner :</b> 👨‍💻
/addowmer
/listowner
/ownerremove

<b>General :</b> 📊
/stats
/ping
"""


@bot.message_handler(
    func=lambda m: m.text is not None
    and m.text.strip().lower() in [".help", "/help", "/panel", "help"]
)
def show_panel(message):
    if not is_owner(message.from_user.id):
        return
    bot.send_message(
        message.chat.id, HELP_TEXT, parse_mode="HTML"
    )


# ===================== SPAM =====================
@bot.message_handler(commands=["addspam"])
def add_spam(message):
    if not is_owner(message.from_user.id):
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(message, "⚠️ Error: Text required.")
        return
    data["spam_texts"].append(text)
    save_data()
    bot.reply_to(message, f"✅ Added. Total: {len(data['spam_texts'])}")


@bot.message_handler(commands=["delspam"])
def del_spam(message):
    if not is_owner(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "⚠️ Usage: /delspam [number]")
        return
    idx = int(parts[1]) - 1
    if 0 <= idx < len(data["spam_texts"]):
        data["spam_texts"].pop(idx)
        save_data()
        bot.reply_to(message, "🗑️ Deleted.")
    else:
        bot.reply_to(message, "❌ Invalid index.")


@bot.message_handler(commands=["listspam"])
def list_spam(message):
    if not is_owner(message.from_user.id):
        return
    if not data["spam_texts"]:
        bot.reply_to(message, "📂 Empty.")
        return
    text = "📋 <b>Spam List:</b>\n" + "\n".join([f"{i}. {t}" for i, t in enumerate(data["spam_texts"], 1)])
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(commands=["settimespam"])
def set_time_spam(message):
    if not is_owner(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "⚠️ Usage: /settimespam [seconds]")
        return
    try:
        data["spam_delay"] = float(parts[1])
        save_data()
        bot.reply_to(message, f"⏱️ Delay set to {data['spam_delay']}s.")
    except ValueError:
        bot.reply_to(message, "❌ Invalid number.")


@bot.message_handler(commands=["start"])
def start_spam(message):
    if not is_owner(message.from_user.id):
        return
    if not data["spam_texts"]:
        bot.reply_to(message, "⚠️ No spam texts.")
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
    bot.reply_to(message, f"🚀 Started! Count: {count} | Delay: {delay}s")


@bot.message_handler(commands=["stopspam", "stop"])
def stop_spam(message):
    if not is_owner(message.from_user.id):
        return
    chat_id = message.chat.id
    active_spams[chat_id] = False
    active_tofans[chat_id] = False
    bot.reply_to(message, "⛔ Stopped.")


# ===================== TARGET =====================
@bot.message_handler(commands=["targed", "target"])
def add_target(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ Reply to a user.")
        return
    tid = message.reply_to_message.from_user.id
    if tid not in data["targets"]:
        data["targets"].append(tid)
        save_data()
    bot.reply_to(message, "🎯 Target added.")


@bot.message_handler(commands=["deltarged"])
def del_target(message):
    if not is_owner(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) == 2 and parts[1].isdigit():
        idx = int(parts[1]) - 1
        if 0 <= idx < len(data["targets"]):
            removed_tid = data["targets"].pop(idx)
            save_data()
            bot.reply_to(message, f"🗑️ Target removed successfully (ID: {removed_tid}).")
        else:
            bot.reply_to(message, "❌ Invalid index number.")
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        tid = message.reply_to_message.from_user.id
        if tid in data["targets"]:
            data["targets"].remove(tid)
            save_data()
            bot.reply_to(message, "🗑️ Target removed successfully.")
        else:
            bot.reply_to(message, "❌ This user is not in the target list.")
        return

    bot.reply_to(message, "⚠️ Usage: /deltarged [number] OR reply to a user.")


@bot.message_handler(commands=["listtarged"])
def list_target(message):
    if not is_owner(message.from_user.id):
        return
    if not data["targets"]:
        bot.reply_to(message, "📂 Target list is empty.")
        return
    
    emoji = data["current_emoji"]
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    list_str = f"🎯 <b>Target List ({len(data['targets'])} users):</b>\n"
    for i, tid in enumerate(data["targets"], 1):
        list_str += f"<b>{i}.</b> ID: <code>{tid}</code>\n"
        button_text = f"{emoji} Profile {i} ({tid})"
        markup.add(types.InlineKeyboardButton(button_text, url=f"tg://user?id={tid}"))
        
    bot.reply_to(message, list_str, parse_mode="HTML", reply_markup=markup)


@bot.message_handler(commands=["setemoji"])
def set_emoji(message):
    if not is_owner(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Usage: /setemoji [emoji]")
        return
    data["current_emoji"] = parts[1].strip()
    save_data()
    bot.reply_to(message, f"✅ Emoji updated: {data['current_emoji']}")


@bot.message_handler(commands=["adtext"])
def ad_text(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to text or file.")
        return

    target_msg = message.reply_to_message
    content_text = ""
    if target_msg.document:
        try:
            file_info = bot.get_file(target_msg.document.file_id)
            content_text = bot.download_file(file_info.file_path).decode("utf-8")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {e}")
            return
    elif target_msg.text:
        content_text = target_msg.text
    else:
        bot.reply_to(message, "❌ No text found.")
        return

    new_lines = [l.strip() for l in content_text.splitlines() if l.strip()]
    if not new_lines:
        bot.reply_to(message, "❌ Empty lines.")
        return

    data["target_texts"] = new_lines
    save_data()
    bot.reply_to(message, f"✅ Texts updated ({len(new_lines)} lines).")


@bot.message_handler(commands=["tofan"])
def start_tofan(message):
    if not is_owner(message.from_user.id):
        return
    if not data["targets"]:
        bot.reply_to(message, "⚠️ No targets found. Please add targets first.")
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
    bot.reply_to(message, f"🎯 Tofan started! Count: {count} | Delay: {delay}s")


@bot.message_handler(commands=["stoptofan"])
def stop_tofan(message):
    if not is_owner(message.from_user.id):
        return
    active_tofans[message.chat.id] = False
    bot.reply_to(message, "⛔ Tofan stopped.")


# ===================== ENEMY =====================
@bot.message_handler(commands=["enemy"])
def add_enemy(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ Reply to user.")
        return
    tid = message.reply_to_message.from_user.id
    if tid not in data["enemy_targets"]:
        data["enemy_targets"].append(tid)
        save_data()
    bot.reply_to(message, "🧌 Enemy added.")


@bot.message_handler(commands=["listenemy"])
def list_enemy(message):
    if not is_owner(message.from_user.id):
        return
    if not data["enemy_targets"]:
        bot.reply_to(message, "📂 Empty.")
        return
    bot.reply_to(message, "🧌 <b>Enemies:</b>\n" + "\n".join(map(str, data["enemy_targets"])), parse_mode="HTML")


@bot.message_handler(commands=["textenemy"])
def text_enemy(message):
    if not is_owner(message.from_user.id):
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(message, "💬 <b>Responses:</b>\n" + "\n".join([f"- {t}" for t in data["enemy_texts"]]), parse_mode="HTML")
        return
    data["enemy_texts"].append(text)
    save_data()
    bot.reply_to(message, "✅ Enemy text added.")


@bot.message_handler(commands=["clear_enemy_texts"])
def clear_enemy_texts(message):
    if not is_owner(message.from_user.id):
        return
    data["enemy_texts"] = []
    save_data()
    bot.reply_to(message, "🧹 Enemy response texts cleared.")


@bot.message_handler(commands=["enemyremove"])
def remove_enemy(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ Reply to user.")
        return
    tid = message.reply_to_message.from_user.id
    if tid in data["enemy_targets"]:
        data["enemy_targets"].remove(tid)
        save_data()
        bot.reply_to(message, "🗑️ Enemy removed.")
    else:
        bot.reply_to(message, "❌ Not found.")


# ===================== FRIEND =====================
@bot.message_handler(commands=["friend"])
def add_friend(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ Reply to user.")
        return
    tid = message.reply_to_message.from_user.id
    if tid not in data["friends"]:
        data["friends"].append(tid)
        save_data()
    bot.reply_to(message, "💞 Friend added.")


@bot.message_handler(commands=["listfriend"])
def list_friend(message):
    if not is_owner(message.from_user.id):
        return
    if not data["friends"]:
        bot.reply_to(message, "📂 Empty.")
        return
    bot.reply_to(message, "💞 <b>Friends:</b>\n" + "\n".join(map(str, data["friends"])), parse_mode="HTML")


@bot.message_handler(commands=["textfriend"])
def text_friend(message):
    if not is_owner(message.from_user.id):
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(message, "💬 <b>Responses:</b>\n" + "\n".join([f"- {t}" for t in data["friend_texts"]]), parse_mode="HTML")
        return
    data["friend_texts"].append(text)
    save_data()
    bot.reply_to(message, "✅ Friend text added.")


@bot.message_handler(commands=["clear_friend_texts"])
def clear_friend_texts(message):
    if not is_owner(message.from_user.id):
        return
    data["friend_texts"] = []
    save_data()
    bot.reply_to(message, "🧹 Friend response texts cleared.")


@bot.message_handler(commands=["friendremove"])
def remove_friend(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ Reply to user.")
        return
    tid = message.reply_to_message.from_user.id
    if tid in data["friends"]:
        data["friends"].remove(tid)
        save_data()
        bot.reply_to(message, "🗑️ Friend removed.")
    else:
        bot.reply_to(message, "❌ Not found.")


# ===================== REACTION =====================
@bot.message_handler(commands=["listReaction"])
def list_reaction(message):
    if not is_owner(message.from_user.id):
        return
    reactions = ["👍", "👎", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🙏", "👌", "🕊", "🤡", "🥱", "😍", "❤‍🔥", "💯", "🤣", "⚡", "🏆", "💔", "🤨", "💋", "🖕", "😈", "🤓", "👻", "👀", "✍", "🤗", "🗿"]
    bot.reply_to(message, f"✍️ <b>Reactions:</b>\n" + " ".join(reactions) + f"\nCurrent: {data['target_reaction']}", parse_mode="HTML")


@bot.message_handler(commands=["addReaction"])
def add_reaction(message):
    if not is_owner(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Usage: /addReaction [emoji]")
        return
    data["target_reaction"] = parts[1].strip()
    save_data()
    bot.reply_to(message, f"✅ Reaction set to: {data['target_reaction']}")


@bot.message_handler(commands=["addname"])
def add_name_reaction(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ Reply to user.")
        return
    tid = message.reply_to_message.from_user.id
    if tid not in data["reaction_users"]:
        data["reaction_users"].append(tid)
        save_data()
    bot.reply_to(message, "✍️ User added for auto-reaction.")


@bot.message_handler(commands=["stopReaction"])
def stop_reaction(message):
    if not is_owner(message.from_user.id):
        return
    data["reaction_users"] = []
    save_data()
    bot.reply_to(message, "⛔ Reactions cleared.")


# ===================== FUN SECTION =====================
FAILS = [
    "🔮 فال حافظ: ای دل غمدیده حالم به شود دل بد مکن... روزهای روشنی در پیش داری.",
    "🔮 فال حافظ: مرغ سحر آوخ که سرود شب تار است... صبر کن که صبوری کلید پیروزی است.",
    "🔮 فال حافظ: دوش ازسفیده‌صبح هدایای حق رسید... به زودی خبرهای بسیار عالی می‌شنوی.",
    "🔮 فال حافظ: حافظ ار بویی شنیدی ز وفا... به مراد دل خود می‌رسی، فقط ناامید نباش."
]

JOKES = [
    "😂 یارو میره هندوانه فروشی، میگه این هندوانه‌ها شیرینه؟ یارو میگه داداش اینا شیرین نیست، عسله! یارو میگه پس دو تا نون بربری هم بده روش بخوریم!",
    "😂 غضنفر میره دکتر، دکتر میگه روزی دو تا قرص بخور. غضنفر میگه آقای دکتر من روزی یکیشم به زور قورت میدم!",
    "😂 طرف میگه خدایا شکرت که کورم نکردی تا قیافه این مردم رو ببینم! یکی میگه داداش الان که بینایی، چه فرقی کرد؟",
    "😂 معلم: چرا مشق‌هات رو ننوشتی؟ دانش‌آموز: آقا مدادم گم شده بود، تو تاریکی نتونستم پیداش کنم!"
]

@bot.message_handler(commands=["fall"])
def fun_fall(message):
    bot.reply_to(message, random.choice(FAILS))


@bot.message_handler(commands=["jok"])
def fun_jok(message):
    bot.reply_to(message, random.choice(JOKES))


@bot.message_handler(commands=["fack"])
def fun_fack(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to a message.")
        return
    
    target_msg = message.reply_to_message
    
    for i in range(10, 0, -1):
        try:
            bot.edit_message_text(f"⏳ Counting down: {i}", chat_id=target_msg.chat.id, message_id=target_msg.message_id)
            time.sleep(1)
        except Exception:
            pass

    quote_art = (
        "⠀⠀⠀⠀⠀⠀⠀⣠⣾⣷⣄\n"
        "⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿\n"
        "⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿\n"
        "⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿\n"
        "⠀⠀⢀⣴⣿⣦⡀⣿⣿⣿⣿⢀⣴⣿⣦⡀\n"
        "⠀⠀⢸⣿⣿⣿⡇⣿⣿⣿⣿⢸⣿⣿⣿⡇\n"
        "⠀⠀⢸⣿⣿⣿⡇⠿⠿⠿⠿⢸⣿⣿⣿⡇\n"
        "⢿⣿⣿⣿⣿⣿⡇⣤⣤⣤⣤⢸⣿⣿⣿⡇\n"
        "⠘⣿⣿⣿⣿⣿⣧⣿⣿⣿⣿⣼⣿⣿⣿⡇\n"
        "⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇\n"
        "⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇\n"
        "⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇\n"
        "⠀⠀⠈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠁"
    )
    
    try:
        bot.edit_message_text(f"{quote_art}", chat_id=target_msg.chat.id, message_id=target_msg.message_id)
    except Exception:
        pass


@bot.message_handler(commands=["hak", "hacker"])
def prank_hacker(message):
    if not is_owner(message.from_user.id):
        return
    
    target_name = "ILIYA"
    if message.reply_to_message and message.reply_to_message.from_user:
        target_name = message.reply_to_message.from_user.first_name

    msg = bot.reply_to(message, f"💻 <b>Initializing hack protocol on {target_name}...</b>\n<code>[▒▒▒▒▒▒▒▒▒▒] 0%</code>", parse_mode="HTML")
    
    stages = [
        (f"💻 <b>Bypassing firewall for {target_name}...</b>\n<code>[███▒▒▒▒▒▒▒] 30%</code>", 0.3),
        (f"💻 <b>Extracting IP address & data...</b>\n<code>[██████▒▒▒▒] 60%</code>", 0.3),
        (f"💻 <b>Accessing files and gallery...</b>\n<code>[██████████] 100%</code>", 0.3),
    ]
    
    for text, delay in stages:
        time.sleep(delay)
        try:
            bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode="HTML")
        except Exception:
            pass

    quoted_result = (
        f"☠️💀 ACCESS GRANTED 💀☠️\n"
        f"🎯 Target: {target_name}\n"
        f"[██████████] 100%\n"
        f"✔ Firewall ........ BYPASSED\n"
        f"✔ Contacts ........ COPIED\n"
        f"✔ Messages ........ COPIED\n"
        f"✔ Gallery ......... COPIED\n"
        f"✔ Passwords ....... EXTRACTED"
    )
    
    final_output = f"<blockquote>{quoted_result}</blockquote>\n🔴 Hacked By FONEX 🕷"
    
    try:
        bot.edit_message_text(final_output, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode="HTML")
    except Exception:
        pass


@bot.message_handler(commands=["matrix"])
def prank_matrix(message):
    bot.reply_to(message, "🟢 <code>SYSTEM OVERRIDE: █▀█ █▄█ █ █</code>", parse_mode="HTML")


@bot.message_handler(commands=["radar"])
def prank_radar(message):
    bot.reply_to(message, "🎯 <b>TARGET LOCATED!</b>\n📍 Distance: <code>3.5 km away! 🚨</code>", parse_mode="HTML")


@bot.message_handler(commands=["fon"])
def fun_entertainment(message):
    bot.reply_to(message, "⚡ <b>FONEX Fun Zone Active!</b> Try /fall, /jok, /hak, /fack, /matrix, /radar", parse_mode="HTML")


# ===================== OWNER =====================
@bot.message_handler(commands=["addowmer", "addowner"])
def add_owner(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ Reply to user.")
        return
    new_owner = message.reply_to_message.from_user.id
    if new_owner not in data["owners"]:
        data["owners"].append(new_owner)
        save_data()
        bot.reply_to(message, f"👑 Owner added: {new_owner}")
    else:
        bot.reply_to(message, "ℹ️ Already an owner.")


@bot.message_handler(commands=["listowner"])
def list_owner(message):
    if not is_owner(message.from_user.id):
        return
    bot.reply_to(message, "👨‍💻 <b>Owners:</b>\n" + "\n".join(map(str, data["owners"])), parse_mode="HTML")


@bot.message_handler(commands=["ownerremove"])
def remove_owner(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ Reply to owner.")
        return
    target_id = message.reply_to_message.from_user.id
    if target_id == OWNER_ID:
        bot.reply_to(message, "❌ Cannot remove main master!")
        return
    if target_id in data["owners"]:
        data["owners"].remove(target_id)
        save_data()
        bot.reply_to(message, "🗑️ Owner removed.")
    else:
        bot.reply_to(message, "❌ Not in list.")


# ===================== GENERAL =====================
@bot.message_handler(commands=["stats"])
def stats_cmd(message):
    if not is_owner(message.from_user.id):
        return
    text = (
        f"📊 <b>FONEX STATS</b>\n"
        f"👥 Owners: {len(data['owners'])}\n"
        f"🎯 Targets: {len(data['targets'])}\n"
        f"💞 Friends: {len(data['friends'])}\n"
        f"🧌 Enemies: {len(data['enemy_targets'])}\n"
        f"✍️ Reactions: {len(data['reaction_users'])}\n"
        f"📤 Spams: {len(data['spam_texts'])}"
    )
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(commands=["ping"])
def ping_cmd(message):
    if not is_owner(message.from_user.id):
        return
    start = time.time()
    sent = bot.reply_to(message, "🏓 Pinging...")
    latency = round((time.time() - start) * 1000, 2)
    uptime = round(time.time() - ping_start_time, 2)
    bot.edit_message_text(
        f"🏓 Pong! Latency: <code>{latency}ms</code>\n⏱️ Uptime: <code>{uptime}s</code>",
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
    text = message.text or ""

    if sender_id == me_id:
        return

    if not is_owner(sender_id) and text.startswith("/"):
        attempts = unauthorized_attempts.get(sender_id, 0)
        if attempts < 3:
            unauthorized_attempts[sender_id] = attempts + 1
            try:
                bot.reply_to(message, "You are not an owner!")
            except Exception:
                pass
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
    return "FONEX Bot is active and running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# اجرای وب‌سرور در پس‌زمینه برای ماندگاری روی رندر
threading.Thread(target=run_web, daemon=True).start()

print("FONEX bot is running successfully...")
bot.infinity_polling(skip_pending=True)
