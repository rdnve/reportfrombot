import typing as ty

import datetime as dt
import logging

from core.requests import session

logger = logging.getLogger(__name__)


def plural(value: str, quantitative: ty.Tuple[ty.Any]) -> ty.Any:
    if value % 100 in (11, 12, 13, 14):
        return quantitative[2]
    if value % 10 == 1:
        return quantitative[0]
    if value % 10 in (2, 3, 4):
        return quantitative[1]
    return quantitative[2]


def is_allowed_to_update(report_at: dt.date) -> bool:
    today = dt.date.today()
    if report_at.isoweekday() in {5, 6, 7} and (today - report_at).days < 3:
        return True

    if today != report_at:
        return False

    return False


def is_dayoff() -> bool:
    try:
        res: str = session.get("https://isdayoff.ru/today", timeout=5).text
    except Exception as e:
        logger.exception(e)
    else:
        if res == "1":
            return True

    return False
