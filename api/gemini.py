from io import BytesIO

import google.generativeai as genai
import PIL.Image

from .config import GOOGLE_API_KEY, generation_config, safety_settings, gemini_err_info, new_chat_info

genai.configure(api_key=GOOGLE_API_KEY[0])

model_usual = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings)

model_vision = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings)


def list_models() -> None:
    """list all models"""
    for m in genai.list_models():
        print(m)
        if "generateContent" in m.supported_generation_methods:
            print(m.name)


""" This function is deprecated """


def generate_content(prompt: str) -> str:
    """generate text from prompt"""
    try:
        response = model_usual.generate_content(prompt)
        result = response.text
    except Exception as e:
        result = f"{gemini_err_info}\n{repr(e)}"
    return result


def generate_text_with_image(prompt: str, image_bytes: BytesIO) -> str:
    """generate text from prompt and image"""
    img = PIL.Image.open(image_bytes)
    try:
        response = model_vision.generate_content([prompt, img])
        result = response.text
    except Exception as e:
        result = f"{gemini_err_info}\n{repr(e)}"
    return result


class ChatConversation:
    """
    Manages a conversation that can handle both text and images.
    """

    def __init__(self) -> None:
        self.chat = model_usual.start_chat(history=[])

    def send_message(self, prompt: str, image: PIL.Image = None) -> str:
        """Send a message which could be text or text with an image."""
        if prompt.startswith("/new"):
            self.__init__()
            return new_chat_info

        try:
            if image:
                # Send both the image and the prompt
                response = self.chat.send_message([image, prompt])
            else:
                # Send only the prompt as text
                response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"{gemini_err_info}\n{repr(e)}"

    @property
    def history(self):
        """Returns the conversation history."""
        return self.chat.history

    @property
    def history_length(self):
        """Returns the length of the conversation history."""
        return len(self.chat.history)

if __name__ == "__main__":
    print(list_models())
