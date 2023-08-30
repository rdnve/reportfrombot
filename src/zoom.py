import typing as ty

import argparse
import logging
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message

from core import settings

logger = logging.getLogger(__name__)


class NotifyService:

    FILENAME: str = "result.txt"

    def __init__(self, token: str, chat_id: str, zoom_url: str) -> None:
        self.bot: TeleBot = TeleBot(token=token, parse_mode="HTML")
        self.chat_id: str = chat_id
        self.zoom_url: str = zoom_url

    def send_message(self) -> int:
        users: ty.List[str] = list()

        for item in self.bot.get_chat_administrators(self.chat_id):
            if item.user.username == self.bot.user.username:
                continue

            if item.user.username:
                users.append(f"@{item.user.username}")
            else:
                users.append(
                    f'<a href="tg://user?id={item.user.id}">{item.user.first_name}</a>'
                )

        msg: Message = self.bot.send_message(
            chat_id=self.chat_id,
            text=f"{self.zoom_url}\n\n{', '.join(users)}.",
            disable_web_page_preview=True,
        )
        return msg.id

    def delete_message(self, message_id: ty.Optional[int] = None) -> None:
        if message_id is None:
            logger.warning(f"{self.__class__.__name__}: message_id is null")
            return

        try:
            self.bot.delete_message(chat_id=self.chat_id, message_id=message_id)
        except ApiTelegramException as e:
            logger.warning(f"{self.__class__.__name__}: {e}")

    def get_or_save_message_id(
        self, value: ty.Optional[int] = None
    ) -> ty.Optional[int]:
        if value is not None:
            with open(self.FILENAME, "w") as f:
                f.write(str(value))
        else:
            try:
                with open(self.FILENAME, "r") as f:
                    return int(f.read())
            except FileNotFoundError:
                logger.warning(
                    f"{self.__class__.__name__}: filename={self.FILENAME} not found"
                )
                return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", type=str, default="")
    args = parser.parse_args()

    service: NotifyService = NotifyService(
        token=settings.API_TELEGRAM,
        chat_id=settings.CHAT_ID,
        zoom_url=settings.ZOOM_URL,
    )

    if args.action == "send":
        service.get_or_save_message_id(value=service.send_message())
    else:
        service.delete_message(message_id=service.get_or_save_message_id())
