import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "jira_url": "https://jira.votre-entreprise.fr/jira",
    "jira_token": "",
    "verify_ssl": False,
    "favorite_projects": [],
    "template_us": {
        "description": "En tant que DevOps, je dois mettre en place xxx afin de xxxx.",
        "acceptance_criteria": "* Critère 1 : \n* Critère 2 : \n* Critère 3 : "
    }
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        for key, value in DEFAULT_CONFIG.items():
            if key not in config or (isinstance(config[key], str) and config[key] == ""):
                config[key] = value
        return config
    return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_config_path():
    return CONFIG_PATH
