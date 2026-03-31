'''
Fichier regroupant les routes générales, càd les routes vers les pages principales de l'application web.
'''

# ----- importation des modules python -----

from ..app import app, db
from ..models.madata import * # on importe tout le modèle de données
from ..models.formulaires import Recherche
from sqlalchemy import Function, or_, func, cast, String
from flask import request, render_template, redirect, url_for, Response, current_app
from collections import Counter
import io
import csv
from ..utils.transformations import nettoyage_string_to_int, clean_arg # pour nettoyer

# ----- création des routes -----

# --- routes générales ---

# routes de la page d'accueil

@app.route("/") # redirige immédiatement sur la page /index ci-dessous
def home():
    return redirect(url_for("index")) # redirect(url_for) permet de faire la redirection

@app.route("/accueil") # page d'accueil du site
def index():
    return render_template("pages/index.html") # on utilise ici simplement un render_template

@app.route("/ajout") # page recensant les pages d'insertions et suppressions
def ajout():
    '''
    Page par défaut recensant les pages d'insertions et de suppressions de séances
    '''
    return render_template("pages/ajout.html")

# routes d'erreur
@app.route("/erreur") # page d'erreur
@app.route("/erreur/404") # page de l'erreur 404
def erreur_404():

    return render_template("erreurs/404.html")
@app.route("/erreur/500") # page de l'erreur 500
def erreur_500():

    return render_template("erreurs/500.html")

# ----- routes liées à une catégorie de données -----

# --- expositions ---

# route du sommaire des expositions

@app.route("/expositions",methods=['GET', 'POST'])
def expositions():
    '''
    Cette route crée une page de sommaire des expositions par le biais d'une liste de dictionnaires
    '''
    liste_expos = [{'nom_expo': 'Toutes les expositions', 'id_expo': 'ALL'}] # initialisation d'une liste contenant des dictionnaires

    for exposition in Expositions.query.all(): # boucle pour créer les dictionnaires
        expo = dict(
            nom_expo = str(exposition.nom_exposition), # récupère les noms et les passe en str
            id_expo = str(exposition.id_exposition) # récupère les id et les passe en str
        )
        liste_expos.append(expo) # ajout des dictionnaires dans la liste

    return render_template('pages/expositions_sommaire.html',liste_expos=liste_expos)

# route des pages d'exposition

