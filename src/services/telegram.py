# coding: utf-8

import typing as ty

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from core import settings


class SendMessageService:
    """
    Just another service for sending some messages.
    """

    def __init__(
        self,
        body: str,
        chat_id: ty.Optional[int] = settings.CHAT_ID,
        button: ty.Dict[str, str] = None,
    ) -> None:
        self.body = body
        self.chat_id = chat_id
        self.button = button

    def __call__(self) -> int:
        self.bot = telebot.TeleBot(settings.API_TELEGRAM, parse_mode=None)
        return self.send_message()

    @staticmethod
    def get_button_markup(text: str, callback_data: str) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        return markup

    def send_message(self) -> int:
        payload = dict(
            chat_id=self.chat_id,
            text=str(self.body),
            parse_mode="HTML",
        )

        if self.button is not None and isinstance(self.button, dict):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(**self.button))
            payload["reply_markup"] = markup

        obj = self.bot.send_message(**payload)
        return obj.id
