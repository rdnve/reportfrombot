# coding: utf-8

import typing as ty

import datetime as dt
import gitlab
import re

from core import settings
from core.requests import session


class ListCommitService:
    """
    Return all commites by date.
    """

    def __init__(
        self,
        project_id: int,
        date: dt.date,
        email: ty.Optional[str] = settings.EMAIL,
    ):
        self.project_id = project_id
        self.email = email
        self.date = date

    def __call__(self) -> ty.Tuple[str, ty.List[any]]:
        self.gl = gitlab.Gitlab(
            settings.API_GITLAB_URL,
            private_token=settings.API_GITLAB_KEY,
        )
        self.project = self.gl.projects.get(self.project_id)
        return self.get_committs()

    def get_committs(self) -> ty.List[any]:
        res = []
        for commit in self.project.commits.ty.List():
            commited_date = dt.datetime.fromisoformat(
                commit.committed_date,
            ).date()
            if commited_date < self.date:
                break
            if commit.committer_email != self.email:
                continue
            res.append(
                {
                    "title": commit.title,
                    "url": commit.web_url,
                    "id": commit.id[:8],
                }
            )
        return res


class MergeRequestSyncYouTrackService:
    """
    Sync titles in merge requests with YouTrack issues.
    """

    def __init__(self, project_id: int):
        self.project_id = project_id
        self.url = f"https://{settings.API_YOUTRACK_DOMAIN}/youtrack/api"
        self.headers = {
            "Authorization": f"Bearer {settings.API_YOUTRACK_TOKEN}",
        }

    def __call__(self):
        self.gl = gitlab.Gitlab(
            settings.API_GITLAB_URL,
            private_token=settings.API_GITLAB_KEY,
        )
        project = self.gl.projects.get(id=self.project_id)
        for mr in project.mergerequests.list(state="opened"):
            task_id = self.extract_task_id(value=mr.title)
            if task_id is None:
                continue
            summary = self.get_youtrack_summary(task_id=task_id)
            new_title = f"{task_id} {summary}"
            if mr.draft:
                new_title = f"Draft: {new_title}"
            if new_title != mr.title:
                mr.title = new_title
                mr.save()

    @staticmethod
    def extract_task_id(value: str) -> ty.Optional[str]:
        results = re.findall("(DEV-\d+)", value)
        if not results:
            return None
        return results[0]

    def get_youtrack_summary(self, task_id: str) -> str:
        res = session.get(
            f"{self.url}/issues/{task_id}",
            headers=self.headers,
            params=dict(fields="idReadable,summary"),
        )
        res.raise_for_status()
        return res.json()["summary"]
