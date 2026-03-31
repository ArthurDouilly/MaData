# MaData : un outil d'analyse des données du MaD

---

## Au sujet de ce projet

### Les objectifs

Ce *repository* constitue un dépôt pour le projet "MaData", un projet de groupe visant à la création d'un site web au travers d'une application Flask à partir d'une base de données relationnelles réalisée à partir de données du Musée des Arts Décoratifs (MAD) de Paris. Il s'agit de l'une des évaluations finales du M2 TNAH de l'École nationale des Chartes (ENC).

### L'équipe

Ce projet est réalisé de concert par quatre étudiantes & étudiant en M2 TNAH : Léticia Mvogo, Charline Emiry, Neïla Hamoudi et Arthur Douilly.

---

## Fonctionnalités de l'application

L'application Flask realisée dispose de plusieurs fonctionnalités permettant son utilisation pour la visualisation et l'analyse de données : 

- **Recherche simple et avancée** : l'application dispose d'un système de recherche simple et avancée permettant à l'utilisateur de naviguer au sein des données des expositions, activités, séances et types de publics. Il s'agit d'une recherche paginée et plein texte.

- **Export de données** : l'utilisateur peut également faire un export des données des expositions, des activités et des séances grâce au bouton d'export disponible dans les pages d'analyse. Ces exports se font au format CSV.

- **Modélisation de données** : les données disponibles sur la base de données sont disponibles sous un format visuel grâce à l'implémentation de graphiques dynamiques, permettant à l'utilisateur d'accéder à un ensemble d'informations visuelles qui sont mises à jour dynamiquement selon les données disponibles sur la base.

- **Insertion/suppression de données** : il est possible d'utiliser les outils disponibles dans l'onglet "Données" de l'application afin de créer et de supprimer des données directement dans la base de données. Au stade actuel, les données des séances, des expositions et des types d'activités peuvent être insérées et supprimées par l'utilisateur.

---

## Installer et lancer l'application

### Première installation

#### Téléchargement de Python

L'application flask tourne à l'aide du langage Python. Celui-ci doit donc être installé sur votre machine au préalable afin de rendre possible son fonctionnement. Vous pouvez télécharger Python [ici](https://www.python.org/downloads/).

#### Téléchargement de l'application

Afin d'installer l'application Flask, il vous faudra récupérer les fichiers disponibles dans ce dépôt. Cela peut être fait en cliquant sur le bouton `<> Code` sur la page principale du dépot. Github propose alors un téléchargement sous forme de zip, ou alors par le biais de la commande `git clone [lien SSH/HTTPS]` si vous avez configuré un lien entre votre compte git local et GitHub.

#### Récupération de la base de données

##### Connection à PostgreSQL

Une fois l'application téléchargée, assurez-vous d'avoir bien téléchargé le fichier pg_dump (celui-ci n'est pas fourni sur le GitHub mais sera donné séparément). Pour restaurer le dump de la base, ouvrez l'interface de commande et assurez-vous d'être connecté à une instance PostgreSQL (voir [ici](https://www.postgresql.org/download/) pour un tutoriel d'installation de PostgreSQL selon votre OS).

##### Activer la base de données

Avec le Dump de la base de données, lancer la commande suivante :

```
psql -X madata < madatafile
```

La base de donnée devrait ainsi être recréée et activée pour votre compte postgreSQL, vous permettant de l'utiliser en variable d'entrée de l'application.

#### Configuration du .env

Afin de pouvoir lancer l'application, l'utilisateur devra configurer un fichier **.env** (sans aucune extension de fichier) et le placer au même niveau que le fichier **run.py**. Ce fichier devra impérativement comporter les variables suivantes :

```
DEBUG=False
SQLALCHEMY_DATABASE_URI= #postgresql://UTILISATEUR:MOT_DE_PASSE@HOTE:PORT/NOM_BASE
RESULTATS_PAR_PAGE=10
SQLALCHEMY_ECHO=False
SECRET_KEY= #chaîne de caractères
WTF_CRSF_ENABLE=True
```

Pour la variable `SQLALCHEMY_DATABASE_URI` : 

- `UTILISATEUR` correspond à votre nom d'utilisateur Postgresql.

- `MOT_DE_PASSE` correspond à votre mot de passe Postgresql.

- `HOTE` correspond à l'hôte serveur. Pour une installation locale, indiquez localhost.

- `PORT` correspond au port de connection. Pour une installation locale, indiquer 5000.

- `NOM_BASE` = madata

Pour la variable `SECRET_KEY`,  rentrez une chaîne de caractères aléatoires.

#### Mise en place d'un environnement virtuel

Afin de pouvoir utiliser l'application, vous devrez ensuite mettre en place un environnement virtuel afin de pouvoir installer les dépendances de l'application (c'est-à-dire, les modules de Python qui ont été employés pour réaliser l'application, nécessaires à son fonctionnement). 

Dans l'interface de commande, placez-vous dans le dossier de l'application (à l'aide de la commande `cd [chemin vers le dossier]`) puis lancez la commande `python3 -m venv venv`.

Cette commande créera un dossier venv dans lequel se trouvent les fichiers de configuration de l'environnement virtuel. Lancez ensuite cet environnement avec la commande `source venv/bin/activate`.

Une fois l'environnement activé (le nom devrait s'afficher dans l'invite de commandes), installez les dépendances de l'application avec la commande `pip install -r requirements.txt`

Après cette étape, votre configuration initiale est achevée et vous pouvez lancer l'application.

#### Lancement de l'application

Pour lancer l'application, utilisez la commande `python3 run.py`. Cette commande devrait vous indiquer l'URL sur laquelle l'application s'est lancée, typiquement `http://127.01.01.5000` pour une installation locale. Rendez vous à cette adresse sur votre navigateur de choix afin de naviguer sur l'application web.

#### Fermeture de l'application

Pour fermer l'application, utilisez ctrl + c dans l'interface de commande ou fermez la fenêtre pour arrêter le processus.

---

## Lancer l'application après une première installation

Pour lancer l'application après l'installation, il faudra réaliser les étapes suivantes dans l'ordre :

- Se placer au sein du dossier de l'application dans l'interface de commandes (avec la commande cd).

- Réactiver l'environnement virtuel avec `source venv/bin/activate`.

- Relancer l'application avec `python3 run.py`.

- Fermez l'application avec ctrl + c.

Si vous avez cloné le dépôt sur votre machine, vous pouvez additionnellement vérifier si une mise à jour a été réalisée sur le dépôt à l'aide de `git status`, et télécharger toute mise à jour avec `git pull`. Dans le cas où vous avez réalisé des modifications au niveau local, n'oubliez pas de sauvegarder vos modifications avec `git add`/`git commit` avant de réaliser un `git pull`. Ni vos fichiers .env ni l'environnement virtuel ne seront affectés.

