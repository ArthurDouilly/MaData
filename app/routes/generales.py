'''
Fichier regroupant les routes générales, càd les routes vers les pages principales de l'application web.
'''

# ----- importation des modules python -----

from ..app import app, db
from ..models.madata import *
from ..models.formulaires import Recherche
from sqlalchemy import Function, or_
from flask import request, render_template, redirect, url_for, Response
from collections import Counter
import io
import csv
from ..utils.transformations import nettoyage_string_to_int, clean_arg

# ----- création des routes -----

# --- routes générales ---

# routes de la page d'accueil

@app.route("/") # redirige immédiatement sur la page /index ci-dessous
def home():
    return redirect(url_for("index")) # redirect(url_for) permet de faire la redirection

@app.route("/accueil") # page d'accueil du site
def index():
    return render_template("pages/index.html") # on utilise ici simplement un render_template

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

    for exposition in Expositions.query.all(): # boucle créant les dictionnaires
        expo = dict(
            nom_expo = str(exposition.nom_exposition), # récupère les noms et les passe en str
            id_expo = str(exposition.id_exposition) # récupère les id et les passe en str
        )
        liste_expos.append(expo) # ajout des dictionnaires dans la liste

    return render_template('pages/expositions_sommaire.html',liste_expos=liste_expos)

# route des pages d'exposition

@app.route("/expositions/<string:exposition_choisie>")
def détail_exposition(exposition_choisie):
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

    # requête avec jointure entre Capacité et Séances, sélectionnant les places vendues et la date
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

    # il faudrait voir s'il est utile d'aller plus loin ici, j'ai essayé de voir pour faire la somme par jour mais c'est compliqué

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

    return render_template("pages/une_exposition.html", exposition_choisie=exposition_choisie,
        resultats=resultats,
        frequentation_journée=frequentation_journée,
        frequentation_publics=frequentation_publics,
        visiteurs=visiteurs,
        sous_titre="Détails des expositions du MAD"
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

    # Passe au template avec les bons noms
    return render_template(
        'pages/une_activite.html',
        donnees=activite,
        seances=seances
    )
# --- publics ---

# route de la page de recensement des types de publics
@app.route("/publics")
def publics():
    """
    Cette route crée une page de sommaire des activités
    """
    liste_publics = []

    for public in Publics.query.all():
        pub = dict(
            id_public=str(public.id_public),
            type_public=str(public.type_public)
        )
        liste_publics.append(pub)
    
    return render_template("pages/publics.html", liste_publics=liste_publics, sous_titre="Tous les types de publics du MAD")

# route de la page d'un type de public en particulier
@app.route("/publics/<string:type_public>")
def public(type_public):
    return render_template("pages/un_public.html",
    sous_titre=type_public,
    donnees=Publics.query.filter(Publics.type_public == type_public).first())

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
    chaine = request.args.get("chaine", None) # utilise la fonction request pour chercher dans la base de données
    
    try: # essaie de faire fonctionner la requête
        if chaine: # si la chaîne est remplie, effectue la requête ci-dessous

            # requête cherchant dans Expositions
            resultats_expo = Expositions.query.\
                filter(
                    or_(
                        Expositions.id_exposition.ilike("%"+chaine+"%"),
                        Expositions.nom_exposition.ilike("%"+chaine+"%")
                    )
                ).\
                distinct(Expositions.id_exposition, Expositions.nom_exposition).\
                order_by(Expositions.id_exposition).\
                paginate(page=page, per_page=app.config["RESULTATS_PAR_PAGE"])

        else: # si la chaîne est vide, pas de recherche
            resultats = None

        # dans les deux cas, renvoi vers la page des résultats de la recherche rapide
        return render_template("pages/resultats_recherche_rapide.html", 
        sous_titre= "Recherche | " + chaine, 
        resultats_expo=resultats_expo,
        requete=chaine)

    except Exception as e: # s'il y a une erreur interne, renvoi vers la page d'erreur
        print(e) # print de l'erreur dans le terminal

        return render_template("erreurs/500.html") # erreur 500 car il s'agit d'un problème lié au serveur

# route de la page de recherche avancée

@app.route("/recherche", methods=['GET', 'POST'])
@app.route("/recherche/<int:page>", methods=['GET', 'POST'])
def recherche(page=1):
    form = Recherche() 

    # initialisation des données de retour dans le cas où il n'y ait pas de requête
    donnees = []

    try:
        if form.validate_on_submit():
            # récupération des éventuels arguments de l'URL qui seraient le signe de l'envoi d'un formulaire
            id_seance =  clean_arg(request.form.get("id_seance", None))
            nom_exposition =  clean_arg(request.form.get("nom_exposition", None))
            type_activite =  clean_arg(request.form.get("type_activite", None))
            type_public =  clean_arg(request.form.get("type_public", None))

            # si l'un des champs de recherche a une valeur, alors cela veut dire que le formulaire a été rempli et qu'il faut lancer une recherche 
            # dans les données
            if id_seance or nom_exposition or type_activite or type_public:
                # initialisation de la recherche; en fonction de la présence ou nom d'un filtre côté utilisateur, nous effectuerons des filtres SQLAlchemy,
                # ce qui signifie que nous pouvons jouer ici plusieurs filtres d'affilée
                query_results = Seances.query

                if id_seance: # si le critère id_seance est rempli
                    query_results = query_results.filter(Seances.name.ilike("%"+id_seance.lower()+"%"))
                
                if nom_exposition: # si le critère nom_exposition est rempli
                    query_results = query_results.select_from(Seances).join(Expositions).\
                        filter(Expositions.nom_exposition.ilike("%"+nom_exposition.lower()+"%"))

                if type_activite: # si le critère type_activite est rempli
                    query_results = query_results.select_from(Seances).join(Activites).\
                        filter(Activites.type_activite.ilike("%"+type_activite.lower()+"%"))

                if type_public: # si le critère type_public est rempli
                    query_results = query_results.select_from(Seances).join(Publics, Seances.seance_publics).\
                        filter(Publics.type_public.ilike("%"+type_public.lower()+"%"))

                donnees = query_results.order_by(Seances.id_seance).paginate(page=page, per_page=app.config["RESULTATS_PAR_PAGE"])

                # renvoi des filtres de recherche pour préremplissage du formulaire
                form.id_seance.data = id_seance
                form.exposition.data = exposition
                form.activite.data = activite
                form.public.data = public
            # flash("La recherche a été effectuée avec succès", "info")
    except Exception as e:
        print(e)
        # flash("La recherche a rencontré une erreur "+ str(e), "info")

    return render_template("pages/resultats_recherche.html", 
            sous_titre= "Recherche" , 
            donnees=donnees,
            form=form)

# --- exports csv ---

# expositions
@app.route("/export/expositions")
def export_expositions_csv():
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
    writer = csv.writer(output, delimiter=";")

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
            "Content-Disposition": "attachment; filename=expositions.csv"
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