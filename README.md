# JiraUSCreator

Application Windows pour créer des User Stories sur Jira via l'API REST.

## Fonctionnalités

- **Connexion à Jira** via Bearer Token (Personal Access Token)
- **Recherche de projets** et sélection par favoris
- **Recherche d'Epics** (Features) liés au projet sélectionné
- **Création de User Stories** avec champs personnalisés :
  - Type de ticket, Type UST, Tâche OPS
  - Composants (chargés dynamiquement depuis Jira)
  - Story Points (saisie manuelle ou estimateur automatique)
  - Priorité, Epic Link
  - Ajout au sprint actif via l'API Agile Jira
  - Assignation automatique à l'utilisateur connecté
- **Estimateur de Story Points** avec guide d'aide interactif
- **Sauvegarde de templates** de User Story
- **Favoris** projets et epics avec accès rapide
- **Dropdowns avec recherche** et hauteur dynamique

## Installation

### Prérequis
- Python 3.10+ (pour compiler depuis les sources)
- Accès à une instance Jira avec un Personal Access Token valide

### Utiliser l'exécutable

1. Téléchargez la dernière version depuis les [Releases](https://github.com/DavyLss/jira-us-creator/releases)
2. Copiez `JiraUSCreator.exe` où vous souhaitez
3. Lancez le fichier
4. Configurez l'URL de votre Jira et votre token dans l'onglet **Configuration**

### Compiler depuis les sources

```powershell
# Cloner le repo
git clone https://github.com/DavyLss/jira-us-creator.git
cd jira-us-creator

# Installer les dépendances
pip install -r requirements.txt

# Compiler l'exécutable
.\build.bat
```

L'exécutable sera généré dans `dist\JiraUSCreator.exe`.

## Utilisation

### Configuration
1. Entrez l'URL de votre instance Jira (ex: `https://jira.votre-entreprise.fr/jira`)
2. Entrez votre **Personal Access Token**
3. Cliquez sur **Tester** pour valider la connexion
4. Cliquez sur **Sauvegarder**

### Créer une User Story
1. Sélectionnez un projet (recherche ou favoris)
2. Sélectionnez un Epic/Feature lié
3. Remplissez les champs : Titre, Description, Type, etc.
4. Utilisez le bouton **Auto** pour estimer les Story Points
5. Cochez **Ajouter au sprint actif** pour assigner automatiquement
6. Cliquez sur **Créer la Jira**

### Désinstaller
- Lancez `uninstall.bat` ou utilisez le bouton **Désinstaller** dans l'onglet Configuration
- Supprime manuellement `%LOCALAPPDATA%\jira-us-creator\` si nécessaire

## Structure

```
jira-us-creator/
├── app.py              # Interface principale (CustomTkinter)
├── jira_api.py         # Client API Jira REST + Agile
├── config.py           # Gestion de la configuration locale
├── main.py             # Point d'entrée
├── build.bat           # Script de compilation PyInstaller
├── install.bat         # Script d'installation
├── uninstall.bat       # Script de désinstallation
├── requirements.txt    # Dépendances Python
└── app.ico             # Icône de l'application
```

## Configuration locale

Les paramètres sont sauvegardés dans :
```
%LOCALAPPDATA%\jira-us-creator\config.json
```

## Licence

[MIT License](LICENSE)
