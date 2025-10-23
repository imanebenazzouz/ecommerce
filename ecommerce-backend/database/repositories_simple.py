"""
Repositories PostgreSQL simplifiés
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .models import (
    User, Product, Cart, CartItem, Order, OrderItem, 
    Delivery, Invoice, Payment, MessageThread, Message
)
from enums import OrderStatus, DeliveryStatus
from datetime import datetime

class PostgreSQLUserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_data: Dict[str, Any]) -> User:
        """Crée un nouvel utilisateur"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par ID"""
        return self.db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(self) -> List[User]:
        """Récupère tous les utilisateurs"""
        return self.db.query(User).all()
    
    def update(self, user: User) -> User:
        """Met à jour un utilisateur"""
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: str) -> bool:
        """Supprime un utilisateur"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True

class PostgreSQLProductRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, product_data: Dict[str, Any]) -> Product:
        """Crée un nouveau produit"""
        product = Product(**product_data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Récupère un produit par ID"""
        return self.db.query(Product).filter(Product.id == uuid.UUID(product_id)).first()
    
    def get_all(self) -> List[Product]:
        """Récupère tous les produits"""
        return self.db.query(Product).all()
    
    def get_all_active(self) -> List[Product]:
        """Récupère tous les produits actifs"""
        return self.db.query(Product).filter(Product.active == True).all()
    
    def update(self, product: Product) -> Product:
        """Met à jour un produit"""
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete(self, product_id: str) -> bool:
        """Supprime complètement un produit et tous ses éléments associés"""
        try:
            # Récupérer le produit
            product = self.get_by_id(product_id)
            if not product:
                return False
            
            # Supprimer tous les éléments de panier associés à ce produit
            from database.models import CartItem, OrderItem
            self.db.query(CartItem).filter(CartItem.product_id == uuid.UUID(product_id)).delete()
            
            # Supprimer tous les éléments de commande associés à ce produit
            # (les commandes sont des archives, donc on supprime les références)
            self.db.query(OrderItem).filter(OrderItem.product_id == uuid.UUID(product_id)).delete()
            
            # Supprimer le produit lui-même
            self.db.delete(product)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Réserve du stock pour un produit"""
        product = self.get_by_id(product_id)
        if not product or product.stock_qty < quantity:
            return False
        
        product.stock_qty -= quantity
        self.db.commit()
        return True
    
    def release_stock(self, product_id: str, quantity: int) -> bool:
        """Libère du stock pour un produit"""
        product = self.get_by_id(product_id)
        if not product:
            return False
        
        product.stock_qty += quantity
        self.db.commit()
        return True

class PostgreSQLCartRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_user_id(self, user_id: str) -> Optional[Cart]:
        """Récupère le panier d'un utilisateur"""
        return self.db.query(Cart).filter(Cart.user_id == uuid.UUID(user_id)).first()
    
    def create_cart(self, user_id: str) -> Cart:
        """Crée un panier pour un utilisateur"""
        cart = Cart(user_id=uuid.UUID(user_id))
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart
    
    def add_item(self, user_id: str, product_id: str, quantity: int) -> bool:
        """Ajoute un article au panier"""
        try:
            cart = self.get_by_user_id(user_id)
            if not cart:
                cart = self.create_cart(user_id)
            
            # Vérifier si l'article existe déjà
            existing_item = self.db.query(CartItem).filter(
                and_(
                    CartItem.cart_id == cart.id,
                    CartItem.product_id == uuid.UUID(product_id)
                )
            ).first()
            
            if existing_item:
                existing_item.quantity += quantity
            else:
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=uuid.UUID(product_id),
                    quantity=quantity
                )
                self.db.add(cart_item)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Erreur add_item: {e}")
            return False
    
    def remove_item(self, user_id: str, product_id: str, quantity: int) -> bool:
        """Retire un article du panier"""
        try:
            cart = self.get_by_user_id(user_id)
            if not cart:
                return False
            
            cart_item = self.db.query(CartItem).filter(
                and_(
                    CartItem.cart_id == cart.id,
                    CartItem.product_id == uuid.UUID(product_id)
                )
            ).first()
            
            if not cart_item:
                return False
            
            if quantity == 0:
                # Supprimer complètement l'article
                self.db.delete(cart_item)
            else:
                # Réduire la quantité
                cart_item.quantity -= quantity
                if cart_item.quantity <= 0:
                    self.db.delete(cart_item)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Erreur remove_item: {e}")
            return False
    
    def clear_cart(self, user_id: str) -> bool:
        """Vide complètement le panier de l'utilisateur"""
        try:
            cart = self.get_by_user_id(user_id)
            if not cart:
                return False
            
            # Supprimer tous les éléments du panier
            self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Erreur clear_cart: {e}")
            return False
    
    def clear(self, user_id: str) -> bool:
        """Alias pour clear_cart"""
        return self.clear_cart(user_id)

class PostgreSQLOrderRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, order_data: Dict[str, Any]) -> Order:
        """Crée une nouvelle commande"""
        order = Order(
            user_id=uuid.UUID(order_data["user_id"]),
            status=order_data.get("status", OrderStatus.CREE)
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        # Créer les articles de commande
        for item_data in order_data.get("items", []):
            order_item = OrderItem(
                order_id=order.id,
                product_id=uuid.UUID(item_data["product_id"]),
                name=item_data["name"],
                unit_price_cents=item_data["unit_price_cents"],
                quantity=item_data["quantity"]
            )
            self.db.add(order_item)
        
        self.db.commit()
        return order
    
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Récupère une commande par ID"""
        return self.db.query(Order).filter(Order.id == uuid.UUID(order_id)).first()
    
    def get_by_user_id(self, user_id: str) -> List[Order]:
        """Récupère les commandes d'un utilisateur"""
        return self.db.query(Order).filter(Order.user_id == uuid.UUID(user_id)).all()
    
    def get_all(self) -> List[Order]:
        """Récupère toutes les commandes"""
        return self.db.query(Order).all()
    
    def update_status(self, order_id: str, status: OrderStatus) -> bool:
        """Met à jour le statut d'une commande"""
        order = self.get_by_id(order_id)
        if not order:
            return False
        
        order.status = status
        
        # Mettre à jour les timestamps selon le statut
        now = datetime.utcnow()
        if status == OrderStatus.VALIDEE:
            order.validated_at = now
        elif status == OrderStatus.EXPEDIEE:
            order.shipped_at = now
        elif status == OrderStatus.LIVREE:
            order.delivered_at = now
        elif status == OrderStatus.ANNULEE:
            order.cancelled_at = now
        elif status == OrderStatus.REMBOURSEE:
            order.refunded_at = now
        
        self.db.commit()
        return True
    
    def update(self, order: Order) -> Order:
        """Met à jour une commande"""
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def add_item(self, item_data: Dict[str, Any]) -> OrderItem:
        """Ajoute un article à une commande"""
        order_item = OrderItem(
            order_id=uuid.UUID(item_data["order_id"]),
            product_id=uuid.UUID(item_data["product_id"]),
            name=item_data["name"],
            unit_price_cents=item_data["unit_price_cents"],
            quantity=item_data["quantity"]
        )
        self.db.add(order_item)
        self.db.commit()
        self.db.refresh(order_item)
        return order_item

class PostgreSQLInvoiceRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, invoice_data: Dict[str, Any]) -> Invoice:
        """Crée une nouvelle facture"""
        invoice = Invoice(**invoice_data)
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    def get_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """Récupère une facture par ID"""
        return self.db.query(Invoice).filter(Invoice.id == uuid.UUID(invoice_id)).first()
    
    def get_by_order_id(self, order_id: str) -> Optional[Invoice]:
        """Récupère une facture par ID de commande"""
        return self.db.query(Invoice).filter(Invoice.order_id == uuid.UUID(order_id)).first()

class PostgreSQLPaymentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, payment_data: Dict[str, Any]) -> Payment:
        """Crée un nouveau paiement"""
        payment = Payment(**payment_data)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        """Récupère un paiement par ID"""
        return self.db.query(Payment).filter(Payment.id == uuid.UUID(payment_id)).first()
    
    def get_by_order_id(self, order_id: str) -> List[Payment]:
        """Récupère les paiements d'une commande"""
        return self.db.query(Payment).filter(Payment.order_id == uuid.UUID(order_id)).all()

class PostgreSQLThreadRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, thread_data: Dict[str, Any]) -> MessageThread:
        """Crée un nouveau fil de discussion"""
        thread = MessageThread(**thread_data)
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        return thread
    
    def get_by_id(self, thread_id: str) -> Optional[MessageThread]:
        """Récupère un fil par ID"""
        return self.db.query(MessageThread).filter(MessageThread.id == uuid.UUID(thread_id)).first()
    
    def get_by_user_id(self, user_id: str) -> List[MessageThread]:
        """Récupère les fils d'un utilisateur"""
        return self.db.query(MessageThread).filter(MessageThread.user_id == uuid.UUID(user_id)).all()
    
    def get_all(self) -> List[MessageThread]:
        """Récupère tous les fils"""
        return self.db.query(MessageThread).all()
    
    def add_message(self, thread_id: str, message_data: Dict[str, Any]) -> Message:
        """Ajoute un message à un fil"""
        message = Message(
            thread_id=uuid.UUID(thread_id),
            author_user_id=uuid.UUID(message_data["author_user_id"]) if message_data.get("author_user_id") else None,
            content=message_data["content"]
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
