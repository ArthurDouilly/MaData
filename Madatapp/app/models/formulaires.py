from ..app import app, db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,TextAreaField, SelectMultipleField



# class Recherche(FlaskForm): à modifier pour rendre dynamique
class Recherche(FlaskForm):
    id_seance = StringField("id_seance", validators=[])
    exposition = SelectField("exposition", choices=[('','')])
    activite  = SelectField("activite", choices=[('','')])
    public    = SelectField("public", choices=['',''])