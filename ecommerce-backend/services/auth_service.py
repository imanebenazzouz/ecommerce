"""
Service d'authentification
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from database.models import User
from database.repositories_simple import PostgreSQLUserRepository
from enums import OrderStatus

class AuthService:
    """Service d'authentification"""
    
    def __init__(self, user_repo: PostgreSQLUserRepository):
        self.user_repo = user_repo
        self.secret_key = "your-secret-key-change-in-production"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def hash_password(self, password: str) -> str:
        """Hash un mot de passe"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: dict) -> str:
        """Crée un token JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Vérifie un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur"""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    def register(self, email: str, password: str, first_name: str, last_name: str, address: str) -> User:
        """Enregistre un nouvel utilisateur"""
        # Vérifier si l'email existe déjà
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email déjà utilisé.")
        
        # Créer le nouvel utilisateur
        hashed_password = self.hash_password(password)
        user_data = {
            "email": email,
            "password_hash": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "is_admin": False
        }
        return self.user_repo.create(user_data)
