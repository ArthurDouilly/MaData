from ..app import app, db
from flask import render_template, request, flash
from ..models.madata import *
from ..models.formulaires import Suppression_seance, Suppression_exposition, Suppression_activite
from ..utils.transformations import  clean_arg

# suppression d'une exposition
@app.route("/suppressions/exposition", methods=['GET','POST'])
def suppression_exposition():
    '''
    Cette route permet d'appeler la page de suppression des expositions en GET afin que l'utilisateur puisse remplir le formulaire,
    puis se recharge en POST avec les informations afin de traiter les données d'entrée.
    ---
    Les données entrées proviennent de l'utilisateur mais sont conditionnées par la classe Suppression_exposition qui crée le formulaire.
    '''
    form = Suppression_exposition() # appel du formulaire depuis formulaires.py
    form.id_exposition.choices = [('','')] + [(Expositions.id_exposition, Expositions.nom_exposition) for exposition in Expositions.query.all()] #récupération des informations depuis la table Expositions

    def delete_exposition(exposition):
        '''
        Définition interne permettant d'effectuer la suppression puis le commit.
        '''
        exposition = Expositions.query.get(id_exposition)
        if exposition:
            db.session.delete(exposition)
            db.session.commit()

    try: # étape de protection pour éviter un lock de la base de données
        if form.validate_on_submit(): # si le formulaire est valide au moment de la soumission des données remplies
            id_exposition = clean_arg(request.form.get("id_exposition", None)) # création de la variable id_exposition
            nom_exposition = clean_arg(request.form.get("nom_exposition", None)) # création de la variable nom_exposition

            if id_exposition: # si id_exposition existe, activation de la définition delete_exposition et information de l'utilisateur
                delete_exposition(id_exposition)
                flash("La suppression de l'exposition s'est correctement déroulée", 'info')

            elif nom_exposition: # sinon, même tentative pour nom_exposition, ce qui permet de ne pas avoir à remplir tout le formulaire
                delete_exposition(nom_exposition)
                flash("La suppression de l'exposition s'est correctement déroulée", 'info')

            else: # sinon, message d'erreur utilisateur
                flash("L'exposition n'est pas correctement indiquée", "error") 

    except Exception as e: # message d'erreur système
        flash("Une erreur s'est produite lors de la suppression : " + str(e), "error")
    
    return render_template("pages/suppression_exposition.html", 
            sous_titre= "Suppression exposition" , 
            form=form)

@app.route("/suppressions/seance", methods=['GET', 'POST'])
def suppression_seance():
    form = Suppression_seance()
    form.id_seance.choices = [('')] + [seance.id_seance for seance in Seances.query.all()]

    def delete_seance(seance):
        # vérifier que le code existe bien en base
        seance = Seances.query.get(id_seance)
        if seance:
            db.session.delete(seance)
            db.session.commit()

    try:
        if form.validate_on_submit():
            id_seance =  clean_arg(request.form.get("id_seance", None))
            date_seance =  clean_arg(request.form.get("date_seance", None))

            if id_seance:
                delete_seance(id_seance)
                flash("La suppression de la séance s'est correctement déroulée", 'info')

            else:
                flash("La séance n'est pas correctement indiquée", "error")
    
    except Exception as e :
        flash("Une erreur s'est produite lors de la suppression : " + str(e), "error")
    
    return render_template("pages/suppression_seance.html", 
            sous_titre= "Suppression seance" , 
            form=form)

# suppression d'une activité
@app.route("/suppressions/activité", methods=['GET','POST'])
def suppression_activite():
    form = Suppression_activite()
    form.id_activite.choices = [('','')] + [(Activites.id_activite, Activites.type_activite) for activite in Activites.query.all()]

    def delete_activite(activite):
        activite = Activites.query.get(id_activite)
        if activite:
            db.session.delete(activite)
            db.session.commit()

    try:
        if form.validate_on_submit():
            id_activite = clean_arg(request.form.get("id_activite", None))
            type_activite = clean_arg(request.form.get("type_activite", None))

            if id_activite:
                delete_activite(id_activite)
                flash("La suppression de l'activité s'est correctement déroulée", 'info')

            elif type_activite:
                delete_activite(type_activite)
                flash("La suppression de l'activité s'est correctement déroulée", 'info')

            else:
                flash("L'activité n'est pas correctement indiquée", "error") 

    except Exception as e:
        flash("Une erreur s'est produite lors de la suppression : " + str(e), "error")
    
    return render_template("pages/suppression_activite.html", 
            sous_titre= "Suppression activité" , 
            form=form)