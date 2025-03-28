# Gestion des tâches

Ce projet est une application web de gestion des tâches en temps réel, développée avec Flask et SQLAlchemy.

## Fonctionnalités

- Ajouter, modifier et supprimer des tâches
- Suivre la progression des tâches en temps réel
- Afficher les tâches complétées et en cours
- Mettre à jour la progression des tâches via un code unique
- Générer un QR code pour accéder à la page de mise à jour de la progression

## Prérequis

- Docker
- Docker Compose

## Installation

1. Clonez le dépôt :
    ```bash
    git clone https://github.com/username/activity-screening.git
    cd activity-screening
    ```

2. Construisez et démarrez les services Docker :
    ```bash
    docker-compose up --build
    ```

3. Ouvrez votre navigateur et accédez à `http://localhost:5000` pour voir la liste des tâches.

## Structure du projet

- `app.py` : Fichier principal de l'application Flask
- `create_db.py` : Script pour créer la base de données
- `templates/` : Dossier contenant les fichiers HTML pour les différentes pages
- `static/` : Dossier contenant les fichiers statiques (QR code, CSS, etc.)

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements que vous souhaitez apporter.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
