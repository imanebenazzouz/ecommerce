"""
Configuration de la base de données PostgreSQL
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database.models import Base

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce")

# Création du moteur de base de données
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Nombre de connexions dans le pool
    max_overflow=20,  # Connexions supplémentaires en cas de besoin
    pool_pre_ping=True,  # Vérifier les connexions avant utilisation
    pool_recycle=3600,  # Recycler les connexions après 1 heure
    echo=False  # Mettre à True pour voir les requêtes SQL
)

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crée toutes les tables dans la base de données"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Supprime toutes les tables de la base de données"""
    Base.metadata.drop_all(bind=engine)