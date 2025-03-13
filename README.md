# Gestion des tâches

Ce projet est une application web de gestion des tâches en temps réel, développée avec Flask et SQLAlchemy.

## Fonctionnalités

- Ajouter, modifier et supprimer des tâches
- Suivre la progression des tâches en temps réel
- Afficher les tâches complétées et en cours
- Mettre à jour la progression des tâches via un code unique
- Générer un QR code pour accéder à la page de mise à jour de la progression

## Prérequis

- Python 3.x
- pip (Python package installer)

## Installation

1. Clonez le dépôt :
    ```bash
    git clone https://github.com/username/activity-screening.git
    cd activity-screening
    ```

2. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

3. Créez la base de données :
    ```bash
    python create_db.py
    ```

## Utilisation

1. Lancez l'application :
    ```bash
    python app.py
    ```

2. Ouvrez votre navigateur et accédez à `http://<votre_ip_locale>:5000` pour voir la liste des tâches.

## Structure du projet

- `app.py` : Fichier principal de l'application Flask
- `create_db.py` : Script pour créer la base de données
- `templates/` : Dossier contenant les fichiers HTML pour les différentes pages
- `static/` : Dossier contenant les fichiers statiques (QR code, CSS, etc.)

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements que vous souhaitez apporter.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
