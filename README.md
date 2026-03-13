# Au sujet de ce projet

Ce *repository* constitue un dépôt pour le projet "MaData", un projet de groupe visant à la création d'un site web au travers d'une application Flask à partir d'une base de données relationnelles réalisée au sujet du Musée des Arts Décoratifs (MAD) de Paris. Il s'agit de l'une des évaluations finales du M2 TNAH de l'École nationale des Chartes (ENC).

## L'équipe du projet

Ce projet est réalisé de concert par quatre étudiantes & étudiant en M2 TNAH : Léticia Mvogo, Charline Emiry, Neïla Hamoudi et Arthur Douilly.

### Structure du dépôt

#### Architecture de l'application web

Le dossier **app** contient tous les éléments nécessaires au bon fonctionnement de l'application flask. Il est composé de plusieurs sous-dossiers qui font office de modules python :

- **models** contient le code des formulaires et de l'ORM.

- **routes** contient le code des routes de l'application web.

- **statics** contient le code et les éléments statiques de l'application (css, polices d'écriture...).

- **templates** contient le code des pages webs sous la forme de templates généraux (pages) et partiels (partials) du site, au format HTML et en employant JINJA.

#### Branches

Les différentes branches du projet servent à travailler en évitant le téléscopage des versions. On distingue plusieurs branches spécifiques :

- **main**, la branche des versions officielles et validées par l'équipe.

- **test**, la branche de merge de la version en production.

- **[feature]-dev**, des branches servant à la réalisation du code en phase initiale avant les merge dans la branche de test.
