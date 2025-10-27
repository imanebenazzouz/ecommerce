"""
Tests unitaires pour les fonctions de validation backend
"""
import pytest
import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))

from utils.validations import (
    sanitize_numeric,
    validate_luhn,
    validate_card_number,
    validate_cvv,
    validate_expiry_month,
    validate_expiry_year,
    validate_expiry_date,
    validate_postal_code,
    validate_phone,
    validate_street_number,
    validate_quantity
)


class TestSanitizeNumeric:
    """Tests pour sanitize_numeric"""

    def test_remove_non_numeric(self):
        assert sanitize_numeric('abc123def456') == '123456'
        assert sanitize_numeric('4242-4242-4242-4242') == '4242424242424242'
        assert sanitize_numeric('4242 4242 4242 4242') == '4242424242424242'
        assert sanitize_numeric('Hello World 123') == '123'

    def test_empty_string_for_non_string(self):
        assert sanitize_numeric(None) == ''
        assert sanitize_numeric(123) == ''

    def test_no_digits(self):
        assert sanitize_numeric('abcdef') == ''
        assert sanitize_numeric('---') == ''


class TestValidateLuhn:
    """Tests pour l'algorithme de Luhn"""

    def test_valid_card_numbers(self):
        # Numéros de test Stripe valides
        assert validate_luhn('4242424242424242') is True
        assert validate_luhn('5555555555554444') is True
        assert validate_luhn('378282246310005') is True  # Amex

    def test_invalid_card_numbers(self):
        assert validate_luhn('4242424242424241') is False  # Dernier chiffre incorrect
        assert validate_luhn('1234567890123456') is False
        assert validate_luhn('0000000000000000') is False

    def test_card_numbers_with_spaces_dashes(self):
        assert validate_luhn('4242-4242-4242-4242') is True
        assert validate_luhn('4242 4242 4242 4242') is True


class TestValidateCardNumber:
    """Tests pour validate_card_number"""

    def test_valid_card_numbers(self):
        is_valid, error = validate_card_number('4242424242424242')
        assert is_valid is True
        assert error == ''

        is_valid, error = validate_card_number('5555555555554444')
        assert is_valid is True
        assert error == ''

    def test_wrong_length(self):
        is_valid, error = validate_card_number('42424242')  # Trop court
        assert is_valid is False
        assert '13 à 19' in error

        is_valid, error = validate_card_number('42424242424242424242')  # Trop long
        assert is_valid is False

    def test_fails_luhn_check(self):
        is_valid, error = validate_card_number('4242424242424241')
        assert is_valid is False
        assert 'invalide' in error

    def test_with_spaces(self):
        is_valid, error = validate_card_number('4242 4242 4242 4242')
        assert is_valid is True


class TestValidateCVV:
    """Tests pour validate_cvv"""

    def test_valid_cvv_3_digits(self):
        is_valid, error = validate_cvv('123')
        assert is_valid is True
        assert error == ''

    def test_valid_cvv_4_digits(self):
        is_valid, error = validate_cvv('1234')
        assert is_valid is True
        assert error == ''

    def test_wrong_length(self):
        is_valid, error = validate_cvv('12')
        assert is_valid is False
        assert 'CVV' in error

        is_valid, error = validate_cvv('12345')
        assert is_valid is False

    def test_non_numeric(self):
        is_valid, error = validate_cvv('12a')
        assert is_valid is False


class TestValidateExpiryMonth:
    """Tests pour validate_expiry_month"""

    def test_valid_months(self):
        assert validate_expiry_month(1)[0] is True
        assert validate_expiry_month(12)[0] is True
        assert validate_expiry_month(6)[0] is True

    def test_invalid_months(self):
        assert validate_expiry_month(0)[0] is False
        assert validate_expiry_month(13)[0] is False
        assert validate_expiry_month(99)[0] is False

    def test_non_integer(self):
        is_valid, error = validate_expiry_month('12')
        assert is_valid is False


