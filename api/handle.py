from .auth import is_authorized
from .command import execute_command
from .context import ChatManager
from .telegram import Update, send_message
from .printLog import send_log, send_image_log
from .config import *
from .gemini import generate_content, generate_text_with_image, ChatConversation

chat_manager = ChatManager()

def handle_message(update_data):
    update = Update(update_data)

    # Log the incoming event
    if update.is_group:
        log = f"{event_received}\n@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`\n{the_content_sent_is}\n{update.text}\n```json\n{update_data}```"
    else:
        log = f"{event_received}\n@{update.user_name} id:`{update.from_id}`\n{the_content_sent_is}\n{update.text}\n```json\n{update_data}```"
    send_log(log)

    # Check if the user is authorized to interact with the bot
    authorized = is_authorized(update.is_group, update.from_id, update.user_name, update.chat_id, update.group_name)

    if update.type == "command":
        response_text = execute_command(update.from_id, update.text, update.from_type, update.chat_id)
        if response_text != "":
            send_message(update.chat_id, response_text)
            if update.is_group:
                log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}"
            else:
                log = f"@{update.user_name} id:`{update.from_id}`{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}"
            send_log(log)

    elif not authorized:
        if update.is_group:
            send_message(update.chat_id, f"{group_no_permission_info}\nID:`{update.chat_id}`")
            log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`{no_rights_to_use},{the_content_sent_is}\n{update.text}"
        else:
            send_message(update.from_id, f"{user_no_permission_info}\nID:`{update.from_id}`")
            log = f"@{update.user_name} id:`{update.from_id}`{no_rights_to_use},{the_content_sent_is}\n{update.text}"
        send_log(log)
        return

    elif update.type == "text":
        if update.is_group and GROUP_MODE == "2":
            history_id = update.from_id
        else:
            history_id = update.chat_id
        chat = chat_manager.get_chat(history_id)
        response_text = chat.send_message(update.text)
        extra_text = f"\n\n{prompt_new_info}" if chat.history_length >= prompt_new_threshold * 2 else ""
        response_text = f"{response_text}{extra_text}"
        send_message(update.chat_id, response_text)
        dialogueLogarithm = int(chat.history_length / 2)
        if update.is_group:
            log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}\n{the_logarithm_of_historical_conversations_is}{dialogueLogarithm}"
        else:
            log = f"@{update.user_name} id:`{update.from_id}`{the_content_sent_is}\n{update.text}\n{the_reply_content_is}\n{response_text}\n{the_logarithm_of_historical_conversations_is}{dialogueLogarithm}"
        send_log(log)

    elif update.type == "photo":
        if update.is_group and GROUP_MODE == "2":
            history_id = update.from_id
        else:
            history_id = update.chat_id
        chat = chat_manager.get_chat(history_id)
        response_text = generate_text_with_image(update.photo_caption, update.photo_bytes)
        print(f"update.message_id {update.message_id}")
        send_message(update.chat_id, response_text, reply_to_message_id=update.message_id)

        photo_url = chat.tel_photo_url()
        imageID = update.file_id
        if update.is_group:
            log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`[photo]({photo_url}),{the_accompanying_message_is}\n{update.photo_caption}\n{the_reply_content_is}\n{response_text}"
        else:
            log = f"@{update.user_name} id:`{update.from_id}`[photo]({photo_url}),{the_accompanying_message_is}\n{update.photo_caption}\n{the_reply_content_is}\n{response_text}"
        send_image_log("", imageID)
        send_log(log)

    else:
        send_message(update.chat_id, f"{unable_to_recognize_content_sent}\n\n/help")
        if update.is_group:
            log = f"@{update.user_name} id:`{update.from_id}` {group} @{update.group_name} id:`{update.chat_id}`{send_unrecognized_content}"
        else:
            log = f"@{update.user_name} id:`{update.from_id}`{send_unrecognized_content}"
        send_log(log)