"""
All the chat that comes through the Telegram bot gets passed to the
handle_message function. This function checks out if the user has the
green light to chat with the bot. Once that's sorted, it figures out if
the user sent words or an image and deals with it accordingly.

For text messages, it fires up the ChatManager class that keeps track of
the back-and-forth with that user.

As for images, in Gemini pro, they're context-free, so you can handle
them pretty straight-up without much fuss.
"""

from .auth import is_authorized
from .command import excute_command
from .context import ChatManager
from .telegram import Update, send_message
from .printLog import send_log,send_image_log
from .config import *

chat_manager = ChatManager()


def handle_message(update_data):
    update = Update(update_data)

    if not is_authorized(update.is_group, update.from_id, update.user_name, update.chat_id, update.group_name):
        permission_info = group_no_permission_info if update.is_group else user_no_permission_info
        send_message(update.chat_id, f"{permission_info}\nID:`{update.chat_id if update.is_group else update.from_id}`")
        return

    if update.type == "command":
        response_text = excute_command(update.from_id, update.text, update.from_type, update.chat_id)
        if response_text:
            send_message(update.chat_id, response_text)
    else:
        history_id = update.from_id if update.is_group and GROUP_MODE == "2" else update.chat_id
        chat = chat_manager.get_chat(history_id)

        if update.type == "photo":
            # Get the image bytes from the file ID
            photo_url = f"{TELEGRAM_API}/getFile?file_id={update.file_id}"
            file_path = requests.get(photo_url).json()['result']['file_path']
            full_file_url = f"{TELEGRAM_API}/file/bot{BOT_TOKEN}/{file_path}"
            image_bytes = BytesIO(requests.get(full_file_url).content)
            image = PIL.Image.open(image_bytes)

            response_text = chat.send_message(update.photo_caption, image)
            send_imageMessage(update.chat_id, response_text, update.file_id)
        elif update.type == "text":
            response_text = chat.send_message(update.text)
            send_message(update.chat_id, response_text)

        dialogue_logarithm = int(chat.history_length / 2)
        extra_info = f"\n\n{prompt_new_info}" if chat.history_length >= prompt_new_threshold * 2 else ""
        log = (f"@{update.user_name} id:`{update.from_id}`"
               f"{group if update.is_group else ''} @{update.group_name if update.is_group else ''} id:`{update.chat_id}`"
               f"{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}{extra_info}"
               f"\n{the_logarithm_of_historical_conversations_is}{dialogue_logarithm}")
        send_log(log)