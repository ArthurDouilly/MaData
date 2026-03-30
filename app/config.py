import os
import dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv.load_dotenv(os.path.join(BASE_DIR, ".env"))


def to_bool(value):
    """
    Convertit une string en booléen.
    True si value est "true", "1", "yes", "y" (insensible à la casse).
    """
    if value is None:
        return False
    return str(value).strip().lower() in ["true", "1", "yes", "y"]



class Config:
    # Mode debug (False par défaut)
    DEBUG = to_bool(os.environ.get("DEBUG", "False"))

    # Base de données (SQLite par défaut) (les informations du point env)
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

    # Pagination (10 résultats par page par défaut)
    RESULTATS_PAR_PAGE = int(os.environ.get("RESULTATS_PAR_PAGE", 10))

    # Logs SQL (False par défaut)
    SQLALCHEMY_ECHO = to_bool(os.environ.get("SQLALCHEMY_ECHO", "false"))

    # Clé secrète Flask (clé par défaut pour dev)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key")

    # Protection CSRF (True par défaut)
    WTF_CSRF_ENABLED = to_bool(os.environ.get("WTF_CSRF_ENABLED", "true"))