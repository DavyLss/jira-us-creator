# JiraUSCreator

<p align="center">
  <img src="https://img.shields.io/github/stars/DavyLss/jira-us-creator?style=flat-square" alt="stars" />
  <img src="https://img.shields.io/github/release/DavyLss/jira-us-creator?style=flat-square" alt="releases" />
  <img src="https://img.shields.io/github/last-commit/DavyLss/jira-us-creator?style=flat-square" alt="last commit" />
  <img src="https://img.shields.io/github/license/DavyLss/jira-us-creator?style=flat-square" alt="license" />
  <img src="https://img.shields.io/badge/platform-Windows-2b2b2b?style=flat-square" alt="Windows" />
</p>

<p align="center"><strong>Small Windows app to create Jira user stories from templates, fast and reliable</strong></p>

---

## Quick facts

- Platform: Windows desktop (executable)
- Language: Python 3.10+ for build, executable distributed
- License: MIT
- Topics: jira, windows, automation, ux, developer-tools

---

## Highlights

- Create user stories quickly using templates, story point estimator, and optional add-to-sprint workflow
- Search and select projects and epics, favorites support
- Save and reuse templates for consistent ticket creation
- Lightweight, offline-capable UI (local config storage)

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

Settings saved locally, no secrets are committed to the repo. Use a Personal Access Token with the minimal scopes required by your Jira instance.

---

## Usage

- Open the app, select project or use favorites
- Select or search for an Epic, fill the story template, estimate story points
- Optionally add created issue to the active sprint
- Create, and the ticket will be opened in the target Jira instance

---

## Security & privacy

- Do not commit your Jira token, it is stored locally in user config only
- Prefer scoped tokens with the least privileges required for creation and sprint updates

---

## License

MIT License — see LICENSE file.

---

# JiraUSCreator (FR)

<p align="center"><strong>Application Windows pour créer rapidement des user stories Jira depuis des modèles</strong></p>

---

## Faits rapides

- Plateforme: Windows desktop (exécutable)
- Langage: Python 3.10+ pour la compilation, exécutable distribué
- Licence: MIT
- Topics: jira, windows, automation, ux, developer-tools

---

## Points forts

- Création rapide de user stories avec templates et estimateur de story points
- Recherche et sélection de projets et d'epics, prise en charge des favoris
- Sauvegarde et réutilisation des templates
- UI légère, stockage local des paramètres, fonctionnement hors ligne pour la configuration

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

- Ouvrez l'application, sélectionnez un projet ou utilisez vos favoris
- Sélectionnez un Epic, remplissez le template, estimer les story points
- Optionnel: ajouter l'issue créée au sprint actif
- Cliquez sur créer, et la ticket sera publié dans votre instance Jira

---

## Sécurité & vie privée (FR)

- Ne commitez pas votre token Jira, il reste en local
- Préférez des tokens restreints aux permissions minimales nécessaires

---

## Licence (FR)

Licence MIT — voir le fichier LICENSE.
