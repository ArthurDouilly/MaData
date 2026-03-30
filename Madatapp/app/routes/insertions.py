from ..app import app, db
from flask import render_template, request, flash
from ..models.madata import *
from ..models.formulaires import Insertion_seance
from ..utils.transformations import  clean_arg

@app.route("/ajout")
def ajout():
    '''
    Page par défaut recensant les pages d'insertions et de suppressions de séances
    '''
    return render_template("pages/ajout.html")

@app.route("/ajout/insertions/seance", methods=['GET', 'POST'])
def insertion_seance():
    '''
    Route spéciale servant à insérer une séance dans la base de données
    '''
    form = Insertion_seance() 

    try:
        if form.validate_on_submit():
            id_seance =  clean_arg(request.form.get("id_seance", None))
            id_exposition =  clean_arg(request.form.get("id_exposition", None))
            id_activite =  clean_arg(request.form.get("id_activite", None))
            langue_seance =  clean_arg(request.form.get("langue_seance", None))
            date_seance =  clean_arg(request.form.getlist("date_seance", None))
            heure_debut =  clean_arg(request.form.get("heure_debut", None))
            heure_fin =  clean_arg(request.form.get("heure_fin", None))
            nature_seance =  clean_arg(request.form.get("nature_seance", None))

            nouvelle_seance = Seances(id_seance=id_seance, 
                id_exposition=id_exposition,
                id_activite=id_activite,
                langue_seance=langue_seance,
                date_seance=date_seance,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                nature_seance=nature_seance
                )
            
            db.session.add(nouvelle_seance)
            db.session.commit()

            flash("L'insertion de la séance n°"+ id_seance + " s'est correctement déroulée", 'info')
            print("réussite!")
    
    except Exception as e :
        flash("Une erreur s'est produite lors de l'insertion de la séance n°" + id_seance + " : " + str(e), "error")
        print("échec!")
        db.session.rollback()
    
    return render_template("pages/insertion_seance.html", 
            sous_titre= "Insertion d'une nouvelle séance", 
            form=form)
