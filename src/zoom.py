import typing as ty

import telebot

from core import settings

if __name__ == "__main__":
    bot: telebot.TeleBot = telebot.TeleBot(settings.API_TELEGRAM, parse_mode="HTML")
    users: ty.List[str] = list()

    for item in bot.get_chat_administrators(settings.CHAT_ID):
        if item.user.username == bot.user.username:
            continue
        if item.user.username:
            users.append(f"@{item.user.username}")
        else:
            users.append(
                f'<a href="tg://user?id={item.user.id}">{item.user.first_name}</a>'
            )

    bot.send_message(
        chat_id=settings.CHAT_ID,
        text=f"{settings.ZOOM_URL}<br><br>{', '.join(users)}.",
        disable_web_page_preview=True,
    )
