from ..app import app, db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,TextAreaField, SelectMultipleField, DateField, TimeField
from wtforms.validators import Optional
from wtforms.validators import DataRequired, Length, Regexp
from ..models.madata import *


class Recherche(FlaskForm):
    id_seance = StringField("ID de la séance", validators=[Optional()])
    exposition = SelectField("Exposition", choices=[], validators=[Optional()])
    activite = SelectField("Activité", choices=[], validators=[Optional()])
    public = SelectField("Type de public", choices=[], validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(Recherche, self).__init__(*args, **kwargs)

        # remplir dynamiquement les choix depuis la DB
        self.exposition.choices = [('', '-- Sélectionnez une exposition --')] + [
            (expo.nom_exposition, expo.nom_exposition) for expo in Expositions.query.order_by(Expositions.nom_exposition).all()
        ]
        self.activite.choices = [('', '-- Sélectionnez une activité --')] + [
            (act.type_activite, act.type_activite) for act in Activites.query.order_by(Activites.type_activite).all()
        ]
        self.public.choices = [('', '-- Sélectionnez un type de public --')] + [
            (pub.type_public, pub.type_public) for pub in Publics.query.order_by(Publics.type_public).all()
        ]

class Recherche_Rapide(FlaskForm):
    chaine = StringField("Recherche", validators=[Optional()])

# -- INSERTIONS --

class Insertion_seance(FlaskForm):
    '''
    Classe servant à créer le formulaire d'insertion des séances. Il reprend la structure de la table Seances.
    ---
    En entrée, prend les informations des utilisateurs soit en string (id_seance, langue_seance), 
    soit en Datetime (date_seance, heure_début, heure_fin), soit par le biais de champs de sélection 
    prédéfinis (id_exposition, id_activite, nature_seance) pour les FK et nature_seance qui n'a que deux valeurs
    '''
    id_seance = StringField("id_seance", validators=[])
    id_exposition = SelectField("id_exposition", choices=[(''),('OUR'),('CAD'),('CHR'),('BIJ'),('COL'),('GMG'),('MOD'),('INT'),('ROC'),('DPP'),('MBD'),('POI')])
    id_activite = SelectField("id_activite", choices=[(''),('CO'),('SU'),('VA'),('HP'),('VG'),('EV'),('AT'),('ST'),('PA'),('XX'),('VT'),('VL'),('AP')])
    langue_seance = StringField("langue_seance", validators=[])
    date_seance = DateField("date_seance", validators=[]) # DateField rend un objet date, nécessaire ici
    heure_debut = TimeField("heure_debut", validators=[]) # TimeField rend un objet time, nécessaire ici
    heure_fin = TimeField("heure_fin", validators=[])
    nature_seance = SelectField("nature_seance", validators=[],choices=[(''),('réservation en ligne'),('réservation en groupe')])

class Insertion_exposition(FlaskForm):
    '''
    Classe servant à créer le formulaire d'insertion des expositions.
    ---
    En entrée, prend des informations fournies par l'utilisateur, tout en contraignant l'utilisation de caractères pour l'ID
    '''

    id_exposition = StringField("id_exposition",
    validators=[Regexp("[A-Z]", message="L'identifiant doit être écrit en majuscules"), # regex permettant d'assurer que l'entrée sera en majuscule
    Length(max=3,message="L'identifiant d'exposition ne peut pas faire plus de 3 caractères")]) # contraint l'utilisateur à indiquer l'identifiant en 3 lettres ou moins
    nom_exposition = StringField("nom_exposition")

class Insertion_activite(FlaskForm):
    '''
    Classe servant à créer le formulaire d'insertion des expositions.
    ---
    En entrée, prend des informations fournies par l'utilisateur pour créer l'ID et le type d'activité
    '''

    id_activite = StringField("id_activite",
    validators=[Regexp("[A-Z]", message="L'identifiant doit être écrit en majuscules"), # regex permettant d'assurer que l'entrée sera en majuscule
    Length(max=2,message="L'identifiant d'exposition ne peut pas faire plus de 3 caractères")]) # contraint l'utilisateur à indiquer l'identifiant en 2 lettres ou moins
    type_activite = StringField("type_activite")

# -- SUPPRESSIONS --

class Suppression_seance(FlaskForm):
    '''
    Classe servant à créer le formulaire de suppression des séances. Il reprend une structure plus légère de la table Seances.
    ---
    En entrée, prend les informations spécifiées par les utilisateurs pour l'id_seance.
    '''

    id_seance = StringField("id_seance", validators=[DataRequired(message="ID séance obligatoire")]) # inclusion du validateur DataRequired puisque l'ID à supprimer doit exister

class Suppression_exposition(FlaskForm):
    '''
    Classe servant à supprimer une exposition. La structure est la même que pour l'insertion.
    '''

    id_exposition = StringField("id_exposition", validators=[])
    nom_exposition = StringField("nom_exposition", validators=[])

class Suppression_activite(FlaskForm):
    '''
    Classe servant à supprimer une activité. La structure est la même que pour l'insertion.
    '''

    id_activite = StringField("id_activite", validators=[])
    type_activite = StringField("type_activite", validators=[])