@app.route("/expositions/<string:exposition_choisie>", methods=['GET', 'POST'])
def detail_exposition(exposition_choisie):
    '''
    Le but de cette route est de rendre un ensemble d'informations devant servir d'entrée aux graphiques générés pour les expositions
    '''

    # vérification préalable afin d'éviter l'injection de code dans l'URL
    liste_vérification = ['ALL']

    for exposition in Expositions.query.all():
        id_expo = exposition.id_exposition
        liste_vérification.append(id_expo)

    if exposition_choisie not in liste_vérification:
        return redirect(url_for('erreur_404'))

    # requête 1 : toutes les expositions renseignées dans la table 'Expositions'

    if exposition_choisie == 'ALL' : # si on veut regarder toutes les expositions
        resultats = Expositions.query.all()
    else:
        resultats = Expositions.query.filter(Expositions.id_exposition == exposition_choisie).first()

    # requête 2 : les informations d'entrée du graphique fréquentation/jour

    #  requête avec jointure entre Capacité et Séances, sélectionnant les places vendues et la date
    if exposition_choisie == 'ALL' : # si on veut regarder toutes les expositions
        frequentations = Capacite.query.\
            select_from(Capacite).\
            with_entities(Capacite.places_vendues, Seances.date_seance).\
            join(Capacite.seances_capacite).\
            group_by(Seances.date_seance,Capacite.places_vendues).\
            order_by(Seances.date_seance).all()
    else : 
        frequentations = Capacite.query.\
            select_from(Capacite).\
            with_entities(Capacite.places_vendues, Seances.date_seance).\
            join(Capacite.seances_capacite).\
            filter(Seances.id_exposition == exposition_choisie).\
            group_by(Seances.date_seance,Capacite.places_vendues).\
            order_by(Seances.date_seance).all()

    frequentation_jour = {} # initialisation du dictionnaire vide

    for frequentation in frequentations: # boucle de traitement des valeurs récupérées pour ajout dans le dictionnaire
        if frequentation.date_seance in frequentation_jour: # si la clé[date] existe dans le dictionnaire
            if frequentation.places_vendues == None: # remplacement du None par un zéro
                frequentation_jour[frequentation.date_seance] += 0
            else:
                frequentation_jour[frequentation.date_seance] += frequentation.places_vendues
        else: # si la clé n'existe pas, on crée la clé avant de boucler de nouveau
            if frequentation.places_vendues == None: # remplacement du None par un zéro
                frequentation_jour[frequentation.date_seance] = 0
            else:
                frequentation_jour[frequentation.date_seance] = frequentation.places_vendues

    jour = iter(frequentation_jour.keys()) # iter() permet d'itérer sur les clés du dictionnaire
    places_total = iter(frequentation_jour.values()) # et ici sur les valeurs

    frequentation_journée = [] # initialisation de la liste vide

    for keys in frequentation_jour:
        places_dict = dict(
            date = next(jour),
            places = next(places_total)
        )
        frequentation_journée.append(places_dict)


     # Graphique 1 : données pour Chart.js

    # Création de listes vides
    dates = []
    places = []

    # Boucle sur frequentation_journée
    for f in frequentation_journée:
        if f["places"] != 0:  #jours avec 0 visites ignorés, pour éviter les plages de vide
            dates.append(f["date"].strftime("%Y-%m-%d"))  #date au format ann-mois-jr
            places.append(f["places"])

    # requête 3 : les informations d'entrée du graphique fréquentation/public

    if exposition_choisie == 'ALL' : # si on veut regarder toutes les expositions
        expo_publics = Seances.query.select_from(Seances).\
            join(Publics, Seances.seance_publics).\
            with_entities(Publics.type_public).all()
    else:
        # requête devant permettre de conditionner les groupes selon l'exposition
        expo_publics = Seances.query.select_from(Seances).\
            join(Publics, Seances.seance_publics).\
            filter(Seances.id_exposition == exposition_choisie).\
            with_entities(Publics.type_public).all()

    frequentation_publics = [] # initiation d'une liste vide

    c = Counter(expo_publics) # la variable c utilise Counter pour créer un dictionnaire recensant les occurences de type_public
    iterateur_k = iter(c.keys()) # iter() permet d'itérer sur une série, ici les clés de c
    iterateur_v = iter(c.values()) # et là les valeurs de c

    for keys in c: # création d'un dictionnaire par le biais d'une boucle for
        expo_dict = dict(
            type_public = str(next(iterateur_k))[2:-3], # nettoyage des string
            compte = next(iterateur_v)
        )
        frequentation_publics.append(expo_dict) # ajout à la liste vide initiée plus haut


    # Graphique 2 : données pour Chart.js (même logique)
    type_public = []
    compte = []

    for f in frequentation_publics:
        if f["compte"] != 0:
            type_public.append(str(f["type_public"]))
            compte.append(f["compte"])

    # requête 4 : récupération des détails des visiteurs

    if exposition_choisie == 'ALL' : # si on veut regarder toutes les expositions
            # requête permettant de récupérer directement les informations depuis Groupes
            visiteurs = Groupes.query.with_entities(Groupes.id_groupe,Groupes.ville,Groupes.type_client).\
            distinct(Groupes.id_groupe).\
            order_by(Groupes.id_groupe).all()
    else :
        # requête devant permettre de conditionner les groupes selon l'exposition
        visiteurs = Seances.query.select_from(Seances).\
            join(Groupes, Seances.seance_groupes).\
            distinct(Groupes.id_groupe).\
            with_entities(Groupes.id_groupe,Groupes.ville,Groupes.type_client).\
            filter(Seances.id_exposition == exposition_choisie).\
            order_by(Groupes.id_groupe).all()
        
   # Graphique 3 : données pour Chart.js (compteur)
    types = [a.type_client for a in visiteurs if a.type_client is not None] #récupérer visiteurs en excluant None
    comptage_client = Counter(types) #on compte les occurances
    type_client_labels = list(comptage_client.keys()) #on récupère les noms
    type_client_data = list(comptage_client.values()) #et le nombre de fois qu'ils apparaissent

    # Graphique 4 : données pour Chart.js (même logique de compteur)
    villes = [b.ville for b in visiteurs if b.ville is not None]
    comptage_villes = Counter(villes)
    villes = comptage_villes.most_common(5)  #retourne les 5 plus fréquentes
    villes_labels = [v[0] for v in villes]
    villes_data = [v[1] for v in villes]

    return render_template("pages/une_exposition.html", exposition_choisie=exposition_choisie,
        resultats=resultats,
        frequentation_journée=frequentation_journée,
        frequentation_publics=frequentation_publics,
        visiteurs=visiteurs,
        sous_titre="Détails des expositions du MAD",
        dates=dates,
        places=places,
        type_public=type_public,
        compte=compte,
        type_client_labels=type_client_labels,  
        type_client_data=type_client_data,
        villes_labels=villes_labels,
        villes_data=villes_data
    )


