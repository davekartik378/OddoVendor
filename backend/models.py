from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Base class for all models
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50)) # 'Admin', 'Manager', 'Procurement Officer', 'Vendor'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    rfqs: Mapped[List["RFQ"]] = relationship(back_populates="creator")
    audit_logs: Mapped[List["AuditLedger"]] = relationship(back_populates="user")


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id")) # Links to login if vendor logs in
    name: Mapped[str] = mapped_column(String(150))
    gst_number: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    contact_email: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))
    health_score: Mapped[float] = mapped_column(Float, default=5.0) # Base score out of 5.0 for Novelty 1

    # Relationships
    quotations: Mapped[List["Quotation"]] = relationship(back_populates="vendor")


class RFQ(Base):
    __tablename__ = "rfqs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    product_details: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="Draft") # Draft, Open, Under Review, Approved, Closed
    deadline: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    creator: Mapped["User"] = relationship(back_populates="rfqs")
    quotations: Mapped[List["Quotation"]] = relationship(back_populates="rfq")


class Quotation(Base):
    __tablename__ = "quotations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rfq_id: Mapped[int] = mapped_column(ForeignKey("rfqs.id"))
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"))
    
    # Financial & Delivery Data
    unit_price: Mapped[float] = mapped_column(Float)
    delivery_days: Mapped[int] = mapped_column(Integer)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Submitted") # Submitted, Selected, Rejected

    # Relationships
    rfq: Mapped["RFQ"] = relationship(back_populates="quotations")
    vendor: Mapped["Vendor"] = relationship(back_populates="quotations")
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship(back_populates="quotation")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quotation_id: Mapped[int] = mapped_column(ForeignKey("quotations.id"), unique=True)
    po_number: Mapped[str] = mapped_column(String(50), unique=True) # e.g., PO-2026-0001
    total_amount: Mapped[float] = mapped_column(Float)
    tax_amount: Mapped[float] = mapped_column(Float) # Calculated GST
    status: Mapped[str] = mapped_column(String(50), default="Generated") # Generated, Sent
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    quotation: Mapped["Quotation"] = relationship(back_populates="purchase_order")


# NOVELTY 3: Cryptographic Audit Ledger
class AuditLedger(Base):
    __tablename__ = "audit_ledger"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(255)) # e.g., "Manager approved RFQ #12"
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # The Cryptographic Links
    previous_hash: Mapped[str] = mapped_column(String(64)) # SHA-256 hash of the last entry
    current_hash: Mapped[str] = mapped_column(String(64), unique=True) # SHA-256 hash of THIS entry

    # Relationships
    user: Mapped["User"] = relationship(back_populates="audit_logs")