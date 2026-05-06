import requests


class JiraAPI:
    def __init__(self, url, token, verify_ssl=True):
        self.url = url.rstrip("/")
        self.token = token
        self.verify = verify_ssl
        self.user = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def test_connection(self):
        url = f"{self.url}/rest/api/2/myself"
        try:
            resp = requests.get(url, headers=self.headers,
                                verify=self.verify, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                self.user = data.get("name", "")
                return True, data.get("displayName", self.user), data.get("emailAddress", "")
            elif resp.status_code == 401:
                return False, None, "Token invalide"
            else:
                return False, None, f"Erreur {resp.status_code}: {resp.text[:200]}"
        except requests.exceptions.SSLError:
            return False, None, "Erreur SSL. Essayez de désactiver la vérification SSL."
        except requests.exceptions.ConnectionError:
            return False, None, "Impossible de se connecter. Vérifiez l'URL."
        except Exception as e:
            return False, None, str(e)

    def get_projects(self):
        url = f"{self.url}/rest/api/2/project"
        resp = requests.get(url, headers=self.headers,
                            verify=self.verify, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        return []

    def search_epics(self, search_text="", max_results=50):
        words = [w.strip() for w in search_text.replace("-", " ").split() if w.strip()]
        if not words:
            jql = "issuetype = Feature ORDER BY project, key DESC"
        elif len(words) == 1:
            jql = f'issuetype = Feature AND summary ~ "{words[0]}*" ORDER BY project, key DESC'
        else:
            clauses = " AND ".join([f'summary ~ "{w}*"' for w in words])
            jql = f"issuetype = Feature AND {clauses} ORDER BY project, key DESC"
        url = f"{self.url}/rest/api/2/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,key,project"
        }
        resp = requests.get(url, headers=self.headers,
                            params=params, verify=self.verify, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("issues", [])
        return []

    def create_user_story(self, project_key, summary, description, ticket_type="User Story", ust_type=None, task_ops=None, story_points=None, priority=None, feature_key=None, assignee=None):
        url = f"{self.url}/rest/api/2/issue"
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": ticket_type},
            }
        }

        if ust_type:
            payload["fields"]["customfield_35351"] = {"value": ust_type}

        if task_ops:
            payload["fields"]["customfield_35353"] = {"value": task_ops}

        if story_points is not None:
            payload["fields"]["customfield_10353"] = story_points

        if priority:
            payload["fields"]["priority"] = {"name": priority}

        if feature_key:
            payload["fields"]["customfield_12950"] = feature_key

        resp = requests.post(url, headers=self.headers,
                             json=payload, verify=self.verify, timeout=30)
        if resp.status_code in (200, 201):
            data = resp.json()
            key = data.get("key", "")
            if assignee and key:
                self._assign_issue(key, assignee)
            return True, key, data.get("self", "")
        elif priority and "priority" in resp.text.lower():
            payload["fields"].pop("priority", None)
            resp2 = requests.post(url, headers=self.headers,
                                  json=payload, verify=self.verify, timeout=30)
            if resp2.status_code in (200, 201):
                data = resp2.json()
                key = data.get("key", "")
                if assignee and key:
                    self._assign_issue(key, assignee)
                return True, key, data.get("self", "")
            else:
                return False, None, resp2.text[:500]
        else:
            return False, None, resp.text[:500]

    def _assign_issue(self, issue_key, assignee_name):
        url = f"{self.url}/rest/api/2/issue/{issue_key}/assignee"
        payload = {"name": assignee_name}
        try:
            requests.put(url, headers=self.headers,
                         json=payload, verify=self.verify, timeout=15)
        except Exception:
            pass
