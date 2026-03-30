
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

app = Flask(__name__, #instancie app, où "__name__" comme sécurité pour lancement
template_folder='templates',
    static_folder='statics')
app.config.from_object(Config)
#mauvaise pratique de faire les routes directement dans app.py => à mettre dans dossier 'routes'
db = SQLAlchemy(app)

from .routes import generales #On demande d'importer toutes les routes du package éponyme

