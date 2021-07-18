# coding: utf-8

import datetime as dt
import sys

from core import settings as S
from core.render import render_to_string as rts
from services import ListCommitService, ListEventService, SendMessageService


def main():
    today = dt.date.today()
    is_friday = bool(today.isoweekday() in [5, 6, 7])
    
    events_today, events_tomorrow = ListEventService(
        date=today,
        url=S.CALENDAR_URL,
    )()

    commits = ListCommitService(
        project_id=S.API_GITLAB_PROJECTS[0],
        date=today,
        email=S.EMAIL,
    )()

    rendered_report = rts(
        'ru/report.j2',
        events_today=events_today,
        events_tomorrow=events_tomorrow,
        today=today,
        commits=commits,
        is_friday=is_friday,
    )
    
    if not S.DEBUG:
        SendMessageService(body=rendered_report)()
    else:
        sys.stdout.write(rendered_report + '\n')


if __name__ == '__main__':
    main()
