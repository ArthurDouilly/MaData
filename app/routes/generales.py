'''
Fichier regroupant les routes générales, càd les routes vers les pages principales de l'application web.
'''

# ----- importation des modules python -----

from ..app import app, db
from ..models.madata import *
from sqlalchemy import Function
from flask import render_template, redirect, url_for
from collections import Counter

# ----- création des routes -----

# --- routes générales ---

# routes de la page d'accueil

@app.route("/") # redirige immédiatement sur la page /index ci-dessous
def home():
    return redirect(url_for("index")) # redirect(url_for) permet de faire la redirection

@app.route("/accueil") # page d'accueil du site
def index():
    return render_template("pages/index.html") # on utilise ici simplement un render_template

# route d'erreur
@app.route("/erreur") # page d'erreur
@app.route("/erreur/404") # page de l'erreur 404
def erreur_404():

    return render_template("erreurs/404.html")

@app.route("/test")
def about():
    donnees = []
    id_expo='OUR'
    data =  frequentation_publics_expo = Seances.query.select_from(Seances).\
        join(Publics, Seances.seances_publics).\
        filter(Seances.id_exposition == id_expo).all()
    print(data)
    return "si vous lisez ceci, c'est que ça marche ! (regardez le terminal pour voir si ça print correctement)"
    # return render_template("pages/about.html")

# ----- routes liées à une catégorie de données -----

# --- expositions ---

@app.route("/test/expositions/<string:exposition_choisie>")
def test_exposition(exposition_choisie):
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

    frequentation_journée = {} # initialisation du dictionnaire vide

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
            filter(Expositions.id_exposition == exposition_choisie).\
            group_by(Seances.date_seance,Capacite.places_vendues).\
            order_by(Seances.date_seance).all()

    for frequentation in frequentations: # boucle de traitement des valeurs récupérées pour ajout dans le dictionnaire
        if frequentation.date_seance in frequentation_journée: # si la clé[date] existe dans le dictionnaire
            if frequentation.places_vendues == None: # remplacement du None par un zéro
                frequentation_journée[frequentation.date_seance] = [0]
            else:
                frequentation_journée[frequentation.date_seance].append(frequentation.places_vendues)
        else: # si la clé n'existe pas, on crée la clé avant de boucler de nouveau
            if frequentation.places_vendues == None: # remplacement du None par un zéro
                frequentation_journée[frequentation.date_seance] = [0]
            else:
                frequentation_journée[frequentation.date_seance] = [frequentation.places_vendues]

    # print(frequentation_journée)

    # il faudrait voir s'il est utile d'aller plus loin ici, j'ai essayé de voir pour faire la somme par jour mais c'est compliqué

    # requête 3 : les informations d'entrée du graphique fréquentation/public

    if exposition_choisie == 'ALL' : # si on veut regarder toutes les expositions
        expo_publics = Publics.query.all()
    else:
        # requête devant permettre de conditionner les groupes selon l'exposition
        expo_publics = Seances.query.select_from(Seances).\
            join(Publics, Seances.seances_publics).\
            filter(Seances.id_exposition == exposition_choisie).\
            with_entities(Publics.type_public).all()

    frequentation_publics = Counter(expo_publics)

    print(frequentation_publics)

    # requête 4 : récupération des détails des visiteurs

    if exposition_choisie == 'ALL' : # si on veut regarder toutes les expositions
            # requête permettant de récupérer directement les informations depuis Groupes
            visiteurs = Groupes.query.with_entities(Groupes.id_groupe,Groupes.ville,Groupes.type_client).\
            order_by(Groupes.id_groupe).all()
    else :
        # requête devant permettre de conditionner les groupes selon l'exposition
        visiteurs = Seances.query.select_from(Seances).\
            join(Groupes, Seances.seances_groupes).\
            with_entities(Groupes.id_groupe,Groupes.ville,Groupes.type_client).\
            filter(Seances.id_exposition == exposition_choisie).\
            order_by(Groupes.id_groupe).all()

    return render_template("pages/une_exposition.html", exposition_choisie=exposition_choisie,
        resultats=resultats,
        frequentation_journée=frequentation_journée,
        frequentation_publics=frequentation_publics,
        visiteurs=visiteurs,
        sous_titre="Toutes les expositions du MAD"
    )

# route de la page de recensement des expositions

