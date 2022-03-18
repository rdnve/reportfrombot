# coding: utf-8

import datetime as dt
import sys

from core import settings
from core.render import render_to_string as rts
from services import (
    ListCommitService,
    ListEventService,
    NotionReportService,
    SendMessageService,
)


def extract_from_commits():
    today = dt.date.today()
    is_friday = bool(today.isoweekday() in [5, 6, 7])

    events_today, events_tomorrow = ListEventService(
        date=today,
        url=settings.CALENDAR_URL,
    )()

    commits = []
    for project_id in settings.API_GITLAB_PROJECTS:
        commits += ListCommitService(
            project_id=project_id,
            date=today,
            email=settings.EMAIL,
        )()

    rendered_report = rts(
        "ru/report.j2",
        events_today=events_today,
        events_tomorrow=events_tomorrow,
        today=today,
        commits=commits,
        is_friday=is_friday,
    )

    if not settings.DEBUG:
        SendMessageService(body=rendered_report)()
    else:
        sys.stdout.write(rendered_report + "\n\n")


def extract_from_notion():
    today = dt.date.today()
    data = NotionReportService(today=today)()
    rendered_report = rts(
        "ru/report_v2.j2",
        data=data,
        today=today,
        is_friday=bool(today.isoweekday() in {5, 6, 7}),
    )
    if data["nothing"] or data["done"] or data["tomorrow"]:
        SendMessageService(body=rendered_report)()


if __name__ == "__main__":
    extract_from_notion()
