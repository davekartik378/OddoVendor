from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# --- AUTHENTICATION SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    role: str = Field(..., description="Role must be Admin, Manager, Procurement Officer, or Vendor")

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- VENDOR SCHEMAS ---
class VendorCreate(BaseModel):
    name: str = Field(..., min_length=1)
    gst_number: str = Field(..., min_length=15, max_length=15, description="GST must be exactly 15 characters")
    contact_email: EmailStr
    category: str

class VendorResponse(VendorCreate):
    id: int
    health_score: float

    class Config:
        from_attributes = True

# --- RFQ SCHEMAS ---
class RFQCreate(BaseModel):
    title: str = Field(..., min_length=3)
    product_details: str
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")
    deadline: datetime

class RFQResponse(RFQCreate):
    id: int
    creator_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- QUOTATION SCHEMAS ---
class QuotationCreate(BaseModel):
    rfq_id: int
    unit_price: float = Field(..., gt=0)
    delivery_days: int = Field(..., gt=0)
    remarks: Optional[str] = None

class QuotationResponse(QuotationCreate):
    id: int
    vendor_id: int
    status: str

    class Config:
        from_attributes = True