"""
========================================
SERVICE SUPPORT CLIENT
========================================

Ce service gère le système de messagerie du support client.

Fonctionnalités :
- ✅ Créer un nouveau fil de discussion (ticket support)
- ✅ Envoyer des messages dans un fil
- ✅ Fermer un fil (résolu)
- ✅ Lister les fils d'un utilisateur
- ✅ Lister tous les fils (admin)

SYSTÈME DE MESSAGERIE :
- Un fil (thread) = une conversation entre un client et le support
- Chaque fil peut être lié à une commande (optionnel)
- Les messages peuvent être envoyés par le client OU l'admin
- author_user_id = None → Message de l'admin
- author_user_id = UUID → Message du client
"""

# ========== IMPORTS ==========
from typing import Optional, List  # Pour le typage Python
from datetime import datetime  # Pour les dates
import uuid  # Pour générer des IDs
from database.models import MessageThread, Message, User  # Modèles SQLAlchemy
from database.repositories_simple import PostgreSQLThreadRepository, PostgreSQLUserRepository  # Accès BDD

# ========================================
# CLASSE CustomerService
# ========================================
class CustomerService:
    """
    Service métier pour la gestion du support client.
    
    Ce service gère toutes les interactions entre clients et support.
    """
    
    def __init__(self, thread_repo: PostgreSQLThreadRepository, user_repo: PostgreSQLUserRepository):
        """
        Initialise le service avec les repositories nécessaires.
        
        Args:
            thread_repo: Repository pour accéder aux fils de discussion
            user_repo: Repository pour vérifier les utilisateurs
        """
        self.thread_repo = thread_repo  # Pour gérer les fils et messages
        self.user_repo = user_repo      # Pour vérifier les utilisateurs
    
    # ========================================
    # OUVRIR UN FIL DE DISCUSSION
    # ========================================
    def open_thread(self, user_id: str, subject: str, order_id: Optional[str] = None) -> MessageThread:
        """
        Ouvre un nouveau fil de discussion (ticket support).
        
        Utilisé quand :
        - Un client a une question générale
        - Un client a un problème avec une commande spécifique
        
        Args:
            user_id: ID du client qui ouvre le fil
            subject: Sujet/titre de la conversation (ex: "Problème de livraison")
            order_id: ID de la commande concernée (optionnel)
            
        Returns:
            Le fil de discussion créé (MessageThread)
        """
        # Données du nouveau fil
        thread_data = {
            "user_id": user_id,        # Client qui ouvre le fil
            "order_id": order_id,      # Commande liée (optionnel)
            "subject": subject,        # Sujet de la conversation
            "closed": False            # Fil ouvert par défaut
        }
        
        # Créer le fil dans la base de données
        thread = self.thread_repo.create(thread_data)
        return thread
    
    # ========================================
    # POSTER UN MESSAGE
    # ========================================
    def post_message(self, thread_id: str, author_user_id: Optional[str], content: str) -> Message:
        """
        Poste un message dans un fil de discussion existant.
        
        Peut être utilisé par :
        - Le client (author_user_id = son ID)
        - L'admin (author_user_id = None)
        
        Args:
            thread_id: ID du fil de discussion
            author_user_id: ID de l'auteur (None = admin, UUID = client)
            content: Contenu du message
            
        Returns:
            Le message créé
            
        Raises:
            ValueError: Si le fil est introuvable, fermé, ou l'auteur inconnu
        """
        # Vérifier que le fil existe et est ouvert
        thread = self.thread_repo.get_by_id(thread_id)
        if not thread or thread.closed:
            raise ValueError("Fil introuvable ou fermé")
        
        # Si c'est un message client (pas admin), vérifier que l'utilisateur existe
        if author_user_id is not None and not self.user_repo.get_by_id(author_user_id):
            raise ValueError("Auteur inconnu")
        
        # Données du message
        message_data = {
            "thread_id": thread_id,              # Fil auquel appartient le message
            "author_user_id": author_user_id,    # Auteur (None = admin)
            "content": content                   # Contenu du message
        }
        
        # Ajouter le message au fil
        message = self.thread_repo.add_message(thread_id, message_data)
        return message
    
    # ========================================
    # FERMER UN FIL (ADMIN)
    # ========================================
    def close_thread(self, thread_id: str, admin_user_id: str) -> MessageThread:
        """
        Ferme un fil de discussion (marque comme résolu).
        
        Réservé aux admins uniquement.
        Une fois fermé, plus de messages ne peuvent être ajoutés.
        
        Args:
            thread_id: ID du fil à fermer
            admin_user_id: ID de l'admin qui ferme le fil
            
        Returns:
            Le fil de discussion mis à jour
            
        Raises:
            PermissionError: Si l'utilisateur n'est pas admin
            ValueError: Si le fil est introuvable
        """
        # Vérifier que l'utilisateur est bien un admin
        admin = self.user_repo.get_by_id(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants")
        
        # Vérifier que le fil existe
        thread = self.thread_repo.get_by_id(thread_id)
        if not thread:
            raise ValueError("Fil introuvable")
        
        # Fermer le fil (closed = True)
        thread.closed = True  # type: ignore
        self.thread_repo.update(thread)  # type: ignore
        return thread
    
    # ========================================
    # RÉCUPÉRER UN FIL
    # ========================================
    def get_thread(self, thread_id: str) -> Optional[MessageThread]:
        """
        Récupère un fil de discussion spécifique.
        
        Utilisé pour :
        - Afficher la conversation complète
        - Consulter l'historique des messages
        
        Args:
            thread_id: ID du fil
            
        Returns:
            Le fil avec tous ses messages, ou None si introuvable
        """
        return self.thread_repo.get_by_id(thread_id)
    
    # ========================================
    # LISTER LES FILS D'UN UTILISATEUR
    # ========================================
    def list_user_threads(self, user_id: str) -> List[MessageThread]:
        """
        Récupère tous les fils de discussion d'un utilisateur.
        
        Utilisé dans :
        - La page "Mon support" du client
        - Pour afficher l'historique des tickets
        
        Args:
            user_id: ID du client
            
        Returns:
            Liste de tous les fils de l'utilisateur
        """
        return self.thread_repo.list_by_user(user_id)  # type: ignore
    
    # ========================================
    # LISTER TOUS LES FILS (ADMIN)
    # ========================================
    def list_all_threads(self) -> List[MessageThread]:
        """
        Récupère TOUS les fils de discussion (admin uniquement).
        
        Utilisé dans :
        - L'interface admin du support
        - Pour voir tous les tickets de tous les clients
        
        Returns:
            Liste de tous les fils de tous les utilisateurs
        """
        return self.thread_repo.get_all()
