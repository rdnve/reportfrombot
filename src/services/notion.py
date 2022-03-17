# coding: utf-8

import typing as ty

from core.requests import session
from core.settings import NOTION_PAGE_ID, NOTION_TOKEN, NOTION_VERSION

NOTION_DOMAIN = "https://api.notion.com/v1"


class NotionReportService:
    """
    Get all blocks from some Notion page.
    """

    def __init__(self, page_id: ty.Optional[str] = NOTION_PAGE_ID) -> None:
        self.page_id = page_id
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
        }

    def __call__(self) -> ty.Dict[str, ty.Any]:
        title = self.get_page_title()
        blocks = self.get_page_blocks()
        return dict(
            title=title,
            blocks=blocks,
        )

    def make_request(self, url: str) -> dict:
        return session.get(f"{NOTION_DOMAIN}/{url}", headers=self.headers).json()

    def get_page_title(self) -> str:
        res = self.make_request(f"pages/{self.page_id}")
        return res["properties"]["title"]["title"][0]["plain_text"]

    def get_page_blocks(self) -> ty.List[ty.Dict[str, ty.Any]]:
        data = list()
        res = self.make_request(f"blocks/{self.page_id}/children")
        for item in res["results"]:
            type_ = item["type"]
            body = item[type_]["rich_text"]

            if not body:
                continue

            if type_ == "heading_2":
                obj = dict(
                    type=type_,
                    text=body[0]["plain_text"],
                    is_done=None,
                )
            else:
                obj = dict(
                    type=type_,
                    text=body[0]["plain_text"],
                    is_done=item[type_]["checked"],
                )
            data.append(obj)

        return data