# --- activités ---

# route de la page de recensement des types d'activités
@app.route("/activites", methods=['GET', 'POST'])
def activites():
    """
    Cette route crée une page de sommaire des activités
    """
    liste_activites = []

    for activite in Activites.query.all():
        act = dict(
            id_activite=str(activite.id_activite),
            type_activite=str(activite.type_activite)
        )
        liste_activites.append(act)

    return render_template('pages/activite_sommaire.html', activites=liste_activites)


@app.route("/activites/<string:activite_choisie>", methods=['GET', 'POST'])
def detail_activite(activite_choisie):
    """
    Route pour afficher le détail d'une activité choisie
    """
    # Vérification de l'ID pour éviter injection
    liste_verif = [act.id_activite for act in Activites.query.all()]
    if activite_choisie not in liste_verif:
        return redirect(url_for('erreur_404'))

    # Récupération de l'activité
    activite = Activites.query.get(activite_choisie)

    # Récupération des séances liées
    seances = Seances.query.filter_by(id_activite=activite_choisie).all()

        # Requete 1 : Informations générales activités
    if activite_choisie == 'ALL' : 
        resultats = Activites.query.all()
    else:
        resultats = Activites.query.filter(Activites.id_activite == activite_choisie).first()
    # Requête 2 : Présence du type d'activités par expo
    # On part de la table Séances pour lier expositions et activités
    if activite_choisie == 'ALL':
        activites_expo = Seances.query.\
        select_from(Seances).\
        join(Activites, Seances.id_activite == Activites.id_activite).\
        join(Expositions, Seances.id_exposition == Expositions.id_exposition).\
        with_entities(Expositions.nom_exposition, Activites.type_activite,
            db.func.count(Seances.id_seance).label('nb_activites')).\
        group_by(Expositions.nom_exposition).\
        order_by(Activites.type_activite).all()
    else:
        activites_expo = Seances.query.\
        select_from(Seances).\
        join(Activites, Seances.id_activite == Activites.id_activite).\
        join(Expositions, Seances.id_exposition == Expositions.id_exposition).\
        with_entities(Expositions.nom_exposition, Activites.type_activite,
            db.func.count(Seances.id_seance).label('nb_activites')).\
        filter(Seances.id_activite == activite_choisie).\
        group_by(Expositions.nom_exposition, Activites.type_activite).\
        order_by(db.func.count(Seances.id_seance).desc()) # compteur pour le nombre de séances
    # Graphique 1 : données pour Chart.js
    labels_expo = []
    data_expo = []
    # on parcours activites_expo et on ajoute titre de l'expo et les activités associées
    for a in activites_expo:
        if a.nb_activites is not None: #enlever les valeurs nulles
            labels_expo.append(a.nom_exposition)
            data_expo.append(a.nb_activites)
    # Requête 3 : Nombre d'occurences du type d'activités par séance dans le temps
    if activite_choisie == 'ALL': 
        activites_seances = Seances.query.select_from(Seances).\
        join(Activites, Seances.id_activite == Activites.id_activite).\
        with_entities(Seances.date_seance, Activites.type_activite).\
        order_by(Seances.date_seance).all()
    else:
        # requête permettant de conditionner les séances selon l'activité choisie
        activites_seances = Seances.query.select_from(Seances).\
        join(Activites, Seances.id_activite == Activites.id_activite).\
        filter(Seances.id_activite == activite_choisie).\
        with_entities(Seances.date_seance, Activites.type_activite).\
        order_by(Seances.date_seance).all()
    frequentation_activites = {} # initialisation d'un dictionnaire vide
    # On compte le nombre de séances par date/activité
    c = Counter(
        (seance.date_seance, seance.type_activite)
        for seance in activites_seances
    )
    # mise en forme du compteur en dictionnaire
    frequentation_activites = [
        {
            "date": date,
            "type_activite": type_act,
            "compte": count
        }
        for (date, type_act), count in c.items()
    ]
    # Graphique 2 : données pour Chart.js
    labels_activites = []
    data_seances = []
    
    # on parcours frequentation_activites et on ajoute date et total de l'activité
    for a in frequentation_activites:
        labels_activites.append(a["date"].strftime("%Y-%m-%d")) #date au format ann-mois-jr
        data_seances.append(a["compte"])

    return render_template(
        'pages/une_activite.html',
        donnees=activite,
        seances=seances,
        activites_expo=activites_expo,
        labels_expo=labels_expo,
        data_expo=data_expo,
        activites_seances=activites_seances,
        frequentation_activites=frequentation_activites,
        labels_activites=labels_activites,                         
        data_seances=data_seances  
    )

