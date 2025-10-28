"""
Utilitaires de validation pour les paiements et données numériques.

Contrats:
- Toutes les fonctions retournent `(is_valid: bool, message: str)` quand applicable
- Les messages d'erreur sont en français (UI cohérente)
- `sanitize_numeric` supprime tous les caractères non numériques
"""
import re
from typing import Tuple


def sanitize_numeric(value: str) -> str:
    """Supprime tous les caractères non numériques d'une chaîne."""
    if not isinstance(value, str):
        return ""
    return re.sub(r'\D', '', value)


def validate_luhn(card_number: str) -> bool:
    """Vérifie un numéro de carte via l'algorithme de Luhn (True si valide)."""
    sanitized = sanitize_numeric(card_number)
    if not sanitized:
        return False
    
    # Rejeter les cartes avec tous les chiffres identiques (0000..., 1111..., etc.)
    if len(set(sanitized)) == 1:
        return False
    
    # Algorithme de Luhn
    total = 0
    is_even = False
    
    # Parcourir de droite à gauche
    for digit_char in reversed(sanitized):
        digit = int(digit_char)
        
        if is_even:
            digit *= 2
            if digit > 9:
                digit -= 9
        
        total += digit
        is_even = not is_even
    
    return total % 10 == 0


def validate_card_number(card_number: str) -> Tuple[bool, str]:
    """Numéro de carte: 13–19 chiffres + Luhn obligatoire."""
    sanitized = sanitize_numeric(card_number)
    
    # Vérifier la longueur (13 à 19 chiffres)
    if not re.match(r'^[0-9]{13,19}$', sanitized):
        return False, "Le numéro de carte doit contenir uniquement des chiffres (13 à 19)."
    
    # Vérifier l'algorithme de Luhn
    if not validate_luhn(sanitized):
        return False, "Le numéro de carte est invalide."
    
    return True, ""


def validate_cvv(cvv: str) -> Tuple[bool, str]:
    """CVV/CVC: 3 ou 4 chiffres."""
    sanitized = sanitize_numeric(cvv)
    
    if not re.match(r'^[0-9]{3,4}$', sanitized):
        return False, "Le CVV doit contenir uniquement des chiffres (3 ou 4)."
    
    return True, ""


def validate_expiry_month(month: int) -> Tuple[bool, str]:
    """Mois d'expiration: entier 1–12."""
    if not isinstance(month, int) or month < 1 or month > 12:
        return False, "Le mois doit être entre 01 et 12."
    
    return True, ""


def validate_expiry_year(year: int) -> Tuple[bool, str]:
    """Année d'expiration: YYYY entre 2000 et 2100 (borne large)."""
    if not isinstance(year, int) or year < 2000 or year > 2100:
        return False, "L'année doit être au format YYYY (entre 2000 et 2100)."
    
    return True, ""


def validate_expiry_date(month: int, year: int) -> Tuple[bool, str]:
    """Date d'expiration complète: doit être dans le futur (>= mois courant)."""
    from datetime import datetime
    
    # Valider le mois
    is_valid_month, error_month = validate_expiry_month(month)
    if not is_valid_month:
        return False, error_month
    
    # Valider l'année
    is_valid_year, error_year = validate_expiry_year(year)
    if not is_valid_year:
        return False, error_year
    
    # Vérifier que la date est dans le futur
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    if year < current_year or (year == current_year and month < current_month):
        return False, "Date d'expiration invalide."
    
    return True, ""


def validate_postal_code(postal_code: str) -> Tuple[bool, str]:
    """Code postal français: 5 chiffres."""
    sanitized = sanitize_numeric(postal_code)
    
    if not re.match(r'^[0-9]{5}$', sanitized):
        return False, "Code postal invalide — 5 chiffres."
    
    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Téléphone FR: 10 chiffres, commence par 01–09."""
    sanitized = sanitize_numeric(phone)
    
    if not re.match(r'^[0-9]{10}$', sanitized):
        return False, "Numéro de téléphone invalide — 10 chiffres."
    
    # Vérifier que le numéro commence par 01 à 09
    if not re.match(r'^0[1-9]', sanitized):
        return False, "Le numéro de téléphone doit commencer par 01 à 09."
    
    return True, ""


def validate_street_number(street_number: str) -> Tuple[bool, str]:
    """Numéro de rue: chiffres uniquement (>= 1 char)."""
    if not isinstance(street_number, str) or not street_number:
        return False, "Numéro de rue : chiffres uniquement."
    
    # Vérifier que la chaîne originale ne contient que des chiffres
    if not re.match(r'^[0-9]+$', street_number):
        return False, "Numéro de rue : chiffres uniquement."
    
    return True, ""


def validate_street_name(street_name: str) -> Tuple[bool, str]:
    """Nom de rue: lettres/chiffres/espaces/tirets/apostrophes, 3–100 caractères."""
    if not street_name or not isinstance(street_name, str):
        return False, "Nom de rue requis."
    
    # Nettoyer les espaces multiples
    cleaned = re.sub(r'\s+', ' ', street_name.strip())
    
    # Vérifier la longueur (3 à 100 caractères)
    if len(cleaned) < 3:
        return False, "Nom de rue trop court (minimum 3 caractères)."
    
    if len(cleaned) > 100:
        return False, "Nom de rue trop long (maximum 100 caractères)."
    
    # Vérifier le format : lettres, espaces, tirets, apostrophes autorisés
    # Autorise aussi les accents français
    if not re.match(r"^[a-zA-ZÀ-ÿ0-9\s'\-\.]+$", cleaned):
        return False, "Nom de rue invalide : lettres, chiffres, espaces, apostrophes et tirets uniquement."
    
    # Vérifier qu'il y a au moins 2 lettres
    if len(re.findall(r'[a-zA-ZÀ-ÿ]', cleaned)) < 2:
        return False, "Nom de rue invalide : au moins 2 lettres requises."
    
    return True, ""


def validate_quantity(quantity: int) -> Tuple[bool, str]:
    """Quantité: entier >= 1."""
    if not isinstance(quantity, int) or quantity < 1:
        return False, "Quantité invalide."
    
    return True, ""

