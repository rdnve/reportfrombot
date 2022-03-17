# coding: utf-8

from typing import Optional

import telebot

from core import settings as S


class SendMessageService:
    """
    Just another service for sending some messages.
    """

    def __init__(self, body: str, chat_id: Optional[int] = S.CHAT_ID):
        self.body = body
        self.chat_id = chat_id

    def __call__(self) -> int:
        self.bot = telebot.TeleBot(S.API_TELEGRAM, parse_mode=None)
        return self.send_message()

    def send_message(self) -> int:
        obj = self.bot.send_message(
            self.chat_id,
            str(self.body),
            parse_mode="HTML",
        )
        return obj.id
