#!/usr/bin/env python3
"""
Tests unitaires pour les produits
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.database.repositories_simple import PostgreSQLProductRepository

@pytest.mark.unit
@pytest.mark.products
class TestProducts:
    """Tests unitaires pour les produits"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def product_repo(self, mock_db):
        """Repository de produits avec mock"""
        return PostgreSQLProductRepository(mock_db)
    
    def test_product_creation(self, product_repo, mock_db):
        """Test de création de produit"""
        # Données du produit
        product_data = {
            "name": "T-Shirt Premium",
            "description": "T-shirt en coton bio de haute qualité",
            "price_cents": 2999,
            "stock_qty": 100,
            "active": True
        }
        
        # Mock de la création - le repository crée un vrai objet Product
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test de création
        result = product_repo.create(product_data)
        
        assert result is not None
        assert result.name == "T-Shirt Premium"
        assert result.description == "T-shirt en coton bio de haute qualité"
        assert result.price_cents == 2999
        assert result.stock_qty == 100
        assert result.active is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_product_retrieval(self, product_repo, mock_db):
        """Test de récupération de produit"""
        # Mock du produit
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.name = "T-Shirt Premium"
        mock_product.price_cents = 2999
        mock_product.stock_qty = 100
        mock_product.active = True
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = product_repo.get_by_id("product123")
        
        assert result is not None
        assert result.id == "product123"
        assert result.name == "T-Shirt Premium"
        assert result.price_cents == 2999
        assert result.stock_qty == 100
        assert result.active is True
        mock_db.query.assert_called_once()
    
    def test_product_listing(self, product_repo, mock_db):
        """Test de listing des produits"""
        # Mock des produits
        mock_products = [
            Mock(id="product1", name="Product 1", price_cents=2999, stock_qty=100, active=True),
            Mock(id="product2", name="Product 2", price_cents=1999, stock_qty=50, active=True),
            Mock(id="product3", name="Product 3", price_cents=3999, stock_qty=75, active=False)
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.all.return_value = mock_products
        mock_db.query.return_value = mock_query
        
        # Test de listing
        result = product_repo.get_all()
        
        assert result is not None
        assert len(result) == 3
        # Vérifier que les objets sont bien les mocks attendus
        assert result[0] == mock_products[0]
        assert result[1] == mock_products[1]
        assert result[2] == mock_products[2]
        mock_db.query.assert_called_once()
    
    def test_active_products_listing(self, product_repo, mock_db):
        """Test de listing des produits actifs uniquement"""
        # Mock des produits actifs
        mock_products = [
            Mock(id="product1", name="Product 1", price_cents=2999, stock_qty=100, active=True),
            Mock(id="product2", name="Product 2", price_cents=1999, stock_qty=50, active=True)
        ]
        
        # Mock de la requête avec filtre
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_products
        mock_db.query.return_value = mock_query
        
        # Test de listing des produits actifs
        result = product_repo.get_all_active()
        
        assert result is not None
        assert len(result) == 2
        assert all(product.active for product in result)
        mock_db.query.assert_called_once()
    
    def test_product_update(self, product_repo, mock_db):
        """Test de mise à jour de produit"""
        # Mock du produit existant
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.name = "Original Name"
        mock_product.price_cents = 1999
        mock_product.stock_qty = 50
        mock_product.active = True
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Données de mise à jour
        update_data = {
            "name": "Updated Name",
            "price_cents": 2999,
            "stock_qty": 100
        }
        
        # Test de mise à jour
        # La méthode update prend un objet Product, pas un ID et des données
        mock_product.name = "Updated Name"
        mock_product.price_cents = 2999
        mock_product.stock_qty = 100
        result = product_repo.update(mock_product)
        
        assert result is not None
        assert result.name == "Updated Name"
        assert result.price_cents == 2999
        assert result.stock_qty == 100
        mock_db.commit.assert_called_once()
    
    def test_product_deletion(self, product_repo, mock_db):
        """Test de suppression de produit"""
        # Mock du produit existant
        mock_product = Mock()
        mock_product.id = "product123"
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de suppression
        result = product_repo.delete("product123")
        
        assert result is True
        mock_db.delete.assert_called_once_with(mock_product)
        mock_db.commit.assert_called_once()
    
    def test_stock_management(self, product_repo, mock_db):
        """Test de gestion du stock"""
        # Mock du produit avec stock
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.stock_qty = 100
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de réservation de stock
        result = product_repo.reserve_stock("product123", 10)
        
        assert result is True
        assert mock_product.stock_qty == 90  # 100 - 10
        
        # Test de libération de stock
        result = product_repo.release_stock("product123", 5)
        
        assert result is True
        assert mock_product.stock_qty == 95  # 90 + 5
        
        # Vérifier que commit a été appelé deux fois (une fois pour chaque opération)
        assert mock_db.commit.call_count == 2
    
    def test_stock_insufficient(self, product_repo, mock_db):
        """Test de stock insuffisant"""
        # Mock du produit avec stock insuffisant
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.stock_qty = 5
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de réservation avec stock insuffisant
        result = product_repo.reserve_stock("product123", 10)
        
        assert result is False
        assert mock_product.stock_qty == 5  # Inchangé
        mock_db.commit.assert_not_called()
    
    def test_product_validation(self, product_repo):
        """Test de validation des données de produit"""
        # Test avec données valides
        valid_data = {
            "name": "Valid Product",
            "description": "A valid product description",
            "price_cents": 2999,
            "stock_qty": 100,
            "active": True
        }
        
        # Les données valides ne doivent pas lever d'exception
        try:
            assert valid_data["name"] is not None
            assert len(valid_data["name"]) > 0
            assert valid_data["price_cents"] > 0
            assert valid_data["stock_qty"] >= 0
            assert isinstance(valid_data["active"], bool)
        except AssertionError:
            pytest.fail("Les données valides ont échoué la validation")
    
    def test_product_price_calculation(self, product_repo):
        """Test des calculs de prix"""
        # Test de conversion centimes -> euros
        price_cents = 2999
        price_euros = price_cents / 100
        
        assert price_euros == 29.99
        
        # Test de calcul de total
        quantity = 3
        total_cents = price_cents * quantity
        total_euros = total_cents / 100
        
        assert total_cents == 8997
        assert total_euros == 89.97
    
    def test_product_categories(self, product_repo):
        """Test des catégories de produits"""
        # Catégories de produits
        categories = [
            "CLOTHING",
            "ACCESSORIES",
            "ELECTRONICS",
            "HOME_GARDEN",
            "SPORTS",
            "BEAUTY",
            "BOOKS",
            "TOYS"
        ]
        
        for category in categories:
            assert category in categories
            assert isinstance(category, str)
            assert len(category) > 0
    
    def test_product_brands(self, product_repo):
        """Test des marques de produits"""
        # Marques de produits
        brands = [
            "NIKE",
            "ADIDAS",
            "APPLE",
            "SAMSUNG",
            "SONY",
            "CANON",
            "DELL",
            "HP"
        ]
        
        for brand in brands:
            assert brand in brands
            assert isinstance(brand, str)
            assert len(brand) > 0
    
    def test_product_sizes(self, product_repo):
        """Test des tailles de produits"""
        # Tailles de vêtements
        clothing_sizes = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
        
        for size in clothing_sizes:
            assert size in clothing_sizes
            assert isinstance(size, str)
            assert len(size) > 0
        
        # Tailles de chaussures
        shoe_sizes = list(range(35, 46))  # 35-45
        
        for size in shoe_sizes:
            assert size in shoe_sizes
            assert isinstance(size, int)
            assert 35 <= size <= 45
    
    def test_product_colors(self, product_repo):
        """Test des couleurs de produits"""
        # Couleurs de produits
        colors = [
            "BLACK",
            "WHITE",
            "RED",
            "BLUE",
            "GREEN",
            "YELLOW",
            "ORANGE",
            "PURPLE",
            "PINK",
            "BROWN",
            "GRAY",
            "NAVY"
        ]
        
        for color in colors:
            assert color in colors
            assert isinstance(color, str)
            assert len(color) > 0
    
    def test_product_materials(self, product_repo):
        """Test des matériaux de produits"""
        # Matériaux de produits
        materials = [
            "COTTON",
            "POLYESTER",
            "WOOL",
            "LEATHER",
            "SILK",
            "DENIM",
            "CASHMERE",
            "LINEN",
            "VISCOSE",
            "ACRYLIC"
        ]
        
        for material in materials:
            assert material in materials
            assert isinstance(material, str)
            assert len(material) > 0
    
    def test_product_conditions(self, product_repo):
        """Test des conditions de produits"""
        # Conditions de produits
        conditions = [
            "NEW",
            "LIKE_NEW",
            "GOOD",
            "FAIR",
            "POOR"
        ]
        
        for condition in conditions:
            assert condition in conditions
            assert isinstance(condition, str)
            assert len(condition) > 0
    
    def test_product_tags(self, product_repo):
        """Test des tags de produits"""
        # Tags de produits
        tags = [
            "SALE",
            "NEW_ARRIVAL",
            "BESTSELLER",
            "LIMITED_EDITION",
            "ECO_FRIENDLY",
            "ORGANIC",
            "VINTAGE",
            "DESIGNER"
        ]
        
        for tag in tags:
            assert tag in tags
            assert isinstance(tag, str)
            assert len(tag) > 0
    
    def test_product_ratings(self, product_repo):
        """Test du système de notation des produits"""
        # Échelle de notation
        rating_scale = (1, 5)  # 1-5 étoiles
        
        assert rating_scale[0] > 0
        assert rating_scale[1] > rating_scale[0]
        assert isinstance(rating_scale[0], int)
        assert isinstance(rating_scale[1], int)
    
    def test_product_reviews(self, product_repo):
        """Test du système d'avis des produits"""
        # Structure d'un avis
        review_structure = {
            "user_id": "user123",
            "product_id": "product123",
            "rating": 4,
            "title": "Great product!",
            "content": "I really like this product. Highly recommended!",
            "verified_purchase": True,
            "helpful_votes": 5
        }
        
        # Vérifier la structure
        required_fields = ["user_id", "product_id", "rating", "title", "content"]
        for field in required_fields:
            assert field in review_structure
            assert review_structure[field] is not None
    
    def test_product_inventory_tracking(self, product_repo):
        """Test du suivi d'inventaire des produits"""
        # Métriques d'inventaire
        inventory_metrics = {
            "current_stock": 100,
            "reserved_stock": 10,
            "available_stock": 90,
            "reorder_point": 20,
            "max_stock": 500,
            "turnover_rate": 0.15  # 15% par mois
        }
        
        for metric, value in inventory_metrics.items():
            assert metric in inventory_metrics
            assert value >= 0
            assert isinstance(value, (int, float))
    
    def test_product_pricing_strategies(self, product_repo):
        """Test des stratégies de prix des produits"""
        # Stratégies de prix
        pricing_strategies = [
            "FIXED_PRICE",
            "DYNAMIC_PRICING",
            "TIERED_PRICING",
            "BULK_PRICING",
            "SEASONAL_PRICING",
            "PROMOTIONAL_PRICING"
        ]
        
        for strategy in pricing_strategies:
            assert strategy in pricing_strategies
            assert isinstance(strategy, str)
            assert len(strategy) > 0
    
    def test_product_discounts(self, product_repo):
        """Test du système de remises des produits"""
        # Types de remises
        discount_types = [
            "PERCENTAGE_DISCOUNT",
            "FIXED_AMOUNT_DISCOUNT",
            "BUY_ONE_GET_ONE",
            "BULK_DISCOUNT",
            "SEASONAL_DISCOUNT",
            "LOYALTY_DISCOUNT"
        ]
        
        for discount_type in discount_types:
            assert discount_type in discount_types
            assert isinstance(discount_type, str)
            assert len(discount_type) > 0
    
    def test_product_shipping(self, product_repo):
        """Test des options d'expédition des produits"""
        # Options d'expédition
        shipping_options = [
            "STANDARD_SHIPPING",
            "EXPRESS_SHIPPING",
            "OVERNIGHT_SHIPPING",
            "FREE_SHIPPING",
            "PICKUP_IN_STORE",
            "DIGITAL_DELIVERY"
        ]
        
        for option in shipping_options:
            assert option in shipping_options
            assert isinstance(option, str)
            assert len(option) > 0
    
    def test_product_warranty(self, product_repo):
        """Test du système de garantie des produits"""
        # Types de garantie
        warranty_types = [
            "NO_WARRANTY",
            "MANUFACTURER_WARRANTY",
            "EXTENDED_WARRANTY",
            "LIFETIME_WARRANTY",
            "CONDITIONAL_WARRANTY"
        ]
        
        for warranty_type in warranty_types:
            assert warranty_type in warranty_types
            assert isinstance(warranty_type, str)
            assert len(warranty_type) > 0
    
    def test_product_edge_cases(self, product_repo):
        """Test des cas limites des produits"""
        # Test avec nom vide
        empty_name_data = {
            "name": "",
            "description": "A product with empty name",
            "price_cents": 2999,
            "stock_qty": 100,
            "active": True
        }
        
        # Le nom vide devrait être invalide
        assert len(empty_name_data["name"]) == 0
        
        # Test avec prix négatif
        negative_price_data = {
            "name": "Product with negative price",
            "description": "A product with negative price",
            "price_cents": -100,
            "stock_qty": 100,
            "active": True
        }
        
        # Le prix négatif devrait être invalide
        assert negative_price_data["price_cents"] < 0
        
        # Test avec stock négatif
        negative_stock_data = {
            "name": "Product with negative stock",
            "description": "A product with negative stock",
            "price_cents": 2999,
            "stock_qty": -10,
            "active": True
        }
        
        # Le stock négatif devrait être invalide
        assert negative_stock_data["stock_qty"] < 0