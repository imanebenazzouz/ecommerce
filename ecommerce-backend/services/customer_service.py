"""
Service métier pour la gestion du support client.

Ce service gère :
- Création de fils de discussion
- Envoi de messages
- Fermeture de fils
- Gestion des réponses admin
"""

from typing import Optional, List
from datetime import datetime
import uuid
from database.models import MessageThread, Message, User
from database.repositories_simple import PostgreSQLThreadRepository, PostgreSQLUserRepository


class CustomerService:
    """Service métier pour la gestion du support client."""
    
    def __init__(self, thread_repo: PostgreSQLThreadRepository, user_repo: PostgreSQLUserRepository):
        self.thread_repo = thread_repo
        self.user_repo = user_repo
    
    def open_thread(self, user_id: str, subject: str, order_id: Optional[str] = None) -> MessageThread:
        """Ouvre un nouveau fil de discussion."""
        thread_data = {
            "user_id": user_id,
            "order_id": order_id,
            "subject": subject,
            "closed": False
        }
        
        thread = self.thread_repo.create(thread_data)
        return thread
    
    def post_message(self, thread_id: str, author_user_id: Optional[str], content: str) -> Message:
        """Poste un message dans un fil de discussion."""
        thread = self.thread_repo.get_by_id(thread_id)
        if not thread or thread.closed:
            raise ValueError("Fil introuvable ou fermé")
        
        if author_user_id is not None and not self.user_repo.get_by_id(author_user_id):
            raise ValueError("Auteur inconnu")
        
        message_data = {
            "thread_id": thread_id,
            "author_user_id": author_user_id,
            "content": content
        }
        
        message = self.thread_repo.add_message(thread_id, message_data)
        return message
    
    def close_thread(self, thread_id: str, admin_user_id: str) -> MessageThread:
        """Ferme un fil de discussion (admin)."""
        admin = self.user_repo.get_by_id(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants")
        
        thread = self.thread_repo.get_by_id(thread_id)
        if not thread:
            raise ValueError("Fil introuvable")
        
        thread.closed = True
        self.thread_repo.update(thread)
        return thread
    
    def get_thread(self, thread_id: str) -> Optional[MessageThread]:
        """Récupère un fil de discussion."""
        return self.thread_repo.get_by_id(thread_id)
    
    def list_user_threads(self, user_id: str) -> List[MessageThread]:
        """Récupère tous les fils d'un utilisateur."""
        return self.thread_repo.list_by_user(user_id)
    
    def list_all_threads(self) -> List[MessageThread]:
        """Récupère tous les fils (admin)."""
        return self.thread_repo.get_all()
