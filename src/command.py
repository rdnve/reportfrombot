import argparse

from core import settings
from services import MergeRequestSyncYouTrackService

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", type=str, default="")
    args = parser.parse_args()

    if args.sync == "youtrack":
        MergeRequestSyncYouTrackService(project_id=settings.API_GITLAB_PROJECTS[0])()
