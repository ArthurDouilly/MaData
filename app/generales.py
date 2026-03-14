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
    return "WIP"

# route de la page /about

@app.route("/home/about")
def about():
    return render_template("pages/about.html")

# --- routes liées à une catégorie de données ---

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

# --- expositions ---

# route de la page d'une exposition en particulier

@app.route("/expositions/<string:expo>")
def exposition(expo):
    ###
    return render_template("pages/expo.html", expo=nom) ###)

# --- activités ---

# route de la page de recensement des types d'activités

# route de la page d'un type d'activité en particulier

# --- publics ---

# route de la page de recensement des types de publics

# route de la page d'un type de public en particulier

# --- séances ---

# route de la page de recensement des séances

# route de la page d'une séance en particulier

# ----- routes liées à la recherche -----

# route de la page de recherche avancée

# route des résultats de la barre de recherche (pagination)