@app.route("/expositions")
def expositions():
    '''
    Le but de cette route est de rendre un ensemble d'informations devant servir d'entrée aux graphiques générés pour les expositions
    '''
    # requête 1 : toutes les expositions renseignées dans la table 'Expositions'
    resultats = Expositions.query.all()

    # requête 2 : les informations d'entrée du graphique fréquentation/jour
    frequentation_journée = {} # initialisation du dictionnaire vide

    # requête avec jointure entre Capacité et Séances, sélectionnant les places vendues et la date
    frequentations = Capacite.query.\
        select_from(Capacite).\
        with_entities(Capacite.places_vendues, Seances.date_seance).\
        join(Capacite.seances_capacite).\
        group_by(Seances.date_seance,Capacite.places_vendues).\
        order_by(Seances.date_seance).all()

    for frequentation in frequentations: # boucle de traitement des valeurs récupérées pour ajout dans le dictionnaire
        if frequentation.date_seance in frequentation_journée: # si la clé[date] existe dans le dictionnaire
            if frequentation.places_vendues == None: # remplacement du None par un zéro
                frequentation_journée[frequentation.date_seance] = [0]
            else:
                frequentation_journée[frequentation.date_seance].append(frequentation.places_vendues)
        else: # si la clé n'existe pas, on crée la clé avant de boucler de nouveau
            if frequentation.places_vendues == None: # remplacement du None par un zéro
                frequentation_journée[frequentation.date_seance] = [0]
            else:
                frequentation_journée[frequentation.date_seance] = [frequentation.places_vendues]

    # il faudrait voir s'il est utile d'aller plus loin ici, j'ai essayé de voir pour faire la somme par jour mais c'est compliqué

    # requête 3 : les informations d'entrée du graphique fréquentation/public
    frequentation_publics = Publics.query.all()

    print(frequentation_publics)

    # WIP - requête devant permettre de conditionner les groupes selon l'exposition
    # frequentation_publics_expo = Seances.query.select_from(Seances).join(Publics, Seances.seances_publics).\
    #     filter(Seances.id_exposition == id_expo).all()

    # requête 4 : récupération des détails des visiteurs

    #exposition_choisie = 'OUR' # il faudrait que cette valeur change selon la sélection de l'utilisateur

    if exposition_choisie == 'all' : # si on veut regarder toutes les expositions
            # requête permettant de récupérer directement les informations depuis Groupes
            visiteurs = Groupes.query.with_entities(Groupes.id_groupe,Groupes.ville,Groupes.type_client).\
            order_by(Groupes.id_groupe).all()
    else :
        # requête devant permettre de conditionner les groupes selon l'exposition (pour le moment, seances_groupes ne marche pas)
        visiteurs = Seances.query.select_from(Seances).\
            join(Groupes, Seances.seances_groupes).\
            with_entities(Groupes.id_groupe,Groupes.ville,Groupes.type_client).\
            filter(Seances.id_exposition == exposition_choisie).\
            order_by(Groupes.id_groupe).all()

    return render_template("pages/expositions.html", resultats=resultats, frequentation_journée=frequentation_journée, frequentation_publics=frequentation_publics, visiteurs=visiteurs, sous_titre="Toutes les expositions du MAD")

# route de la page d'une exposition en particulier

# @app.route("/expositions/<string:nom_exposition>") # route contenant le nom d'exposition en variable
# def exposition(nom_exposition):
#     '''
#     'exposition' permet de récupérer les informations d'une exposition définie en entrée pour les réemployer
#     '''

#     # requête 1 : recherche de l'exposition indiquée en URL
#     requete = Expositions.query.filter(Expositions.nom_exposition == nom_exposition).first()
#     id_expo = requete.id_exposition # récupération de l'ID de l'exposition

#     # requête 2 : recherche des informations des séances liées à l'exposition choisie
#     seances_dans_expo = [] # initiation d'une liste vide

#     seances = Seances.query.filter(Seances.id_exposition == id_expo).all() # requête des séances ayant id_expo en identifiant d'exposition
    
#     for seance in seances: # boucle for permettant de sélectionner les informations utiles
#         seance_info = dict( # dict permet de créer un dictionnaire
#             id = seance.id_seance,
#             date = seance.date_seance,
#             heure_debut = seance.heure_debut,
#             heure_fin = seance.heure_fin
#         )
#         seances_dans_expo.append(seance_info) # ajout du dictionnaire créé dans la liste créée plus haut

#     return render_template("pages/une_exposition.html",
#     sous_titre=nom_exposition,
#     donnees=requete, seances=seances_dans_expo) # construction de la page dynamique avec les informations d'entrée

# --- activités ---

