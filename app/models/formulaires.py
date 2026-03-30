from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,TextAreaField, SelectMultipleField

#Là où on décrit tous nos formulaires :

# class Recherche(FlaskForm): à modifier pour rendre dynamique
class Recherche(FlaskForm):
    nom_exposition = SelectField("Exposition", validators=[], choices=[])
    type_activite  = SelectField("Activité", validators=[], choices=[])
    type_public    = SelectField("Type de public", validators=[], choices=[])
