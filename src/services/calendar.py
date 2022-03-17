# coding: utf-8

import typing as ty

import datetime as dt
import requests
from ics import Calendar

from services.indexes import DELTA_DAYS


class ListEventService:
    """
    Get all events in some calendar.
    """

    def __init__(self, url: str, date: dt.date):
        self.url = url
        self.date = date
        self.cal_data = None

    def __call__(self) -> ty.Tuple[ty.List[any], ty.List[any]]:
        self.cal_data = Calendar(requests.get(self.url).text)
        today, tomorrow = self.get_sorted_events_by_date()

        return self.get_events(today), self.get_events(tomorrow)

    def filter_data(self, d) -> ty.List[any]:  # noqa: VNE001
        return list(filter(lambda x: x.begin.date() == d, self.cal_data.events))

    def get_sorted_events_by_date(self) -> ty.Tuple[ty.List[any], ty.List[any]]:
        today = self.filter_data(self.date)
        week = self.date.isoweekday()
        if week in [5, 6, 7]:
            tomorrow = self.filter_data(
                self.date + dt.timedelta(days=dict(DELTA_DAYS).get(week)),
            )
        else:
            tomorrow = self.filter_data(self.date + dt.timedelta(days=1))
        return today, tomorrow

    def get_events(self, events) -> ty.List[any]:
        res = list()
        for index, event in enumerate(events):
            res.append(
                {
                    "id": index + 1,
                    "uid": event.uid,
                    "name": event.name,
                    "description": event.description,
                    "is_done": bool(event.url),
                    "name_with_status": "{} {}".format(
                        event.name,
                        "<i>(готово)</i>" if event.url else "",
                    ).strip(),
                }
            )
        return res