class TestValidateExpiryYear:
    """Tests pour validate_expiry_year"""

    def test_valid_years(self):
        assert validate_expiry_year(2025)[0] is True
        assert validate_expiry_year(2030)[0] is True
        assert validate_expiry_year(2099)[0] is True

    def test_invalid_years(self):
        assert validate_expiry_year(1999)[0] is False  # Trop ancien
        assert validate_expiry_year(2101)[0] is False  # Trop loin
        assert validate_expiry_year(123)[0] is False    # Format incorrect

    def test_non_integer(self):
        is_valid, error = validate_expiry_year('2025')
        assert is_valid is False


class TestValidateExpiryDate:
    """Tests pour validate_expiry_date"""

    def test_valid_future_date(self):
        is_valid, error = validate_expiry_date(12, 2030)
        assert is_valid is True
        assert error == ''

    def test_past_date(self):
        is_valid, error = validate_expiry_date(1, 2020)
        assert is_valid is False
        assert 'invalide' in error

    def test_invalid_month(self):
        is_valid, error = validate_expiry_date(13, 2030)
        assert is_valid is False

    def test_invalid_year(self):
        is_valid, error = validate_expiry_date(12, 1999)
        assert is_valid is False


class TestValidatePostalCode:
    """Tests pour validate_postal_code"""

    def test_valid_postal_codes(self):
        assert validate_postal_code('75001')[0] is True
        assert validate_postal_code('13000')[0] is True
        assert validate_postal_code('69007')[0] is True

    def test_invalid_postal_codes(self):
        is_valid, error = validate_postal_code('7500')  # Trop court
        assert is_valid is False
        assert '5 chiffres' in error

        is_valid, error = validate_postal_code('750011')  # Trop long
        assert is_valid is False

        is_valid, error = validate_postal_code('7500a')  # Lettre
        assert is_valid is False

    def test_with_spaces(self):
        is_valid, error = validate_postal_code('75 001')
        assert is_valid is True  # Sanitization appliquée


class TestValidatePhone:
    """Tests pour validate_phone"""

    def test_valid_phone_numbers(self):
        assert validate_phone('0612345678')[0] is True
        assert validate_phone('0123456789')[0] is True

    def test_invalid_phone_numbers(self):
        is_valid, error = validate_phone('061234567')  # Trop court
        assert is_valid is False
        assert '10 chiffres' in error

        is_valid, error = validate_phone('06123456789')  # Trop long
        assert is_valid is False

        is_valid, error = validate_phone('061234567a')  # Lettre
        assert is_valid is False

    def test_with_spaces(self):
        is_valid, error = validate_phone('06 12 34 56 78')
        assert is_valid is True  # Sanitization appliquée


class TestValidateStreetNumber:
    """Tests pour validate_street_number"""

    def test_valid_street_numbers(self):
        assert validate_street_number('1')[0] is True
        assert validate_street_number('123')[0] is True
        assert validate_street_number('9999')[0] is True

    def test_invalid_street_numbers(self):
        is_valid, error = validate_street_number('')
        assert is_valid is False
        assert 'chiffres uniquement' in error

        is_valid, error = validate_street_number('abc')
        assert is_valid is False

        is_valid, error = validate_street_number('12a')
        assert is_valid is False


class TestValidateQuantity:
    """Tests pour validate_quantity"""

    def test_valid_quantities(self):
        assert validate_quantity(1)[0] is True
        assert validate_quantity(10)[0] is True
        assert validate_quantity(100)[0] is True

    def test_invalid_quantities(self):
        is_valid, error = validate_quantity(0)
        assert is_valid is False
        assert 'invalide' in error

        is_valid, error = validate_quantity(-1)
        assert is_valid is False

        is_valid, error = validate_quantity('abc')
        assert is_valid is False


class TestValidationMessages:
    """Tests pour vérifier que tous les messages sont en français"""

    def test_all_error_messages_in_french(self):
        """Vérifier que tous les messages d'erreur sont en français"""
        # Tester quelques validations et vérifier qu'il n'y a pas de messages en anglais
        _, error = validate_card_number('1234')
        assert error != ''
        assert 'chiffres' in error or 'invalide' in error

        _, error = validate_cvv('12')
        assert error != ''
        assert 'CVV' in error and 'chiffres' in error

        _, error = validate_postal_code('123')
        assert error != ''
        assert 'postal' in error and 'chiffres' in error

        _, error = validate_phone('123')
        assert error != ''
        assert 'téléphone' in error and 'chiffres' in error

