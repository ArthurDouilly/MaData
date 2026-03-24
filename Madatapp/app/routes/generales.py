'''
Fichier regroupant les routes générales, càd les routes vers les pages principales de l'application web.
'''

# ----- importation des modules python -----

from ..app import app, db
from ..models.madata import *
from flask import render_template, redirect, url_for

# ----- création des routes -----

# --- routes générales ---

# routes de la page d'accueil

@app.route("/") # redirige immédiatement sur la page /index ci-dessous
def home():
return redirect(url_for("index")) # redirect(url_for) permet de faire la redirection

@app.route("/accueil") # page d'accueil du site
def index():
return render_template("pages/index.html") # on utilise ici simplement un render_template

# route de la page /about

@app.route("/test")
def about():
donnees = []
data = Activites.query.all()
print(data)
return "si vous lisez ceci, c'est que ça marche ! (regardez le terminal pour voir si ça print correctement)"
# return render_template("pages/about.html")

# ----- routes liées à une catégorie de données -----

# --- expositions ---

# route de la page de recensement des expositions

@app.route("/expositions")
def expositions():
resultats = Expositions.query.all()

return render_template(
"pages/expositions.html",
resultats=resultats,
sous_titre="Toutes les expositions du MAD"
)

# route de la page d'une exposition en particulier

@app.route("/expositions/<string:nom_exposition>") # route contenant le nom d'exposition en variable
def exposition(nom_exposition):
return render_template("pages/une_exposition.html",
sous_titre=nom_exposition,
donnees=Expositions.query.filter(Expositions.nom_exposition == nom_exposition).first())

# --- activités ---

# route de la page de recensement des types d'activités
@app.route("/activites")
def activites():
resultats = Activites.query.all()

return render_template(
"pages/activites.html",
resultats=resultats,
sous_titre="Toutes les activités du MAD"

)

# route de la page d'un type d'activité en particulier
@app.route("/activites/<string:nom_activite>")
def activite(nom_activite):
return render_template("pages/une_activite.html",
sous_titre="nom_activite",
donnees=Activites.query.filter(Activites.nom_activite == nom_activite).first())

# --- publics ---

# route de la page de recensement des types de publics
@app.route("/publics")
def publics():
resultats = Publics.query.all()
return render_template(
"pages/publics.html",
resultats=resultats,
sous_titre="Tous les types de publics du MAD"
)

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

### à réaliser !
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
id_seance = clean_arg(request.form.get("id_seance", None))
nom_exposition = clean_arg(request.form.get("nom_exposition", None))
type_activite = clean_arg(request.form.get("type_activite", None))
type_public = clean_arg(request.form.get("type_public", None))

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
inner join country_resources b on b.id = a.id and b.resource == '"""+ressource+"""'
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
