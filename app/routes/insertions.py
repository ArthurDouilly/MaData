from ..app import app, db
from flask import render_template, request, flash
from ..models.madata import *
from ..models.formulaires import Insertion_seance, Insertion_exposition, Insertion_activite
from ..utils.transformations import  clean_arg

# route d'insertion des séances

@app.route("/insertions/seance", methods=['GET', 'POST'])
def insertion_seance():
    '''
    Route spéciale servant à insérer une séance dans la base de données
    '''
    form = Insertion_seance() # appel du formulaire si la méthode est GET

    try: # try/except afin d'attraper les erreurs
        if form.validate_on_submit(): # permet de lancer le code si l'utilisateur renvoie un formulaire
            id_seance =  clean_arg(request.form.get("id_seance", None)) # on spécifie la valeur attendue en retour, soit correspondante à la méthode de la classe Insertion_seance, soit None
            id_exposition =  clean_arg(request.form.get("id_exposition", None))
            id_activite =  clean_arg(request.form.get("id_activite", None))
            langue_seance =  clean_arg(request.form.get("langue_seance", None))
            date_seance =  clean_arg(request.form.getlist("date_seance", None))
            heure_debut =  clean_arg(request.form.get("heure_debut", None))
            heure_fin =  clean_arg(request.form.get("heure_fin", None))
            nature_seance =  clean_arg(request.form.get("nature_seance", None))

            # création d'une variable rassemblant tous les éléments renseignés avec l'instanciation d'un objet Seances
            nouvelle_seance = Seances(id_seance=id_seance,
                langue_seance=langue_seance,
                date_seance=date_seance,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                nature_seance=nature_seance
                )

            # les valeurs issues de clés étrangères sont liées aux valeurs correspondantes dans les tables liées, Activités et Expositions
            nouvelle_seance.activites.append(Activites.query.filter(Activites.id_activite == id_activite).first())
            nouvelle_seance.expositions.append(Expositions.query.filter(Expositions.id_exposition == id_exposition).first())
            
            # add() et commit() permettent de rajouter les informations de nouvelle_seance à la base de données
            db.session.add(nouvelle_seance)
            db.session.commit()

            flash("L'insertion de la séance n°"+ id_seance + " s'est correctement déroulée", 'info') # message flash d'information indiquant la réussite de l'insertion à l'utilisateur
    
    except Exception as e : # récupération du message d'erreur
        flash("Une erreur s'est produite lors de l'insertion de la séance n°" + id_seance + " : " + str(e), "error") # message flash d'erreur indiquant l'échec de l'insertion
        db.session.rollback()
    
    # dans les deux cas, on retourne la page actuelle
    return render_template("pages/insertion_seance.html", 
            sous_titre= "Insertion d'une nouvelle séance", 
            form=form)

# route d'insertion des expositions

@app.route("/insertions/exposition", methods=['GET', 'POST'])
def insertion_exposition():
    '''
    Route servant à créer une exposition par le biais d'un formulaire
    '''
    form = Insertion_exposition()

    try:
        if form.validate_on_submit():
            id_exposition =  clean_arg(request.form.get("id_exposition", None)) # on spécifie la valeur attendue en retour, soit correspondante à la méthode de la classe Insertion_seance, soit None
            nom_exposition =  clean_arg(request.form.get("nom_exposition", None))

            # création de l'objet nouvelle_exposition dans la classe Expositions
            nouvelle_exposition = Expositions(
                id_exposition=id_exposition,
                nom_exposition=nom_exposition
            )

            # add() et commit() permettent de rajouter les informations de nouvelle_seance à la base de données
            db.session.add(nouvelle_exposition)
            db.session.commit()

            flash("L'insertion de l'exposition "+ nom_exposition + " s'est correctement déroulée", 'info') # message flash d'information indiquant la réussite de l'insertion à l'utilisateur

    except Exception as e :
        flash("Une erreur s'est produite lors de l'insertion de l'exposition " + nom_exposition + " : " + str(e), "error") # message flash d'erreur indiquant l'échec de l'insertion
        db.session.rollback()

    # dans les deux cas, on retourne la page actuelle
    return render_template("pages/insertion_exposition.html", 
            sous_titre= "Insertion d'une nouvelle exposition", 
            form=form)

# route d'insertion des activités

@app.route("/insertions/activité", methods=['GET', 'POST'])
def insertion_activite():
    '''
    Route servant à créer une activité par le biais d'un formulaire
    '''
    form = Insertion_activite()

    try:
        if form.validate_on_submit():
            id_activite =  clean_arg(request.form.get("id_activite", None)) # on spécifie la valeur attendue en retour, soit correspondante à la méthode de la classe Insertion_activite, soit None
            type_activite =  clean_arg(request.form.get("type_activite", None))

            # création de l'objet nouvelle_activite dans la classe Activites
            nouvelle_activite = Activites(
                id_activite=id_activite,
                type_activite=type_activite
            )

            # add() et commit() permettent de rajouter les informations de nouvelle_seance à la base de données
            db.session.add(nouvelle_activite)
            db.session.commit()

            flash("L'insertion de l'activite "+ type_activite + " s'est correctement déroulée", 'info') # message flash d'information indiquant la réussite de l'insertion à l'utilisateur

    except Exception as e :
        flash("Une erreur s'est produite lors de l'insertion de l'activité" + type_activite + " : " + str(e), "error") # message flash d'erreur indiquant l'échec de l'insertion
        db.session.rollback()

    # dans les deux cas, on retourne la page actuelle
    return render_template("pages/insertion_activite.html", 
            sous_titre= "Insertion d'une nouvelle activite", 
            form=form)