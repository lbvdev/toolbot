import telebot
from telebot.apihelper import ApiTelegramException

from services.env import get_env
from services.logger import error_log

bot = telebot.TeleBot(get_env("TELEGRAM_BOT_TOKEN"))


def smart_reply(
    message, reply_message: str, parse_mode: str = "HTML", chunk_size: int = 3500
):
    if len(reply_message) <= chunk_size:
        return bot.reply_to(message, reply_message, parse_mode=parse_mode)

    parts = []
    cur = ""
    for line in reply_message.splitlines(keepends=True):
        if len(cur) + len(line) > chunk_size and cur:
            parts.append(cur)
            cur = line
        else:
            cur += line
    if cur:
        parts.append(cur)

    sent = []
    for i, part in enumerate(parts):
        msg = bot.send_message(
            chat_id=message.chat.id,
            text=part,
            parse_mode=parse_mode,
            reply_to_message_id=message.message_id if i == 0 else None,
        )
        sent.append(msg)
    return sent


@bot.message_handler(commands=["emo"])
def handle_emo(message):
    try:
        src = message.reply_to_message or message

        custom_ids = [
            e.custom_emoji_id for e in (src.entities or []) if e.type == "custom_emoji"
        ]

        if not custom_ids:
            bot.reply_to(message, "че, не нашел кастомных эмодзи")
            return

        stickers = bot.get_custom_emoji_stickers(custom_ids)
        emoji_by_id = {st.custom_emoji_id: (st.emoji or "🙂") for st in stickers}
        emoji_preview_message = [
            f'<tg-emoji emoji-id="{emoji_id}">{emoji_by_id.get(emoji_id, "🙂")}</tg-emoji><code> {emoji_id}</code>'
            for emoji_id in custom_ids
        ]
        emoji_tag_message = [
            f'<code>&lt;tg-emoji emoji-id="{emoji_id}"&gt;{emoji_by_id.get(emoji_id, "🙂")}&lt;/tg-emoji&gt;</code>'
            for emoji_id in custom_ids
        ]
        reply_message = "\n".join(emoji_preview_message + [""] + emoji_tag_message)
        smart_reply(message, reply_message, parse_mode="HTML")

    except ApiTelegramException as e:
        error_log(e, "Telegram API error in /emo")


@bot.message_handler(commands=["emopack"])
def handle_emopack(message):
    try:
        src = message.reply_to_message or message
        custom_ids = [
            e.custom_emoji_id for e in (src.entities or []) if e.type == "custom_emoji"
        ]
        if not custom_ids:
            bot.reply_to(message, "че, не нашел кастомных эмодзи")
            return

        stickers = bot.get_custom_emoji_stickers(custom_ids)
        set_names = sorted({s.set_name for s in stickers if s.set_name})
        if not set_names:
            bot.reply_to(message, "че, не нашел наборов")
            return

        blocks = []
        for set_name in set_names:
            st_set = bot.get_sticker_set(set_name)
            emoji_items = [
                (st.custom_emoji_id, st.emoji or "💩")
                for st in st_set.stickers
                if st.custom_emoji_id
            ]
            if not emoji_items:
                continue

            blocks.append(
                f'\n<a href="https://t.me/addemoji/{set_name}"><b>{set_name}</b></a>\n'
            )
            blocks.extend(
                f'<tg-emoji emoji-id="{emoji_id}">{emoji_char}</tg-emoji><code> {emoji_id}</code>'
                for emoji_id, emoji_char in emoji_items
            )
            blocks.append("")
            blocks.extend(
                f'<tg-emoji emoji-id="{emoji_id}">{emoji_char}</tg-emoji> <code>&lt;tg-emoji emoji-id="{emoji_id}"&gt;{emoji_char}&lt;/tg-emoji&gt;</code>'
                for emoji_id, emoji_char in emoji_items
            )
            blocks.append("")

        if not blocks:
            bot.reply_to(message, "че, не нашел кастомных эмодзи в наборах")
            return

        reply_message = "\n".join(blocks)
        smart_reply(message, reply_message, parse_mode="HTML")

    except ApiTelegramException as e:
        error_log(e, "Telegram API error in /emopack")


def run_polling():
    bot.polling(none_stop=True)
