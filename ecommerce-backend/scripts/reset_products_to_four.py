"""
Script utilitaire: réinitialise les produits à exactement 4 entrées.

Utilisation (dans le dossier ecommerce-backend):
  python -m scripts.reset_products_to_four
"""

from database.database import SessionLocal
from database.models import Product, CartItem, OrderItem


FOUR_PRODUCTS = [
    {
        "name": "MacBook Pro M3",
        "description": "14'' 16 Go / 512 Go",
        "price_cents": 229999,
        "stock_qty": 10,
        "active": True,
    },
    {
        "name": "iPhone 15",
        "description": "128 Go, Noir",
        "price_cents": 99999,
        "stock_qty": 15,
        "active": True,
    },
    {
        "name": "AirPods Pro 2",
        "description": "Réduction de bruit active",
        "price_cents": 27999,
        "stock_qty": 20,
        "active": True,
    },
    {
        "name": "Apple Watch SE",
        "description": "GPS 40mm",
        "price_cents": 29999,
        "stock_qty": 12,
        "active": True,
    },
]


def main():
    db = SessionLocal()
    try:
        # Supprimer les CartItem liés aux produits pour éviter contraintes
        db.query(CartItem).delete()
        db.query(OrderItem).delete()
        db.query(Product).delete()
        db.commit()

        # Insérer 4 produits propres
        for data in FOUR_PRODUCTS:
            p = Product(**data)
            db.add(p)
        db.commit()
        print("✅ Produits réinitialisés à 4 éléments")
    except Exception as e:
        db.rollback()
        print("❌ Erreur:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


