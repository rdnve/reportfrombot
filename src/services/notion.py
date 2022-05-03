# coding: utf-8

import typing as ty

import datetime as dt

from core.requests import session
from core.settings import NOTION_PAGE_ID, NOTION_TOKEN, NOTION_VERSION

NOTION_DOMAIN = "https://api.notion.com/v1"


class NotionReportService:
    """
    Get all blocks from some Notion page.
    """

    def __init__(
        self,
        page_id: ty.Optional[str] = NOTION_PAGE_ID,
        today: ty.Optional[dt.date] = None,
    ) -> None:
        self.page_id = page_id
        self.today = today if today else dt.date.today()
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
        }
        self.blocks = dict(
            nothing=list(), in_process=list(), done=list(), tomorrow=list()
        )

    def __call__(self) -> ty.Dict[str, ty.List[str]]:
        data = self.get_data()
        for item in data:
            state = self.get_state(payload=item)
            text = self.get_text(payload=item)
            self.blocks[state].append(text)
        return self.blocks

    def get_text(self, payload: dict) -> ty.Optional[str]:
        text: str = ""
        items = payload["properties"]["Name"]["title"]
        for item in items:
            text += item["plain_text"]
        return text

    def get_state(self, payload: dict) -> str:
        select = payload["properties"]["Status"]["select"]
        if not select:
            return "nothing"
        return (
            payload["properties"]["Status"]["select"]["name"].replace(" ", "_").lower()
        )

    def get_data(self) -> ty.List[ty.Dict[str, ty.Any]]:
        res = self.make_post_request(f"databases/{self.page_id}/query")
        return res["results"]

    def make_post_request(self, url: str) -> dict:
        query_url = f"{NOTION_DOMAIN}/{url}"
        data = {
            "filter": {
                "property": "Date",
                "date": {"equals": self.today.strftime("%Y-%m-%d")},
            }
        }
        return session.post(query_url, json=data, headers=self.headers).json()
