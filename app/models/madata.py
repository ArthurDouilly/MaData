from ..app import app, db

# Reprendre tout le SQL, globalement...

# ----- tables de relations -----

# les tables de relations sont représentées par des variables utilisant db.Table
# modèle : db.Column('nom', [type], db.ForeignKey('tableA.[nom]'),primary_key=True)

seances_salles = db.Table(
    "seances_salles",
    db.Column('id_seance', db.String(50), db.ForeignKey('madata_db.seances.id_seance'), primary_key=True),
    db.Column('id_salle', db.Integer, db.ForeignKey('madata_db.salles.id_salle'), primary_key=True),
    schema="madata_db"
)

seances_publics = db.Table(
    "seances_publics",
    db.Column('id_seance', db.String(50), db.ForeignKey('madata_db.seances.id_seance'), primary_key=True),
    db.Column('id_public', db.Integer, db.ForeignKey('madata_db.publics.id_public'), primary_key=True),
    schema="madata_db"
)

seances_groupes = db.Table(
    "seances_groupes",
    db.Column('id_seance', db.String(50), db.ForeignKey('madata_db.seances.id_seance'), primary_key=True),
    db.Column('id_groupe', db.Integer, db.ForeignKey('madata_db.groupes.id_groupe'), primary_key=True),
    schema="madata_db"
)

bilan_seances = db.Table(
    "bilan_seances",
    db.Column('id_bilan_annuel', db.Integer, db.ForeignKey('madata_db.bilan_annuel_sdp.id_bilan_annuel'), primary_key=True),
    db.Column('id_seance', db.String(50), db.ForeignKey('madata_db.seances.id_seance'), primary_key=True),
    schema="madata_db"
)

billets_publics = db.Table(
    "billets_publics",
    db.Column('id_billet', db.Integer, db.ForeignKey('madata_db.billets.id_billet'), primary_key=True),
    db.Column('id_public', db.Integer, db.ForeignKey('madata_db.publics.id_public'), primary_key=True),
    schema="madata_db"
)

expositions_salles = db.Table(
    "expositions_salles",
    db.Column('id_expositions', db.String(50), db.ForeignKey('madata_db.expositions.id_exposition'), primary_key=True),
    db.Column('id_salle', db.Integer, db.ForeignKey('madata_db.groupes.id_groupe'), primary_key=True),
    schema="madata_db"
)

# ----- les tables, représentées par des classes -----

# --- Séances ---

class Seances(db.Model):
    '''
    Classe servant à modéliser la table 'Séances' et ses relations.
    '''
    __tablename__ = "seances"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_seance = db.Column(db.String(50), primary_key=True)
    id_exposition = db.Column(db.String(10), db.ForeignKey('madata_db.expositions.id_exposition'))
    id_activite = db.Column(db.String(10), db.ForeignKey('madata_db.activites.id_activite'))
    langue_seance = db.Column(db.String(10))
    date_seance = db.Column(db.Date)
    heure_debut = db.Column(db.Time)
    heure_fin = db.Column(db.Time)
    nature_seance = db.Column(db.String(50))

    # propriétés de relations simples (sans table de relations)
    expositions = db.relationship('Expositions', backref="madata_db.expositions", lazy=True)
    activites = db.relationship('Activites', backref='madata_db.activites', lazy=True)

    # propriétés de relations many-to-many (avec table de relations)
    seances_salles = db.relationship(
        'Salles',
        secondary=seances_salles,
        backref="madata_db.salles"
    )
    seances_publics = db.relationship(
        'Publics',
        secondary=seances_publics,
        backref="madata_db.publics"
    )
    seances_groupes = db.relationship(
        'Groupes',
        secondary=seances_groupes,
        backref='madata_db.groupes'
    )
    bilan_seances = db.relationship(
        'Bilan_annuel_sdp',
        secondary=bilan_seances,
        backref='madata_db.bilan'
    )

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Seances %r>' % (self.id_seance)

# --- Activités ---

class Activites(db.Model):
    '''
    Classe servant à modéliser la table 'Activités' et ses relations.
    '''
    __tablename__ = "activites"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_activite = db.Column(db.String(10),primary_key=True)
    type_activite = db.Column(db.String(50), nullable=False)

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Activites %r>' % (self.type_activite)

# --- Expositions ---

class Expositions(db.Model):
    '''
    Classe servant à modéliser la table 'Expositions' et ses relations.
    '''
    __tablename__ = "expositions"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_exposition = db.Column(db.String(10),primary_key=True)
    nom_exposition = db.Column(db.String(50), nullable=False)

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Expositions %r>' % (self.nom_exposition)

# --- Salles ---

class Salles(db.Model):
    '''
    Classe servant à modéliser la table 'Salles' et ses relations.
    '''
    __tablename__ = "salles"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_salle = db.Column(db.Integer,primary_key=True)
    nom_salle = db.Column(db.String(50))

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Salles %r>' % (self.nom_salle)

