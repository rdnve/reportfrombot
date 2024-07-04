import argparse

from core import settings
from services import MergeRequestSyncYouTrackService

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", type=str, default="")
    args = parser.parse_args()

    if args.sync == "youtrack":
        for project_id in settings.API_GITLAB_PROJECTS:
            MergeRequestSyncYouTrackService(project_id=project_id)()
