# coding: utf-8

import json
import os
from dotenv import load_dotenv

load_dotenv()

# main consts
DEBUG = bool(os.getenv('DEBUG'))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

# for telegram
API_TELEGRAM = os.getenv('API_TELEGRAM')
CHAT_ID = int(os.getenv('CHAT_ID'))

# for commits and other
API_GITLAB_URL = os.getenv('API_GITLAB_URL')
API_GITLAB_KEY = os.getenv('API_GITLAB_KEY')
API_GITLAB_PROJECTS = json.loads(os.getenv('API_GITLAB_PROJECTS', '[]'))

# just my email
EMAIL = os.getenv('EMAIL')

# calendar endpoints
CALENDAR_URL = os.getenv('CALENDAR_URL')