# --- publics ---

# route de la page de recensement des types de publics

@app.route("/publics")
def publics():
    """
    Sommaire des publics : liste tous les types valides.
    """
    # on filtre pour ne garder que les types de publics non None
    liste_publics = [
        {"type_public": p.type_public} 
        for p in Publics.query.all() 
        if p.type_public
    ]

    return render_template(
        "pages/publics.html",
        liste_publics=liste_publics,
        sous_titre="Tous les types de publics du MAD"
    )

#  route de la page d'un type de public en particulier 
#               -- avec les graphiques --

@app.route("/publics/<string:type_public_choisi>")
def public(type_public_choisi):
    
    """
    Page d'un type de public spécifique
    """

    #  Vérification anti-injection 
    liste_verif = [pub.type_public for pub in Publics.query.all() if pub.type_public]
    liste_verif.append("ALL")  # autoriser le cas "tous les publics"
    if type_public_choisi not in liste_verif:
        return redirect(url_for('erreur_404'))

    # Récupération des données du public
    resultats = Publics.query.filter(Publics.type_public == type_public_choisi).first()

    #  Répartition du public par exposition (barres)

    if type_public_choisi == "ALL":
    # tous les publics : on récupère id_exposition et type_public
        public_expos = Publics.query.select_from(Publics)\
        .join(Seances, Publics.seance_publics)\
        .join(Expositions, Seances.id_exposition == Expositions.id_exposition)\
        .with_entities(Expositions.nom_exposition).all()
    else:
    
        public_expos = Publics.query.select_from(Publics)\
            .join(Seances, Publics.seance_publics)\
            .join(Expositions, Seances.id_exposition == Expositions.id_exposition)\
            .filter(Publics.type_public == type_public_choisi)\
            .with_entities(Expositions.nom_exposition).all()

        #Graph barres
    c = Counter(public_expos)
    iter_k = iter(c.keys()) # iter() permet d'itérer sur une série, ici les clefs de c
    iter_v = iter(c.values()) # et là les valeurs de c

    type_expos = []
    for _ in c: # création d'un dictionnaire via boucle for
        type_expos.append({
            "expo": str(next(iter_k))[2:-3],  # nettoyage des string
            "compte": next(iter_v)
        })

    # Occurrence public par date
    if type_public_choisi == "ALL": # si on veut regarder toutes les séances
        seance_par_public = Seances.query.select_from(Seances)\
            .join(Publics, Seances.seance_publics)\
            .with_entities(Seances.date_seance, func.count(Publics.id_public))\
            .group_by(Seances.date_seance)\
            .order_by(Seances.date_seance).all()
    else:
        seance_par_public = Seances.query.select_from(Seances)\
            .join(Publics, Seances.seance_publics)\
            .filter(Publics.type_public == type_public_choisi)\
            .with_entities(Seances.date_seance, func.count(Publics.id_public))\
            .group_by(Seances.date_seance)\
            .order_by(Seances.date_seance).all()

        # Graph
    public_par_date = [{"date": ds.strftime("%Y-%m-%d"), "places": count} for ds, count in seance_par_public]

    # Répartition champ social / handicap
    if type_public_choisi == "ALL":
        csh_query = Seances.query.select_from(Publics)\
            .join(Seances, Publics.seance_publics)\
            .join(Groupes, Seances.seance_groupes)\
            .with_entities(Groupes.type_client).all()
    else:
        csh_query = Seances.query.select_from(Publics)\
            .join(Seances, Publics.seance_publics)\
            .join(Groupes, Seances.seance_groupes)\
            .filter(Publics.type_public == type_public_choisi)\
            .with_entities(Groupes.type_client).all()

    csh_data = [g.type_client for g in csh_query if g.type_client]

    # Camembert
    csh_counter = Counter(csh_data)
    info_csh = {
        "CAS": csh_counter.get("Centre d'action sociale", 0),
        "SMSA": csh_counter.get("Structure médico-sociale adulte", 0),
        "AUTRE": sum(v for k, v in csh_counter.items() if k not in ["Centre d'action sociale", "Structure médico-sociale adulte"])
    }

    # --- Rendu du template ---
    return render_template(
        "pages/un_public.html",
        sous_titre=type_public_choisi,
        resultats=resultats,
        type_expos=type_expos,
        public_par_date=public_par_date,
        info_csh=info_csh
    )

