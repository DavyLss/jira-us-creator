# JiraUSCreator

<p align="center">
  <img src="https://img.shields.io/github/stars/DavyLss/jira-us-creator?style=flat-square" alt="stars" />
  <img src="https://img.shields.io/github/release/DavyLss/jira-us-creator?style=flat-square" alt="releases" />
  <img src="https://img.shields.io/github/last-commit/DavyLss/jira-us-creator?style=flat-square" alt="last commit" />
  <img src="https://img.shields.io/github/license/DavyLss/jira-us-creator?style=flat-square" alt="license" />
  <img src="https://img.shields.io/badge/platform-Windows-2b2b2b?style=flat-square" alt="Windows" />
</p>

<p align="center"><strong>Windows app to create Jira user stories faster, with reusable templates and a simple workflow</strong></p>

---

## Quick facts

- Platform: Windows desktop (executable)
- Language: Python 3.10+ for build, executable distributed
- License: MIT
- Topics: jira, windows, automation, ux, developer-tools

---

## Highlights

- Create user stories faster with templates, a story point helper, and optional sprint assignment
- Find projects and epics quickly, with favorites for the ones you use most
- Save and reuse templates to keep ticket creation consistent
- Simple desktop UI, local configuration, no unnecessary setup

---

## Install & run (English)

1. Download the latest release from Releases
2. Copy `JiraUSCreator.exe` to a folder and run it
3. In Configuration, set your Jira URL and Personal Access Token, test connection, then save


## Build from source (English)

```powershell
# Clone
git clone https://github.com/DavyLss/jira-us-creator.git
cd jira-us-creator

# Install dependencies
pip install -r requirements.txt

# Build (Windows)
.\build.bat
```

Executable will be in `dist\JiraUSCreator.exe`.

---

## Configuration

Local config path:
```
%LOCALAPPDATA%\jira-us-creator\config.json
```

Settings are stored locally, and no secrets belong in the repository. Use a Personal Access Token with only the scopes your Jira setup really needs.

---

## Usage

- Open the app, pick a project, or use your favorites
- Select or search for an Epic, fill in the story, then estimate the story points
- Optionally add the new issue to the active sprint
- Create the ticket, and it is sent to the target Jira instance

---

## Security & privacy

- Do not commit your Jira token, it is stored locally in user config only
- Prefer scoped tokens with the least privileges required for creation and sprint updates

---

## License

MIT License, see the LICENSE file.

---

# JiraUSCreator (FR)

<p align="center"><strong>Application Windows pour créer des user stories Jira plus vite, avec des modèles réutilisables et un workflow simple</strong></p>

---

## Faits rapides

- Plateforme: Windows desktop (exécutable)
- Langage: Python 3.10+ pour la compilation, exécutable distribué
- Licence: MIT
- Topics: jira, windows, automation, ux, developer-tools

---

## Points forts

- Création plus rapide des user stories avec des templates, un aide pour les story points, et l'ajout optionnel au sprint
- Recherche simple des projets et des epics, avec favoris pour les éléments les plus utilisés
- Sauvegarde et réutilisation des templates pour garder une création homogène
- Interface desktop simple, configuration locale, pas de complexité inutile

---

## Installation et exécution (FR)

1. Téléchargez la dernière release depuis Releases
2. Copiez `JiraUSCreator.exe` et lancez-le
3. Dans Configuration, renseignez l'URL Jira et votre Personal Access Token, testez la connexion puis sauvegardez

---

## Compiler depuis les sources (FR)

```powershell
# Cloner
git clone https://github.com/DavyLss/jira-us-creator.git
cd jira-us-creator

# Installer dépendances
pip install -r requirements.txt

# Compiler (Windows)
.\build.bat
```

L'exécutable sera dans `dist\JiraUSCreator.exe`.

---

## Configuration locale

Chemin de config locale:
```
%LOCALAPPDATA%\jira-us-creator\config.json
```

---

## Utilisation (FR)

- Ouvrez l'application, choisissez un projet, ou utilisez vos favoris
- Sélectionnez ou recherchez un Epic, remplissez la user story, puis estimez les story points
- Vous pouvez aussi ajouter directement l'issue au sprint actif
- Cliquez sur créer, et le ticket est envoyé vers votre instance Jira

---

## Sécurité & vie privée (FR)

- Ne commitez pas votre token Jira, il reste en local
- Préférez des tokens restreints aux permissions minimales nécessaires

---

## Licence (FR)

Licence MIT, voir le fichier LICENSE.
