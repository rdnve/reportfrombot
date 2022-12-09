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
        self.page_id: str = page_id
        self.today: dt.date = today if today else dt.date.today()
        self.headers: ty.Dict[str, ty.Any] = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
        }
        self.blocks: ty.Dict[str, ty.Any] = dict(
            nothing=list(),
            cold_backlog=list(),
            hot_backlog=list(),
            in_process=list(),
            done=list(),
            tomorrow=list(),
            additionally=list(),
        )

    def __call__(self) -> ty.Dict[str, ty.List[str]]:
        data = self.get_data(f"databases/{self.page_id}/query")
        for item in data["results"]:
            state = self.get_state(payload=item)
            text = self.get_text(payload=item)
            self.blocks[state].append(text)
        return self.blocks

    def get_text(self, payload: ty.Dict[str, ty.Any]) -> ty.Optional[str]:
        text: str = ""
        items = payload["properties"]["Name"]["title"]
        for item in items:
            text += item["plain_text"]
        return text

    def get_state(self, payload: ty.Dict[str, ty.Any]) -> str:
        select = payload["properties"]["Status"]["select"]
        if not select:
            return "nothing"
        return (
            payload["properties"]["Status"]["select"]["name"].replace(" ", "_").lower()
        )

    def get_data(self, url: str) -> ty.Dict[str, ty.Any]:
        query_url: str = f"{NOTION_DOMAIN}/{url}"
        data: ty.Dict[str, ty.Any] = {
            "filter": {
                "property": "Date",
                "date": {"equals": self.today.strftime("%Y-%m-%d")},
            },
            "sorts": [{"property": "Status", "direction": "ascending"}],
        }
        return session.post(query_url, json=data, headers=self.headers).json()
