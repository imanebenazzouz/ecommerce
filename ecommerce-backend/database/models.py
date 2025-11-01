"""
Modèles SQLAlchemy pour PostgreSQL.

Chaque modèle documente son rôle et ses relations pour faciliter la maintenance
et l'évolution du schéma. Les timestamps sont en UTC via datetime.utcnow.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, UTC

def utcnow():
    return datetime.now(UTC)

Base = declarative_base()

class User(Base):
    """Utilisateur de l'application.

    - `is_admin`: contrôle des accès admin
    - Relation 1:N avec `Order`
    - Relation 1:1 avec `Cart`
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    
    # Relations
    orders = relationship("Order", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)

class Product(Base):
    """Produit vendable dans le catalogue.

    - `active`: indique la disponibilité
    - Relations vers items de panier et de commande
    """
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price_cents = Column(Integer, nullable=False)
    stock_qty = Column(Integer, nullable=False, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    
    # Relations
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

class Cart(Base):
    """Panier d'un utilisateur (1:1 avec `User`)."""
    __tablename__ = "carts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relations
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    """Article dans un panier (N:1 `Cart`, N:1 `Product`)."""
    __tablename__ = "cart_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    """Commande utilisateur.

    Les colonnes `*_at` tracent le cycle de vie: création, validation,
    expédition, livraison, annulation, remboursement.
    """
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False, default="CREE")
    created_at = Column(DateTime, default=utcnow, nullable=False)
    validated_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    refunded_at = Column(DateTime)
    payment_id = Column(UUID(as_uuid=True))
    invoice_id = Column(UUID(as_uuid=True))
    
    # Relations
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery = relationship("Delivery", back_populates="order", uselist=False)
    
    def total_cents(self) -> int:
        """Calcule le total de la commande en centimes."""
        return sum(item.unit_price_cents * item.quantity for item in self.items)

class OrderItem(Base):
    """Ligne d'une commande, avec snapshot du nom/prix au moment de l'achat."""
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    name = Column(String(255), nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Relations
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Delivery(Base):
    """Informations de livraison associées à une commande (1:1)."""
    __tablename__ = "deliveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, unique=True)
    transporteur = Column(String(100), nullable=False)
    tracking_number = Column(String(100), nullable=True)  # Rendre optionnel
    address = Column(Text, nullable=False)
    delivery_status = Column(String(50), nullable=False, default="PREPAREE")
    created_at = Column(DateTime, default=utcnow)
    
    # Relations
    order = relationship("Order", back_populates="delivery")

class Invoice(Base):
    """Facture émise pour une commande et un utilisateur."""
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    total_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    # Relations
    order = relationship("Order")
    user = relationship("User")

class Payment(Base):
    """Paiement enregistré pour une commande.

    Les champs `card_last4`, `postal_code`, etc. stockent un minimum d'infos
    non sensibles pour suivi et génération de facture.
    """
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    payment_method = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Informations de paiement détaillées
    card_last4 = Column(String(4), nullable=True)  # 4 derniers chiffres de la carte
    postal_code = Column(String(5), nullable=True)
    phone = Column(String(10), nullable=True)
    street_number = Column(String(10), nullable=True)
    street_name = Column(String(100), nullable=True)  # Nom de rue
    
    # Relations
    order = relationship("Order")

class MessageThread(Base):
    """Fil de discussion de support (lié à un utilisateur et optionnellement une commande)."""
    __tablename__ = "message_threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)  # Ajouter order_id
    subject = Column(String(255), nullable=False)
    closed = Column(Boolean, default=False)  # Utiliser closed au lieu de status
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relations
    user = relationship("User")
    order = relationship("Order")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

class Message(Base):
    """Message dans un fil de support. `author_user_id` None signifie message admin."""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("message_threads.id"), nullable=False)
    author_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Rendre optionnel pour les messages admin
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    # Relations
    thread = relationship("MessageThread", back_populates="messages")
    author = relationship("User")

class PasswordResetToken(Base):
    """Token de réinitialisation de mot de passe.
    
    - Token unique généré pour chaque demande de réinitialisation
    - Expiration après 1 heure pour la sécurité
    - Lié à un utilisateur via user_id
    - used: indique si le token a déjà été utilisé
    """
    __tablename__ = "password_reset_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    
    # Relations
    user = relationship("User")
