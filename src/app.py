# coding: utf-8

import argparse
import datetime as dt
import json
import logging
import telebot
from dateutil.parser import ParserError, parse
from flask import Flask, jsonify, request

from core import settings
from core.render import render_to_string as rts
from services import (
    MergeRequestSyncYouTrackService,
    NotionReportService,
    SendMessageService,
)

app = Flask(__name__)

logger = logging.getLogger(__name__)


@app.route("/__receive", methods=["GET", "POST"])
def main():
    body = request.json or request.form
    logger.warning(f"Request body: {json.dumps(body, ensure_ascii=False)}")

    if "callback_query" not in body:
        return jsonify(ok=True)

    callback = body["callback_query"]
    callback_id = callback["id"]

    message_id = int(callback["message"]["message_id"])
    chat_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    try:
        parsed_datetime = parse(data)
    except ParserError as e:
        logger.warning(f"Parse error: {e}")
        return jsonify(ok=True)

    b = telebot.TeleBot(settings.API_TELEGRAM)

    if (dt.date.today() - parsed_datetime.date()).days > 2:
        b.answer_callback_query(
            callback_query_id=int(callback_id),
            text="Обновлять можно только за текущий и вчерашний день.",
            show_alert=True,
        )
        return jsonify(ok=True)

    today = parsed_datetime.date()
    data = NotionReportService(today=today)()
    rendered_report = rts(
        "ru/report_v2.j2",
        data=data,
        today=today,
        is_friday=bool(today.isoweekday() in {5, 6, 7}),
    ).replace("\n__null__\n", "")

    markup_keyboard = SendMessageService.get_button_markup(
        text="Обновить данные",
        callback_data=today.strftime("%Y-%m-%d"),
    )

    try:
        b.edit_message_text(
            rendered_report,
            chat_id,
            message_id,
            parse_mode="HTML",
            reply_markup=markup_keyboard,
        )
    except telebot.apihelper.ApiTelegramException as e:
        logger.warning(f"{e}")
        b.answer_callback_query(
            callback_query_id=int(callback_id),
            text="Отчёт не изменялся, поэтому, обновлять нечего.",
            show_alert=True,
            cache_time=10,
        )

    logger.warning(
        (
            f"Data: {json.dumps(data, ensure_ascii=False)}, "
            f"callback: {json.dumps(callback, ensure_ascii=False)}"
        )
    )

    return jsonify(ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", type=str, default="")
    args = parser.parse_args()

    # if args.sync == "youtrack":
    MergeRequestSyncYouTrackService(project_id=settings.API_GITLAB_PROJECTS[0])()
