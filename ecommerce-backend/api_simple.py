# api_simple.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid
import io
import time
from datetime import datetime

# Import des repositories PostgreSQL
from database.database import get_db, SessionLocal, create_tables
from database.repositories_simple import (
    PostgreSQLUserRepository, PostgreSQLProductRepository, 
    PostgreSQLCartRepository, PostgreSQLOrderRepository,
    PostgreSQLInvoiceRepository, PostgreSQLPaymentRepository,
    PostgreSQLThreadRepository
)

# Import des services métier
from services.auth_service import AuthService

# Import des modèles
from database.models import User, Product, Order, OrderItem, Delivery, Invoice, Payment, MessageThread, Message
from enums import OrderStatus, DeliveryStatus

app = FastAPI(title="Ecommerce API (TP)")

# -------------------------------- CORS --------------------------------
import os

# Configuration CORS sécurisée
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:5174",  # Vite dev server (port alternatif)
    "http://localhost:3000",  # React dev server alternatif
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
]

# Ajouter les origines de production si définies
if os.getenv("PRODUCTION_ORIGINS"):
    ALLOWED_ORIGINS.extend(os.getenv("PRODUCTION_ORIGINS").split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# -------------------------------- MODÈLES PYDANTIC --------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_admin: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# -------------------------------- ENDPOINTS --------------------------------

@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "API E-commerce",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }

# -------------------------------- AUTHENTIFICATION --------------------------------

@app.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    try:
        # Créer les repositories
        user_repo = PostgreSQLUserRepository(db)
        
        # Créer le service d'authentification
        auth_service = AuthService(user_repo)
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        
        # Créer l'utilisateur
        user = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            address=user_data.address
        )
        
        # Créer le token d'accès
        access_token = auth_service.create_access_token({"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_admin=user.is_admin,
                created_at=user.created_at
            )
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'inscription: {str(e)}")

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db = Depends(get_db)):
    """Connexion d'un utilisateur"""
    try:
        # Créer les repositories
        user_repo = PostgreSQLUserRepository(db)
        
        # Créer le service d'authentification
        auth_service = AuthService(user_repo)
        
        # Authentifier l'utilisateur
        user = auth_service.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        
        # Créer le token d'accès
        access_token = auth_service.create_access_token({"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_admin=user.is_admin,
                created_at=user.created_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la connexion: {str(e)}")

# -------------------------------- UTILITAIRES --------------------------------

def get_current_user(authorization: str = Header(None), db = Depends(get_db)):
    """Récupère l'utilisateur actuel à partir du token JWT"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token d'authentification manquant")
    
    token = authorization.split(" ")[1]
    
    try:
        # Créer les repositories
        user_repo = PostgreSQLUserRepository(db)
        
        # Créer le service d'authentification
        auth_service = AuthService(user_repo)
        
        # Décoder le token
        user_id = auth_service.decode_token(token)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        
        return user
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalide: {str(e)}")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur actuel"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at
    )

# -------------------------------- INITIALISATION --------------------------------

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    print("🚀 Démarrage de l'API E-commerce...")
    
    # Créer les tables de base de données
    create_tables()
    print("✅ Tables de base de données créées")
    
    print("🎉 API prête à recevoir des requêtes!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
