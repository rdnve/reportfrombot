# coding: utf-8

import typing as ty

import datetime as dt
import gitlab

from core import settings as S


class ListCommitService:
    """
    Return all commites by date.
    """

    def __init__(
        self,
        project_id: int,
        date: dt.date,
        email: ty.Optional[str] = S.EMAIL,
    ):
        self.project_id = project_id
        self.email = email
        self.date = date

    def __call__(self) -> ty.Tuple[str, ty.List[any]]:
        self.gl = gitlab.Gitlab(
            S.API_GITLAB_URL,
            private_token=S.API_GITLAB_KEY,
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
