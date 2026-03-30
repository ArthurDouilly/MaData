from ..app import app, db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,TextAreaField, SelectMultipleField, DateField, DateTimeField



# class Recherche(FlaskForm): à modifier pour rendre dynamique
class Recherche(FlaskForm):
    id_seance = StringField("id_seance", validators=[])
    exposition = SelectField("exposition", choices=[('','')])
    activite  = SelectField("activite", choices=[('','')])
    public    = SelectField("public", choices=['',''])

class Insertion_seance(FlaskForm):
    id_seance = StringField("id_seance", validators=[])
    id_exposition = SelectField("id_exposition", choices=[(''),('OUR'),('CAD'),('CHR'),('BIJ'),('COL'),('GMG'),('MOD'),('INT'),('ROC'),('DPP'),('MBD'),('POI')])
    id_activite = SelectField("id_activite", choices=[(''),('CO'),('SU'),('VA'),('HP'),('VG'),('EV'),('AT'),('ST'),('PA'),('XX'),('VT'),('VL'),('AP')])
    langue_seance = StringField("langue_seance", validators=[])
    date_seance = DateField("date_seance",format="%Y-%m-%d")
    heure_debut = DateTimeField("heure_debut", format="%H-%M-%S")
    heure_fin = DateTimeField("heure_fin", format="%H-%M-%S")
    nature_seance = SelectField("nature_seance", validators=[],choices=[(''),('réservation en ligne'),('réservation en groupe')])