# --- Capacités ---

class Capacite(db.Model):
    '''
    Classe servant à modéliser la table 'Capacite' et ses relations.
    '''
    __tablename__ = "capacite"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_seance = db.Column(db.Integer, db.ForeignKey('madata_db.seances.id_seance'), primary_key=True)
    places_ouvertes = db.Column(db.Integer)
    places_vendues = db.Column(db.Integer)
    places_disponibles = db.Column(db.Integer)
    overbooking = db.Column(db.Integer)
    overbooking_vendu = db.Column(db.Integer)
    taux_remplissage = db.Column(db.Integer)

    # clés étrangères
    seances_capacite = db.relationship('Seances', backref='seances_capacite', lazy=True)

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Capacites %r>' % (self.id_seance)

# --- Publics ---

class Publics(db.Model):
    '''
    Classe servant à modéliser la table 'Publics' et ses relations.
    '''
    __tablename__ = "publics"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_public = db.Column(db.Integer,primary_key=True)
    type_public = db.Column(db.String(50))

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Publics %r>' % (self.type_public)

# --- Groupes ---

class Groupes(db.Model):
    '''
    Classe servant à modéliser la table 'Groupes' et ses relations.
    '''
    __tablename__ = "groupes"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_groupe = db.Column(db.Integer,primary_key=True)
    reservation = db.Column(db.String(50))
    nom_client = db.Column(db.String(50))
    nature_client = db.Column(db.String(50))
    type_client = db.Column(db.String(50))
    ville = db.Column(db.String(50))
    pays = db.Column(db.String(50))
    code_postal = db.Column(db.String(50))
    langue = db.Column(db.String(50))

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Groupes %r>' % (self.id_groupe)

# --- Billets ---

class Billets(db.Model):
    '''
    Classe servant à modéliser la table 'Billets' et ses relations.
    '''
    __tablename__ = "billets"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_billet = db.Column(db.Integer,primary_key=True)
    numero_billet = db.Column(db.String(50))
    nom_client = db.Column(db.String(50))
    id_seance = db.Column(db.String(50), db.ForeignKey('madata_db.seances.id_seance'))
    tarif = db.Column(db.String(50))
    numero_operation = db.Column(db.String(50))
    date_creation = db.Column(db.Date)
    heure_operation = db.Column(db.Time)

    # clés étrangères
    seances_billets = db.relationship('Seances', backref='seances_billets', lazy=True)

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Billets %r>' % (self.name)

# --- Bilan_annuel_sdp ---

class Bilan_annuel_sdp(db.Model):
    '''
    Classe servant à modéliser la table 'Bilan_annuel_sdp' et ses relations.
    '''
    __tablename__ = "bilan_annuel_sdp"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    id_bilan_annuel = db.Column(db.Integer,primary_key=True)
    id_museofile = db.Column(db.String(20), db.ForeignKey('madata_db.frequentation_mdf_2024.id_museofile'))
    annee = db.Column(db.Integer, nullable=False)
    nb_seances = db.Column(db.Integer)
    nb_billets = db.Column(db.Integer)
    nb_expositions = db.Column(db.Integer)
    nb_activites = db.Column(db.Integer)

    # clés étrangères
    frequentations = db.relationship('Frequentation_mdf_2024', backref='frequentations', lazy=True)

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Bilan_annuel_sdp %r>' % (self.id_bilan_annuel)

# --- Fréquentation_mdf_2024 ---

class Frequentation_mdf_2024(db.Model):
    '''
    Classe servant à modéliser la table 'Frequentation_mdf_2024' et ses relations.
    '''
    __tablename__ = "frequentation_mdf_2024"
    __table_args__ = {'schema': 'madata_db'}

    # colonnes de la table
    lien_wikidata = db.Column(db.String(20))
    id_museofile = db.Column(db.String(20),primary_key=True)
    nom_musee = db.Column(db.String(300))
    ville = db.Column(db.String(100))
    description = db.Column(db.Text)
    label_th = db.Column(db.String(100))
    accessibilite_pmr = db.Column(db.Text)
    payant = db.Column(db.Integer)
    gratuit = db.Column(db.Integer)
    total = db.Column(db.Integer)
    individuel = db.Column(db.Integer)
    scolaires = db.Column(db.Integer)
    groupes_hors_scolaires = db.Column(db.Integer)
    moins_18_hors_scolaire = db.Column(db.Integer)
    visiteurs_18_25 = db.Column(db.Integer)

    # méthode de classe
    def __repr__(self) -> None:
        '''
        Méthode servant au débuggage (documentation SQLalchemy)
        '''
        return '<Frequentation_mdf_2024 %r>' % (self.nom_musee)

