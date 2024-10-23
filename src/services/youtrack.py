import typing as ty

import datetime as dt
import logging

from core import settings
from core.render import render_to_string as rts
from core.requests import session

if ty.TYPE_CHECKING:
    from requests import Response

logger = logging.getLogger(__name__)


class YouTrackReportService:
    """Just sync your tasks"""

    FIELD_POINT_ID: str = "111-28"

    def __init__(
        self, board_name: str = "Current sprint", report_at: dt.date = dt.date.today()
    ) -> None:
        self.base_url: str = f"https://{settings.API_YOUTRACK_DOMAIN}"
        self.headers: ty.Dict[str, str] = {
            "Authorization": f"Bearer {settings.API_YOUTRACK_TOKEN}"
        }
        self.username: str = settings.API_YOUTRACK_USERNAME
        self.board_name: str = board_name
        self.report_at: dt.date = report_at

    def execute(
        self,
        method: str,
        path: str,
        body: ty.Optional[ty.Any] = None,
        query_params: ty.Optional[ty.Dict[str, ty.Any]] = None,
    ) -> ty.Union[ty.List, ty.Dict]:

        kwargs = dict(
            method=method,
            url=f"{self.base_url}{path}",
            headers={"Authorization": f"Bearer {settings.API_YOUTRACK_TOKEN}"},
        )

        if body is not None:
            kwargs["json"] = body

        if query_params is not None:
            kwargs["params"] = query_params

        response: "Response" = session.request(**kwargs)
        response.raise_for_status()

        return response.json()

    def get_internal_ids_from_issues(self) -> ty.List[str]:
        res = self.execute(
            method="get",
            path="/api/sortedIssues",
            query_params={
                "query": " ".join(
                    [
                        "Assigned: %s" % self.username,
                        "{Board Development}: {%s}" % self.board_name,
                        "Stage: {Test & Review}",
                        "Stage: {Done}",
                    ]
                ),
                "$top": "-1",
                "fields": "tree(id)",
            },
        )

        return [x["id"] for x in res["tree"]]

    def get_issues(self) -> ty.List[ty.Dict[str, str]]:
        res = self.execute(
            method="post",
            path="/api/issuesGetter",
            body=[
                {"id": current_id} for current_id in self.get_internal_ids_from_issues()
            ],
            query_params={
                "$top": "-1",
                "fields": "summary,idReadable,fields(id(111-28),value)",
            },
        )

        issues = list()
        for item in res:
            raw = {
                "issue_id": item["idReadable"],
                "summary": item["summary"],
                "url": f'{self.base_url}/issue/{item["idReadable"]}',
                "point": "?",
            }
            for field in item["fields"]:
                if field["id"] == self.FIELD_POINT_ID:
                    raw["point"] = field["value"]
                    break

            issues.append(raw)

        issues.reverse()
        return issues

    def get_board_name(self, issue_id: str) -> str:

        res = self.execute(
            method="get",
            path=f"/api/issues/{issue_id}/sprints",
            query_params={
                "$top": "-1",
                "fields": "id,name",
            },
        )

        return res[0]["name"]

    def get_report(self) -> ty.Tuple[str, str]:
        issues = self.get_issues()
        board_name = self.get_board_name(issue_id=issues[0]["issue_id"])
        report = rts("ru/report_v4.j2", issues=issues, today=self.report_at).strip()

        return f"{board_name}_{self.report_at.isoformat()}", report


if __name__ == "__main__":
    from services.telegram import SendMessageService

    key, report = YouTrackReportService().get_report()

    SendMessageService(
        body=report, button=dict(text="Обновить отчёт", callback_data=key)
    )()
