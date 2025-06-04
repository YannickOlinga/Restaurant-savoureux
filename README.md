# Savoureux - Restaurant Web Application

Une application web moderne pour la gestion d'un restaurant, développée avec Django.

## Fonctionnalités

- 🍽️ Menu interactif avec filtrage et recherche
- 🛒 Système de panier d'achat
- 👤 Gestion des comptes utilisateurs
- 📅 Système de réservation
- 🌙 Mode sombre/clair
- 📱 Design responsive
- 🔐 Interface d'administration sécurisée

## Technologies Utilisées

- Django 5.1.7
- Python 3.12
- HTML5/CSS3
- JavaScript
- SQLite

## Installation

1. Clonez le repository
```bash
git clone https://github.com/votre-username/savoureux.git
cd savoureux
```

2. Créez un environnement virtuel et activez-le
```bash
python -m venv env
source env/bin/activate  # Sur Unix/macOS
env\Scripts\activate     # Sur Windows
```

3. Installez les dépendances
```bash
pip install -r requirements.txt
```

4. Effectuez les migrations
```bash
python manage.py migrate
```

5. Créez un superutilisateur
```bash
python manage.py createsuperuser
```

6. Lancez le serveur
```bash
python manage.py runserver
```

## Structure du Projet

```
resto/
├── ecomm/              # Application principale
├── resto/              # Configuration du projet
├── media/              # Fichiers média uploadés
├── static/             # Fichiers statiques
└── templates/          # Templates HTML
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 