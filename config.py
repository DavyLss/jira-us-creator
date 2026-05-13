import json
import os
import sys


def _get_config_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(os.environ.get("LOCALAPPDATA", "."), "jira-us-creator")
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_DIR = _get_config_dir()
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "jira_url": "",
    "jira_token": "",
    "verify_ssl": False,
    "favorite_projects": [],
    "favorite_epics": {},

    "template_us": {
        "description": "En tant que DevOps, je veux \"OBJECTIF\" afin de \"BENEFICE ATTENDU\".\n\nContraintes techniques : \"OUTIL OU TECHNOLOGIE\"\nContraintes fonctionnelles :\nCritères d'acceptations : ",
        "acceptance_criteria": "* Critère 1 : \n* Critère 2 : \n* Critère 3 : "
    },
    "last_created": []
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    return DEFAULT_CONFIG.copy()


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_config_path():
    return CONFIG_PATH
