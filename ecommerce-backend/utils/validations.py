"""
Utilitaires de validation pour les paiements et données numériques
Toutes les validations retournent des messages d'erreur en français
"""
import re
from typing import Tuple


def sanitize_numeric(value: str) -> str:
    """
    Nettoie une chaîne en supprimant tous les caractères non numériques
    
    Args:
        value: La chaîne à nettoyer
        
    Returns:
        La chaîne ne contenant que des chiffres
    """
    if not isinstance(value, str):
        return ""
    return re.sub(r'\D', '', value)


def validate_luhn(card_number: str) -> bool:
    """
    Valide un numéro de carte bancaire avec l'algorithme de Luhn
    
    Args:
        card_number: Le numéro de carte (peut contenir espaces/tirets)
        
    Returns:
        True si le numéro est valide selon Luhn
    """
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
    """
    Valide un numéro de carte bancaire (13-19 chiffres + Luhn obligatoire)
    
    Args:
        card_number: Le numéro de carte
        
    Returns:
        Tuple (is_valid, error_message)
    """
    sanitized = sanitize_numeric(card_number)
    
    # Vérifier la longueur (13 à 19 chiffres)
    if not re.match(r'^[0-9]{13,19}$', sanitized):
        return False, "Le numéro de carte doit contenir uniquement des chiffres (13 à 19)."
    
    # Vérifier l'algorithme de Luhn
    if not validate_luhn(sanitized):
        return False, "Le numéro de carte est invalide."
    
    return True, ""


def validate_cvv(cvv: str) -> Tuple[bool, str]:
    """
    Valide un CVV/CVC (3 ou 4 chiffres)
    
    Args:
        cvv: Le code CVV
        
    Returns:
        Tuple (is_valid, error_message)
    """
    sanitized = sanitize_numeric(cvv)
    
    if not re.match(r'^[0-9]{3,4}$', sanitized):
        return False, "Le CVV doit contenir uniquement des chiffres (3 ou 4)."
    
    return True, ""


def validate_expiry_month(month: int) -> Tuple[bool, str]:
    """
    Valide un mois d'expiration (1-12)
    
    Args:
        month: Le mois (1-12)
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not isinstance(month, int) or month < 1 or month > 12:
        return False, "Le mois doit être entre 01 et 12."
    
    return True, ""


def validate_expiry_year(year: int) -> Tuple[bool, str]:
    """
    Valide une année d'expiration (format YYYY >= année actuelle)
    
    Args:
        year: L'année (YYYY)
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not isinstance(year, int) or year < 2000 or year > 2100:
        return False, "L'année doit être au format YYYY (entre 2000 et 2100)."
    
    return True, ""


def validate_expiry_date(month: int, year: int) -> Tuple[bool, str]:
    """
    Valide une date d'expiration complète (doit être postérieure au mois actuel)
    
    Args:
        month: Le mois (1-12)
        year: L'année (YYYY)
        
    Returns:
        Tuple (is_valid, error_message)
    """
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
    """
    Valide un code postal français (5 chiffres)
    
    Args:
        postal_code: Le code postal
        
    Returns:
        Tuple (is_valid, error_message)
    """
    sanitized = sanitize_numeric(postal_code)
    
    if not re.match(r'^[0-9]{5}$', sanitized):
        return False, "Code postal invalide — 5 chiffres."
    
    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Valide un numéro de téléphone français (10 chiffres, commence par 01-09)
    
    Args:
        phone: Le numéro de téléphone
        
    Returns:
        Tuple (is_valid, error_message)
    """
    sanitized = sanitize_numeric(phone)
    
    if not re.match(r'^[0-9]{10}$', sanitized):
        return False, "Numéro de téléphone invalide — 10 chiffres."
    
    # Vérifier que le numéro commence par 01 à 09
    if not re.match(r'^0[1-9]', sanitized):
        return False, "Le numéro de téléphone doit commencer par 01 à 09."
    
    return True, ""


def validate_street_number(street_number: str) -> Tuple[bool, str]:
    """
    Valide un numéro de rue (chiffres uniquement, au moins 1)
    
    Args:
        street_number: Le numéro de rue
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not isinstance(street_number, str) or not street_number:
        return False, "Numéro de rue : chiffres uniquement."
    
    # Vérifier que la chaîne originale ne contient que des chiffres
    if not re.match(r'^[0-9]+$', street_number):
        return False, "Numéro de rue : chiffres uniquement."
    
    return True, ""


def validate_street_name(street_name: str) -> Tuple[bool, str]:
    """
    Valide un nom de rue (lettres, espaces, tirets, apostrophes - 3 à 100 caractères)
    
    Args:
        street_name: Le nom de rue
        
    Returns:
        Tuple (is_valid, error_message)
    """
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
    """
    Valide une quantité (entier >= 1)
    
    Args:
        quantity: La quantité
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not isinstance(quantity, int) or quantity < 1:
        return False, "Quantité invalide."
    
    return True, ""