# --- séances ---

# route de la page de recensement des séances
@app.route("/seances")
@app.route("/seances/<int:page>", methods=['GET', 'POST'])
def seances(page=1):

    return render_template("pages/seances.html", 
    donnees= Seances.query.order_by(Seances.date_seance).paginate(page=page, per_page=10),
    sous_titre="Tous les séances du MAD")

# route de la page d'une séance en particulier
@app.route("/seances/<string:id_seance>")
def seance(id_seance):

    # 1. ensemble de requêtes permettant de constituer le profil de la séance
    resultats = Seances.query.filter(Seances.id_seance == id_seance).first() # recherche dans Séances de la séance correspondant à l'ID en URL
    expo = Expositions.query.filter(Expositions.id_exposition == resultats.id_exposition).with_entities(Expositions.nom_exposition).first() # recherche du nom de l'exposition
    activite = Activites.query.filter(Activites.id_activite == resultats.id_activite).with_entities(Activites.type_activite).first() # recherche du type d'activité

    # regroupement des informations individuelles dans un dictionnaire
    info_seance = dict(
        id = resultats.id_seance,
        id_expo = resultats.id_exposition,
        date = resultats.date_seance,
        debut = resultats.heure_debut,
        fin = resultats.heure_fin,
        expo = expo.nom_exposition,
        id_activite = resultats.id_activite,
        activite = activite.type_activite
    )

    # la recherche des types de publics est plus complexe car il s'agit d'une relation many-to-many, on crée donc une liste
    type_publics = [] # initialisation de la liste vide

    # 2.requête permettant de récupérer les informations correspondantes dans la table Publics par une jointure
    publics = Seances.query.select_from(Seances).join(Publics, Seances.seance_publics).\
        filter(Seances.id_seance == id_seance).with_entities(Publics.type_public).\
        distinct(Publics.type_public).\
        all()

    # boucle for permettant d'intégrer les résultats à la liste 'type_publics'
    for public in publics:
        type_public = public.type_public
        type_publics.append(type_public)

    # 3. requête permettant d'obtenir les informations de groupe
    groupe = Seances.query.select_from(Seances).join(Groupes, Seances.seance_groupes).\
        filter(Seances.id_seance == id_seance).\
        with_entities(Groupes.id_groupe, Groupes.nom_client, Groupes.nature_client, Groupes.type_client, Groupes.ville, Groupes.langue).first()

    return render_template("pages/seance.html",
    sous_titre=id_seance,
    type_publics=type_publics,
    groupe=groupe,
    donnees=info_seance)

# ----- routes liées à la recherche -----

# route de la recherche rapide

@app.route("/recherche_rapide")
@app.route("/recherche_rapide/<int:page>")
def recherche_rapide(page=1):
    chaine = request.args.get("chaine", None)

    try:
        if chaine:
            # Expositions
            resultats_expo = Expositions.query.filter(
                or_(
                    Expositions.nom_exposition.ilike(f"%{chaine}%"), # ilike rend insensible à la casse
                    cast(Expositions.id_exposition, String).ilike(f"%{chaine}%") # String transforme les valeurs en chaîne de caractère (nécessaire car certains id_* sont Integer => renvoie un bug)
                )
            ).order_by(Expositions.nom_exposition).all()

            # Activités
            resultats_activites = Activites.query.filter(
                or_(
                    Activites.type_activite.ilike(f"%{chaine}%"),
                    cast(Activites.id_activite, String).ilike(f"%{chaine}%")
                )
            ).order_by(Activites.type_activite).all()

            # Publics
            resultats_publics = Publics.query.filter(
                or_(
                    Publics.type_public.ilike(f"%{chaine}%"),
                    cast(Publics.id_public, String).ilike(f"%{chaine}%")
                )
            ).order_by(Publics.type_public).all()
        else:
            resultats_expo = []
            resultats_activites = []
            resultats_publics = []

        return render_template(
            "pages/resultats_recherche_rapide.html",
            sous_titre=f"Recherche | {chaine}" if chaine else "Recherche vide",
            resultats_expo=resultats_expo,
            resultats_activites=resultats_activites,
            resultats_publics=resultats_publics,
            requete=chaine
        )

    except Exception as e:
        print(e)
        return render_template("erreurs/500.html")
    

