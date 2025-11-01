"""
Service d'envoi d'emails avec Brevo (ex-Sendinblue).

Configuration requise:
- BREVO_API_KEY: Clé API Brevo (à obtenir sur https://app.brevo.com)
- SENDER_EMAIL: Email expéditeur vérifié dans Brevo
- SENDER_NAME: Nom de l'expéditeur
- FRONTEND_URL: URL du frontend pour les liens de réinitialisation

Pour obtenir une clé API Brevo:
1. Créer un compte sur https://app.brevo.com (gratuit)
2. Aller dans "SMTP & API" > "API Keys"
3. Créer une nouvelle clé API
4. Copier la clé dans BREVO_API_KEY
"""

import os
import requests
from typing import Optional


class EmailService:
    """Service d'envoi d'emails via l'API Brevo."""
    
    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY", "")
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@techstore.com")
        self.sender_name = os.getenv("SENDER_NAME", "TechStore")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        self.api_url = "https://api.brevo.com/v3/smtp/email"
        
        # Mode développement si pas de clé API
        self.dev_mode = not self.api_key or self.api_key == ""
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Envoie un email via Brevo.
        
        Args:
            to_email: Email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
            
        Returns:
            True si l'email a été envoyé avec succès, False sinon
        """
        if self.dev_mode:
            print(f"\n{'='*60}")
            print(f"📧 MODE DÉVELOPPEMENT - Email non envoyé")
            print(f"{'='*60}")
            print(f"À: {to_email}")
            print(f"Sujet: {subject}")
            print(f"Contenu:\n{html_content}")
            print(f"{'='*60}\n")
            return True
        
        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }
        
        payload = {
            "sender": {
                "name": self.sender_name,
                "email": self.sender_email
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_email.split("@")[0]
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code in (200, 201):
                print(f"✅ Email envoyé avec succès à {to_email}")
                return True
            else:
                print(f"❌ Erreur lors de l'envoi de l'email: {response.status_code}")
                print(f"Réponse: {response.text}")
                return False
                
        except Exception as e:
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

