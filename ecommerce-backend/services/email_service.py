"""
========================================
SERVICE D'ENVOI D'EMAILS (BREVO API)
========================================

Ce fichier gère l'envoi d'emails professionnels via l'API Brevo (ex-Sendinblue).

Brevo offre :
- 300 emails/jour GRATUITS (parfait pour commencer)
- Templates HTML professionnels
- Statistiques d'envoi (taux d'ouverture, clics, etc.)
- Anti-spam intégré

Emails envoyés par l'application :
1. Email de bienvenue (lors de l'inscription)
2. Email de réinitialisation de mot de passe (mot de passe oublié)

CONFIGURATION REQUISE (Variables d'environnement):
- BREVO_API_KEY : Clé API Brevo (obligatoire pour envoyer des emails)
- SENDER_EMAIL : Email expéditeur (doit être vérifié dans Brevo)
- SENDER_NAME : Nom de l'expéditeur (ex: "TechStore")
- FRONTEND_URL : URL du frontend (pour générer les liens de reset)

COMMENT OBTENIR UNE CLÉ API BREVO :
1. Créer un compte GRATUIT sur https://app.brevo.com
2. Aller dans "SMTP & API" → "API Keys"
3. Cliquer sur "Generate a new API key"
4. Copier la clé et la mettre dans config_email.sh
5. Vérifier votre email expéditeur dans "Senders & IP"

MODE DÉVELOPPEMENT :
Si BREVO_API_KEY n'est pas configurée, le service passe en mode dev.
Les emails sont affichés dans la console au lieu d'être envoyés.
"""

# ========== IMPORTS ==========
import os  # Pour lire les variables d'environnement
import requests  # Pour faire des appels HTTP à l'API Brevo
from typing import Optional  # Pour le typage Python

