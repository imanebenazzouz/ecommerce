"""
========================================
CONNEXION À LA BASE DE DONNÉES POSTGRESQL
========================================

Ce fichier configure la connexion à PostgreSQL via SQLAlchemy.

Responsabilités :
- ✅ Créer le "moteur" de connexion à PostgreSQL
- ✅ Configurer le "pool" de connexions (pour gérer plusieurs utilisateurs simultanés)
- ✅ Fournir des sessions de base de données aux endpoints FastAPI
- ✅ Créer/supprimer les tables

IMPORTANT :
- SQLAlchemy = ORM (Object-Relational Mapping)
- Il transforme les objets Python en requêtes SQL automatiquement
- Exemple : user.email → SELECT email FROM users WHERE ...
"""

# ========== IMPORTS ==========
import os  # Pour lire les variables d'environnement
from sqlalchemy import create_engine  # Moteur de connexion à PostgreSQL
from sqlalchemy.orm import sessionmaker  # Fabrique de sessions DB
from sqlalchemy.pool import StaticPool  # Gestion du pool de connexions
from database.models import Base  # Modèles SQLAlchemy (définition des tables)

# ========================================
# CONFIGURATION DE LA CONNEXION
# ========================================

# URL de connexion à PostgreSQL
# Format : postgresql://utilisateur:motdepasse@hôte:port/nomdelabase
# Par défaut : postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce
# Peut être surchargé avec la variable d'environnement DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce")

# ========================================
# CRÉATION DU MOTEUR (ENGINE)
# ========================================
# Le moteur gère la connexion bas niveau à PostgreSQL
engine = create_engine(
    DATABASE_URL,  # URL de connexion
    
    # ===== CONFIGURATION DU POOL DE CONNEXIONS =====
    # Un "pool" = ensemble de connexions réutilisables
    # Pourquoi ? Ouvrir/fermer une connexion à chaque requête est LENT
    # Solution : Garder des connexions ouvertes et les réutiliser
    
    pool_size=10,  # Nombre de connexions toujours ouvertes (10 connexions permanentes)
    max_overflow=20,  # Connexions supplémentaires autorisées si besoin (10 + 20 = 30 max)
    
    # pool_pre_ping : Vérifie que la connexion est vivante avant de l'utiliser
    # Évite les erreurs si PostgreSQL a fermé une connexion inactive
    pool_pre_ping=True,
    
    # pool_recycle : Recycler (fermer/réouvrir) les connexions après 1 heure
    # Évite les connexions "zombies" qui restent ouvertes indéfiniment
    pool_recycle=3600,  # 3600 secondes = 1 heure
    
    # echo : Affiche toutes les requêtes SQL dans la console (utile pour debug)
    # ⚠️ Mettre à True pour voir toutes les requêtes SQL exécutées
    echo=False
)

# ========================================
# CRÉATION DU SESSIONMAKER
# ========================================
# SessionLocal = fabrique de sessions de base de données
# Une "session" = connexion active à PostgreSQL pendant laquelle on peut faire des requêtes
# autocommit=False : Les modifications ne sont pas commitées automatiquement (on contrôle quand)
# autoflush=False : Les objets ne sont pas automatiquement envoyés à la DB (on contrôle quand)
# bind=engine : Lie cette session au moteur créé ci-dessus
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ========================================
# FONCTIONS UTILITAIRES
# ========================================

def get_db():
    """
    Dépendance FastAPI pour obtenir une session de base de données.
    
    Cette fonction est utilisée par les endpoints FastAPI via Depends(get_db).
    
    Fonctionnement :
    1. Crée une nouvelle session DB
    2. La fournit à l'endpoint (via yield)
    3. Ferme automatiquement la session après l'endpoint (dans le finally)
    
    Exemple d'utilisation dans api.py :
        @app.get("/users")
        def list_users(db: Session = Depends(get_db)):
            users = db.query(User).all()  # Utilise la session
            return users
        # La session est automatiquement fermée après
    """
    db = SessionLocal()  # Crée une nouvelle session depuis le pool
    try:
        yield db  # Fournit la session à l'endpoint
    finally:
        db.close()  # Ferme la session (la remet dans le pool)

def create_tables():
    """
    Crée toutes les tables définies dans models.py.
    
    Cette fonction lit toutes les classes qui héritent de Base (User, Product, Order, etc.)
    et génère les requêtes SQL CREATE TABLE correspondantes.
    
    ⚠️ Si les tables existent déjà, cette fonction ne fait rien (pas d'erreur).
    
    Exemple de SQL généré :
        CREATE TABLE users (
            id UUID PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            ...
        );
    """
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Supprime toutes les tables de la base de données.
    
    ⚠️ OPÉRATION DESTRUCTIVE ! Toutes les données seront perdues !
    
    Utilisé uniquement pour :
    - Tests (nettoyer la DB entre les tests)
    - Développement (réinitialiser la DB)
    
    ⚠️ NE JAMAIS utiliser en production !
    """
    Base.metadata.drop_all(bind=engine)