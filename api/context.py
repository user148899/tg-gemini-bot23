"""
The class ChatManager manages all users and their conversations in the
form of a dictionary.

Each user has a ChatConversation instance, which may include multiple
previous conversations of the user (provided by the Google Gemini API).

The class ImageChatManager is rather simple, as the images in Gemini Pro
do not have a contextual environment. This class performs some tasks
such as obtaining photos to addresses and so on.
"""
from io import BytesIO
from typing import Dict

import requests

from .config import BOT_TOKEN
from .gemini import ChatConversation, generate_text_with_image


class ChatManager:
    """setting up a basic conversation storage manager"""

    def __init__(self):
        self.chats: Dict[int, ChatConversation] = {}

    def _new_chat(self, history_id: int) -> ChatConversation:
        chat = ChatConversation()
        self.chats[history_id] = chat
        return chat

    def get_chat(self, history_id: int) -> ChatConversation:
        if self.chats.get(history_id) is None:
            return self._new_chat(history_id)
        return self.chats[history_id]