# ========================================
# CLASSE EmailService
# ========================================
class EmailService:
    """
    Service d'envoi d'emails professionn els via l'API Brevo.
    
    Fonctionnalités :
    - Envoi d'emails avec templates HTML
    - Mode développement (affichage console si pas de clé API)
    - Gestion des erreurs d'envoi
    - Logs détaillés pour le debug
    """
    
    def __init__(self):
        """
        Initialise le service d'email avec la configuration.
        
        Variables d'environnement lues :
        - BREVO_API_KEY : Clé API (ex: "xkeysib-abc123...")
        - SENDER_EMAIL : Email expéditeur (ex: "noreply@techstore.com")
        - SENDER_NAME : Nom expéditeur (ex: "TechStore")
        - FRONTEND_URL : URL frontend (ex: "http://localhost:5173")
        """
        # Lire la clé API depuis les variables d'environnement
        # Si non définie, chaîne vide par défaut
        self.api_key = os.getenv("BREVO_API_KEY", "")
        
        # Email expéditeur (doit être vérifié dans Brevo)
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@techstore.com")
        
        # Nom de l'expéditeur (affiché dans la boîte mail du destinataire)
        self.sender_name = os.getenv("SENDER_NAME", "TechStore")
        
        # URL du frontend (pour générer les liens de réinitialisation de mot de passe)
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        # URL de l'API Brevo pour envoyer des emails
        self.api_url = "https://api.brevo.com/v3/smtp/email"
        
        # Mode développement : activé si pas de clé API
        # En mode dev, les emails sont affichés dans la console au lieu d'être envoyés
        self.dev_mode = not self.api_key or self.api_key == ""
        
        # Log du mode actif au démarrage
        if self.dev_mode:
            print("⚠️  Mode développement activé - Les emails seront affichés dans la console")
        else:
            print(f"✅ Service d'email configuré - Expéditeur: {self.sender_email}")
    
    # ========================================
    # MÉTHODE PRINCIPALE D'ENVOI D'EMAIL
    # ========================================
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Envoie un email via l'API Brevo.
        
        Cette méthode est le cœur du service d'email. Elle est utilisée par
        send_password_reset_email() et send_welcome_email().
        
        Fonctionnement :
        1. Si mode dev : affiche l'email dans la console (pas d'envoi réel)
        2. Sinon : envoie l'email via l'API Brevo
        
        Args:
            to_email: Email du destinataire (ex: "client@example.com")
            subject: Sujet de l'email (ex: "Bienvenue chez TechStore")
            html_content: Contenu HTML complet de l'email
            
        Returns:
            True si l'email a été envoyé avec succès, False sinon
        """
        # ===== MODE DÉVELOPPEMENT =====
        # Si pas de clé API Brevo, on affiche l'email dans la console
        if self.dev_mode:
            print(f"\n{'='*60}")
            print(f"📧 MODE DÉVELOPPEMENT - Email non envoyé (simulation)")
            print(f"{'='*60}")
            print(f"À: {to_email}")
            print(f"Sujet: {subject}")
            print(f"Contenu HTML (extrait):\n{html_content[:200]}...")
            print(f"{'='*60}\n")
            return True
        
        # ===== MODE PRODUCTION : Appel à l'API Brevo =====
        
        # Headers HTTP pour l'API Brevo
        headers = {
            "accept": "application/json",           # On accepte du JSON en réponse
            "api-key": self.api_key,                # Clé API pour l'authentification
            "content-type": "application/json"      # On envoie du JSON
        }
        
        # Corps de la requête (payload) au format attendu par Brevo
        payload = {
            "sender": {  # Expéditeur
                "name": self.sender_name,         # Nom (ex: "TechStore")
                "email": self.sender_email        # Email (ex: "noreply@techstore.com")
            },
            "to": [  # Destinataires (liste, ici un seul)
                {
                    "email": to_email,            # Email du destinataire
                    "name": to_email.split("@")[0]  # Nom = partie avant @ de l'email
                }
            ],
            "subject": subject,                   # Sujet de l'email
            "htmlContent": html_content           # Contenu HTML de l'email
        }
        
        try:
            # Envoi de la requête POST à l'API Brevo
            # timeout=10 : si l'API ne répond pas en 10 secondes, on abandonne
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            
            # Vérifier le code de statut HTTP
            if response.status_code in (200, 201):
                # 200 = OK, 201 = Created → Email envoyé avec succès
                print(f"✅ Email envoyé avec succès à {to_email}")
                return True
            else:
                # Erreur HTTP (400, 401, 500, etc.)
                print(f"❌ Erreur lors de l'envoi de l'email: {response.status_code}")
                print(f"Réponse: {response.text}")
                return False
                
        except Exception as e:
            # Erreur réseau, timeout, ou autre exception
            print(f"❌ Exception lors de l'envoi de l'email: {str(e)}")
            return False
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Envoie un email de réinitialisation de mot de passe.
        
        Args:
            to_email: Email de l'utilisateur
            reset_token: Token de réinitialisation
            
        Returns:
            True si l'email a été envoyé avec succès, False sinon
        """
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
        
        subject = "Réinitialisation de votre mot de passe - TechStore"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                .button {{ display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                .warning {{ background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Réinitialisation de mot de passe</h1>
                </div>
                <div class="content">
                    <h2>Bonjour,</h2>
                    <p>Vous avez demandé à réinitialiser votre mot de passe sur <strong>TechStore</strong>.</p>
                    
                    <p>Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Réinitialiser mon mot de passe</a>
                    </div>
                    
                    <p>Ou copiez ce lien dans votre navigateur :</p>
                    <p style="word-break: break-all; color: #2563eb;">{reset_url}</p>
                    
                    <div class="warning">
                        <strong>⚠️ Important :</strong>
                        <ul>
                            <li>Ce lien est valable pendant <strong>1 heure</strong></li>
                            <li>Il ne peut être utilisé qu'<strong>une seule fois</strong></li>
                            <li>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email</li>
                        </ul>
                    </div>
                    
                    <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                        Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 TechStore. Tous droits réservés.</p>
                    <p>Si vous rencontrez des problèmes, contactez notre support.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)
    
    def send_welcome_email(self, to_email: str, first_name: str) -> bool:
        """Envoie un email de bienvenue à un nouvel utilisateur.
        
        Args:
            to_email: Email de l'utilisateur
            first_name: Prénom de l'utilisateur
            
        Returns:
            True si l'email a été envoyé avec succès, False sinon
        """
        subject = f"Bienvenue sur TechStore, {first_name} ! 🎉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10b981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Bienvenue sur TechStore !</h1>
                </div>
                <div class="content">
                    <h2>Bonjour {first_name},</h2>
                    <p>Merci de vous être inscrit sur <strong>TechStore</strong> ! 🛍️</p>
                    
                    <p>Votre compte a été créé avec succès. Vous pouvez maintenant :</p>
                    <ul>
                        <li>📱 Parcourir notre catalogue de produits</li>
                        <li>🛒 Ajouter des articles à votre panier</li>
                        <li>💳 Passer des commandes en toute sécurité</li>
                        <li>📦 Suivre vos livraisons</li>
                    </ul>
                    
                    <p style="margin-top: 30px;">
                        <a href="{self.frontend_url}" style="display: inline-block; background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Commencer mes achats
                        </a>
                    </p>
                    
                    <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                        Si vous avez des questions, n'hésitez pas à contacter notre support client.
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 TechStore. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)

