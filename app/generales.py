'''
Fichier regroupant les routes générales, càd les routes vers les pages principales de l'application web.
'''

# ----- importation des modules python -----

from ..app import app, db
from flask import render_template

# ----- création des routes -----

# --- routes générales ---

# route de la page d'accueil

@app.route("/home")
def home():
    return "pages/home est WIP"

# route de la page /about

@app.route("/home/about")
def about():
    return "pages/about est WIP"
    # return render_template("pages/about.html")

# ----- routes liées à une catégorie de données -----

# --- expositions ---

# route de la page de recensement des expositions

@app.route("/expositions")
def toutes_expositions():
    resultats = Expositions.query.all()
    donnees = []
    for exposition in resultats:
        donnees.append({
            "nom": expositions.nom_exposition
        })

return render_template("pages/toutes_expos.html", donnees=donnees, resultats=resultats, sous_titre="Toutes les expositions du MAD")

# route de la page d'une exposition en particulier

@app.route("/expositions/<string:expo>")
def exposition(expo):
    ### ... à réaliser
    return render_template("pages/expo.html", expo=nom) ###)

# --- activités ---

# route de la page de recensement des types d'activités
@app.route("/activites")
def toutes_activites():
    resultats = Activites.query.all()
    donnees = []
    for activite in resultats:
        donnees.append({
            "nom": activites.types_activites
        })

return render_template("pages/toutes_activites.html", donnees=donnees, resultats=resultats, sous_titre="Toutes les activités du MAD")

# route de la page d'un type d'activité en particulier
@app.route("/activites/<string:activite>")
def activite(activite):
    ### ... à réaliser
    return render_template("pages/activite.html", activite=nom)

# --- publics ---

# route de la page de recensement des types de publics
@app.route("/publics")
def tous_publics():
    resultats = Publics.query.all()
    donnees = []
    for public in resultats:
        donnees.append({
            "nom": publics.types_public
        })

return render_template("pages/tous_publics.html", donnees=donnees, resultats=resultats, sous_titre="Tous les types de publics du MAD")

# route de la page d'un type de public en particulier
@app.route("/publics/<string:public>")
def public(public):
    ### ... à réaliser
    return render_template("pages/public.html", public=nom)

# --- séances ---

# route de la page de recensement des séances
@app.route("/seances")
def toutes_seances():
    resultats = Seances.query.all()
    donnees = []
    for seance in resultats:
        donnees.append({
            "nom": seances.nom_seance
        })

return render_template("pages/toutes_seances.html", donnees=donnees, resultats=resultats, sous_titre="Tous les séances du MAD")

# route de la page d'une séance en particulier
@app.route("/seances/<string:seance>")
def seance(seance):
    ### ... à réaliser
    return render_template("pages/seance.html", seance=nom)

# ----- routes liées à la recherche -----

# route de la page de recherche avancée
@app.route("/recherche_avancee")
def recherche_avancee():
    return "La recherche avancée est WIP"

# route des résultats de la barre de recherche (pagination)
@app.route("/recherche/")
def résultats():
    return "La recherche est WIP"