# route de la page de recherche avancée

@app.route("/recherche", methods=["GET", "POST"])
@app.route("/recherche/<int:page>", methods=["GET", "POST"])
def recherche(page=1):

    form = Recherche()
    donnees = None

    try:
        #  noms EXACTS du formulaire
        id_seance = request.values.get("id_seance")
        nom_exposition = request.values.get("exposition")
        type_activite = request.values.get("activite")
        type_public = request.values.get("public")

        # nettoyage
        id_seance = id_seance.strip() if id_seance else None
        nom_exposition = nom_exposition.strip() if nom_exposition else None
        type_activite = type_activite.strip() if type_activite else None
        type_public = type_public.strip() if type_public else None

        # lancer recherche seulement si filtre
        if id_seance or nom_exposition or type_activite or type_public:

            query = Seances.query

            if id_seance:
                query = query.filter(
                    Seances.id_seance.ilike(f"%{id_seance}%")
                )

            if nom_exposition:
                query = query.join(Seances.expositions).filter(
                    Expositions.nom_exposition.ilike(f"%{nom_exposition}%")
                )

            if type_activite:
                query = query.join(Seances.activites).filter(
                    Activites.type_activite.ilike(f"%{type_activite}%")
                )

            if type_public:
                query = query.join(Seances.seance_publics).filter(
                    Publics.type_public.ilike(f"%{type_public}%")
                )

            donnees = query.order_by(Seances.id_seance).paginate(
                page=page,
                per_page=app.config["RESULTATS_PAR_PAGE"],
                error_out=False
            )

        # pré-remplissage CORRECT
        form.id_seance.data = id_seance
        form.exposition.data = nom_exposition
        form.activite.data = type_activite
        form.public.data = type_public

    except Exception as e:
        print("Erreur recherche :", e)

    return render_template(
        "pages/resultats_recherche.html",
        donnees=donnees,
        form=form
    )

# --- exports csv ---

# expositions
@app.route("/export/expositions")
def export_expositions_csv(): # Requête SQL : on séléctionne les données voulues
    donnees = db.session.query(
        Expositions.nom_exposition,
        Seances.date_seance,
        Seances.heure_debut,
        Seances.heure_fin,
        Publics.type_public
    ).join(Seances, Seances.id_exposition == Expositions.id_exposition).join(Seances.seance_publics)\
        .group_by(
        Expositions.nom_exposition,
        Seances.date_seance,
        Seances.heure_debut,
        Seances.heure_fin,
        Publics.type_public
    ).order_by(
        Expositions.nom_exposition,
        Seances.date_seance,
        Seances.heure_debut
    ).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";") # Tabulation

    writer.writerow([
        "nom_exposition",
        "date_seance",
        "heure_debut",
        "heure_fin",
        "type_public"
    ])

    for row in donnees:
        writer.writerow([
            row.nom_exposition,
            row.date_seance,
            row.heure_debut,
            row.heure_fin,
            row.type_public
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=expositions.csv" # Défini non du csv lors du téléchargement
        }
    )

# activites

@app.route("/export/activites")
def export_activites_csv():
    donnees = db.session.query(
        Expositions.nom_exposition,
        Activites.type_activite,
        Seances.date_seance,
        Seances.heure_debut,
        Seances.heure_fin
    ).join(Seances, Seances.id_activite == Activites.id_activite).join(Expositions, Seances.id_exposition == Expositions.id_exposition)\
    .group_by(
        Expositions.nom_exposition,
        Activites.type_activite,
        Seances.date_seance,
        Seances.heure_debut,
        Seances.heure_fin
    ).order_by(
        Expositions.nom_exposition,
        Activites.type_activite,
        Seances.date_seance,
        Seances.heure_debut
    ).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "nom_exposition",
        "type_activite",
        "date_seance",
        "heure_debut",
        "heure_fin"
    ])

    for row in donnees:
        writer.writerow([
            row.nom_exposition,
            row.type_activite,
            row.date_seance,
            row.heure_debut,
            row.heure_fin
            ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=activites.csv"}
    )