# route de la page de recensement des types d'activités
@app.route("/activites")
def activites():
    resultats = Activites.query.all()
    donnees = []
    for activite in resultats:
        donnees.append({
            "nom": activites.types_activites
        })
    return render_template("pages/activites.html", donnees=donnees, resultats=resultats, sous_titre="Toutes les activités du MAD")

# route de la page d'un type d'activité en particulier
@app.route("/activites/<string:nom_activite>")
def activite(nom_activite):
    return render_template("pages/une_activite.html",
    sous_titre=nom_activite,
    donnees=Activites.query.filter(Activites.nom_activite == nom_activite).first())

# --- publics ---

# route de la page de recensement des types de publics
@app.route("/publics")
def publics():
    resultats = Publics.query.all()
    donnees = []
    for public in resultats:
        donnees.append({
            "nom": publics.types_public
        })
    return render_template("pages/publics.html", donnees=donnees, resultats=resultats, sous_titre="Tous les types de publics du MAD")

# route de la page d'un type de public en particulier
@app.route("/publics/<string:type_public>")
def public(type_public):
    return render_template("pages/un_public.html",
    sous_titre=type_public,
    donnees=Publics.query.filter(Publics.type_public == type_public).first())

# --- séances ---

# route de la page de recensement des séances
@app.route("/seances")
def seances():
    resultats = Seances.query.all()
    donnees = []
    for seance in resultats:
        donnees.append({
            "nom": seances.nom_seance
        })
    return render_template("pages/seances.html", donnees=donnees, resultats=resultats, sous_titre="Tous les séances du MAD")

# route de la page d'une séance en particulier
@app.route("/seances/<string:id_seance>")
def seance(id_seance):
    return render_template("pages/une_seance.html",
    sous_titre=id_seance,
    donnees=Seances.query.filter(Seances.id_seance == id_seance).first())

# ----- routes liées à la recherche -----

# route de la recherche rapide
@app.route("/recherche_rapide")
@app.route("/recherche_rapide/<int:page>")
def recherche_rapide(page=1):
    chaine = request.args.get("chaine", None)
    
    # Je ne suis pas très sûre de la requête sql... j'ai repris la structure du prof mais je ne suis pas sûre que ça soit pertinent de fou
        # J'ai mis un inner join entre Seances et Expositions et un left join vers seances_publics et seances_activites
    if chaine:
        resultats = Seances.query.\
            join(Expositions, Seances.id_exposition == Expositions.id_exposition).\
            leftjoin(Seances.seances_publics).\
            leftjoin(Seances.seances_activites).\
            filter(
                or_(
                    Seances.id_seance.ilike("%"+chaine+"%"),
                    Expositions.nom_exposition.ilike("%"+chaine+"%"),
                    Publics.type_public.ilike("%"+chaine+"%"),
                    Activites.nom_activite.ilike("%"+chaine+"%")
                )
            ).\
            distinct(Seances.id_seance).\
            order_by(Seances.id_seance).\
            paginate(page=page, per_page=app.config["RESULTS_PER_PAGE"])
    else:
        resultats = None
        
    return render_template("pages/resultats_recherche.html", 
            sous_titre= "Recherche | " + chaine, 
            donnees=resultats,
            requete=chaine)

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

                if id_seance:
                    query_results = query_results.filter(Seances.name.ilike("%"+id_seance.lower()+"%"))
                
                '''
                if nom_exposition:
                    resource = db.session.execute("""select a.id from country a 
                        inner join country_resources b on b.id = a.id and b.resource  == '"""+ressource+"""'
                        """).fetchall() # à changer, il y a du dur ici !
                    query_results = query_results.filter(Country.id.in_([r.id for r in resource] ))
                
                if type_activite:
                    
                    # chemin : Seances -> Activites
                
                if type_public:
                    # chemin : Seances -> seances_publics -> Publics
                '''

                donnees = query_results.order_by(Seances.id_seance).paginate(page=page, per_page=app.config["RESULTS_PER_PAGE"]) # RESULTS_PER_PAGE à configurer !

                # renvoi des filtres de recherche pour préremplissage du formulaire
                form.nom_pays.data = nom_pays
                form.continents.data = continent
                form.ressources.data = ressource
            flash("La recherche a été effectuée avec succès", "info")
    except Exception as e:
        flash("La recherche a rencontré une erreur "+ str(e), "info")

    return render_template("pages/resultats_recherche.html", 
            sous_titre= "Recherche" , 
            donnees=donnees,
            form=form)