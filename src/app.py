import typing as ty

import argparse
import datetime as dt
import json
import logging
import telebot
from flask import Flask, jsonify, request

from core import settings
from services import (
    MergeRequestSyncYouTrackService,
    SendMessageService,
    YouTrackReportService,
)

if ty.TYPE_CHECKING:
    from flask.wrappers import Response

app = Flask(__name__)

logger = logging.getLogger(__name__)


@app.route("/__receive", methods=["GET", "POST"])
def main() -> "Response":
    body: ty.Dict[str, ty.Any] = request.json or request.form
    message: ty.Optional[ty.Dict[str, ty.Any]] = body.get("message", None)
    callback: ty.Optional[ty.Dict[str, ty.Any]] = body.get("callback_query", None)
    logger.warning(f"Request body: {json.dumps(body, ensure_ascii=False)}")

    if not any([message, callback]):
        return jsonify(ok=True)

    b = telebot.TeleBot(settings.API_TELEGRAM)

    if message and "reply_to_message" in message:
        from_id = message["reply_to_message"]["from"]["id"]
        if from_id != settings.FROM_ID:
            return jsonify(ok=True)

        b.send_message(
            chat_id=message["chat"]["id"],
            text="Ничего не понял, сейчас позову @rdnve.",
            reply_to_message_id=message["message_id"],
        )
        return jsonify(ok=True)

    if not callback:
        return jsonify(ok=True)

    callback_id = callback["id"]
    message_id = int(callback["message"]["message_id"])
    chat_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    try:
        raw_keys = data.split("_")
        board_name, report_at = raw_keys[0], dt.date.fromisoformat(raw_keys[1])
    except Exception as e:
        logger.warning(f"Parse error: {e}")
        return jsonify(ok=True)

    if dt.date.today() != report_at:
        try:
            b.answer_callback_query(
                callback_query_id=int(callback_id),
                text="Отчёт уже устарел, его нельзя повторно обновить.",
                show_alert=True,
            )
        except Exception as e:
            return jsonify(ok=True)
        else:
            return jsonify(ok=True)

    try:
        key, report = YouTrackReportService(
            board_name=board_name, report_at=report_at
        ).get_report()
    except Exception as e:
        logger.warning(f"Sync error: {e}")
        return jsonify(ok=True)

    markup_keyboard = SendMessageService.get_button_markup(
        text=f"Обновлено от {dt.datetime.now().strftime('%d.%m.%y %H:%M')}",
        callback_data=key,
    )

    try:
        b.edit_message_text(
            report,
            chat_id,
            message_id,
            parse_mode="HTML",
            reply_markup=markup_keyboard,
        )
        b.answer_callback_query(
            callback_query_id=int(callback_id),
            text="Обновлено.",
            show_alert=False,
        )
    except telebot.apihelper.ApiTelegramException as e:
        logger.warning(f"{e}")

        try:
            b.answer_callback_query(
                callback_query_id=int(callback_id),
                text="Отчёт не изменялся, поэтому, обновлять нечего.",
                show_alert=True,
                cache_time=10,
            )
        except telebot.apihelper.ApiTelegramException as e:
            logger.warning(f"{e}")

    logger.warning(
        f"Data: {json.dumps(data, ensure_ascii=False)}, "
        f"callback: {json.dumps(callback, ensure_ascii=False)}"
    )

    return jsonify(ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", type=str, default="")
    args = parser.parse_args()

    if args.sync == "youtrack":
        for project_id in settings.API_GITLAB_PROJECTS:
            MergeRequestSyncYouTrackService(project_id=project_id)()
    elif args.sync == "report":
        key, report = YouTrackReportService().get_report()
        SendMessageService(
            body=report, button=dict(text="Обновить отчёт", callback_data=key)
        )()
    else:
        raise Exception("???")
