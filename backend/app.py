from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import pandas as pd # Make sure this is at the top of app.py if not already
import hashlib
from database import engine, get_db
import models
import schemas
from fastapi.responses import FileResponse
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engines.pdf_generator import generate_invoice_pdf

# Spin up base DB architecture tables 
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VendorBridge ERP Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- USER CREATION & AUTH ---
@app.post("/users/", response_model=schemas.UserResponse, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # In production, use bcrypt or passlib here. For development, simple mock hashing:
    fake_hashed_password = user.password + "scrambled"
    
    new_user = models.User(email=user.email, password_hash=fake_hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- VENDOR REGISTRATION ---
@app.post("/vendors/", response_model=schemas.VendorResponse, tags=["Vendors"])
def register_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    db_vendor = db.query(models.Vendor).filter(models.Vendor.gst_number == vendor.gst_number).first()
    if db_vendor:
        raise HTTPException(status_code=400, detail="GST number already exists in system")
    
    new_vendor = models.Vendor(**vendor.model_dump())
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor
@app.get("/vendors/", response_model=List[schemas.VendorResponse], tags=["Vendors"])
def get_all_vendors(db: Session = Depends(get_db)):
    """Fetch all approved vendors for the directory."""
    return db.query(models.Vendor).all()

# --- RFQ LOGIC ---
@app.post("/rfqs/", response_model=schemas.RFQResponse, tags=["Procurement"])
def create_rfq(rfq: schemas.RFQCreate, creator_id: int, db: Session = Depends(get_db)):
    new_rfq = models.RFQ(**rfq.model_dump(), creator_id=creator_id, status="Draft")
    db.add(new_rfq)
    db.commit()
    db.refresh(new_rfq)
    return new_rfq

@app.get("/rfqs/", response_model=List[schemas.RFQResponse], tags=["Procurement"])
def list_rfqs(db: Session = Depends(get_db)):
    return db.query(models.RFQ).all()

# --- VENDOR QUOTATION SUBMISSION ---
@app.post("/quotations/", response_model=schemas.QuotationResponse, tags=["Procurement"])
def submit_quotation(quote: schemas.QuotationCreate, vendor_id: int, db: Session = Depends(get_db)):
    target_rfq = db.query(models.RFQ).filter(models.RFQ.id == quote.rfq_id).first()
    if not target_rfq:
        raise HTTPException(status_code=404, detail="RFQ target not found")
    if target_rfq.status != "Open":
        raise HTTPException(status_code=400, detail="RFQ is not accepting bids currently")

    new_quote = models.Quotation(**quote.model_dump(), vendor_id=vendor_id, status="Submitted")
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote


# --- QUOTATION RETRIEVAL ---
@app.get("/rfqs/{rfq_id}/quotations/", tags=["Procurement"])
def get_rfq_quotations(rfq_id: int, db: Session = Depends(get_db)):
    """Fetch all quotations submitted for a specific RFQ."""
    quotes = db.query(models.Quotation).filter(models.Quotation.rfq_id == rfq_id).all()
    
    # We will stitch the vendor name into the response for easier frontend display
    result = []
    for q in quotes:
        vendor = db.query(models.Vendor).filter(models.Vendor.id == q.vendor_id).first()
        result.append({
            "id": q.id,
            "vendor_name": vendor.name if vendor else "Unknown",
            "health_score": vendor.health_score if vendor else 0,
            "unit_price": q.unit_price,
            "delivery_days": q.delivery_days,
            "remarks": q.remarks
        })
    return result

# --- NOVELTY 1: THE SMART ADVISOR ENGINE ---
@app.get("/engine/advisor/{rfq_id}", tags=["Smart Engines"])
def run_vendor_advisor(rfq_id: int, db: Session = Depends(get_db)):
    """
    Evaluates quotes using a Pandas heuristic algorithm.
    Weights: 60% Price, 20% Delivery Speed, 20% Vendor Health.
    """
    quotes = get_rfq_quotations(rfq_id, db)
    if not quotes:
        return {"status": "error", "recommendation": "No quotations available to analyze."}

    # Load data into a Pandas DataFrame for lightning-fast vector math
    df = pd.DataFrame(quotes)
    
    # Avoid division by zero
    min_price = df['unit_price'].min()
    min_days = df['delivery_days'].min()
    
    # Calculate proprietary "Value Score" (Higher is better)
    # 1. Price factor: (Lowest Price / Their Price) * 60 points
    df['price_score'] = (min_price / df['unit_price']) * 60
    
    # 2. Delivery factor: (Fastest Days / Their Days) * 20 points
    df['delivery_score'] = (min_days / df['delivery_days']) * 20
    
    # 3. Health factor: (Their Score / 5.0 max) * 20 points
    df['health_score_calc'] = (df['health_score'] / 5.0) * 20
    
    df['total_score'] = df['price_score'] + df['delivery_score'] + df['health_score_calc']
    
    # Find the winner
    winner = df.loc[df['total_score'].idxmax()]
    
    recommendation_text = (
        f"🏆 **System Recommendation: {winner['vendor_name']}**\n\n"
        f"**Why:** Achieved the highest Value Index ({winner['total_score']:.1f}/100). "
        f"They offered a unit price of ₹{winner['unit_price']} with a {winner['delivery_days']}-day delivery timeline, "
        f"backed by a vendor health rating of {winner['health_score']}★."
    )
    
    return {"status": "success", "recommendation": recommendation_text, "winner_id": int(winner['id'])}



# --- NOVELTY 3: CRYPTOGRAPHIC AUDIT ENGINE ---
def create_ledger_entry(db: Session, user_id: int, action: str):
    """Generates a tamper-proof SHA-256 hash for the audit trail."""
    # Get the last entry to chain the hashes (like a blockchain)
    last_entry = db.query(models.AuditLedger).order_by(models.AuditLedger.id.desc()).first()
    previous_hash = last_entry.current_hash if last_entry else "0000000000000000000000000000000000000000000000000000000000000000"
    
    # Create the new hash payload
    payload = f"{user_id}-{action}-{previous_hash}-{datetime.now(timezone.utc).isoformat()}"
    current_hash = hashlib.sha256(payload.encode()).hexdigest()
    
    new_entry = models.AuditLedger(
        user_id=user_id,
        action=action,
        previous_hash=previous_hash,
        current_hash=current_hash
    )
    db.add(new_entry)
    db.commit()
    return current_hash

# --- WORKFLOW: APPROVE RFQ ---
@app.post("/rfqs/{rfq_id}/approve", tags=["Workflow"])
def approve_procurement(rfq_id: int, winning_quote_id: int, manager_id: int, remarks: str, db: Session = Depends(get_db)):
    """Locks the RFQ, selects the winning bid, and writes to the crypto ledger."""
    rfq = db.query(models.RFQ).filter(models.RFQ.id == rfq_id).first()
    quote = db.query(models.Quotation).filter(models.Quotation.id == winning_quote_id).first()
    
    if not rfq or not quote:
        raise HTTPException(status_code=404, detail="Target not found")
        
    # State Machine Transitions
    rfq.status = "Approved"
    quote.status = "Selected"
    
    # Reject all other bids for this RFQ
    losing_quotes = db.query(models.Quotation).filter(models.Quotation.rfq_id == rfq_id, models.Quotation.id != winning_quote_id).all()
    for lq in losing_quotes:
        lq.status = "Rejected"
        
    # Write to Immutable Ledger
    action_text = f"APPROVED RFQ #{rfq_id} | WINNER: Quote #{winning_quote_id} | REMARKS: {remarks}"
    create_ledger_entry(db, manager_id, action_text)
    
    db.commit()
    return {"status": "Success", "message": "Procurement locked and cryptographically secured."}
# --- PO & INVOICE GENERATION ---
@app.post("/generate-po/{rfq_id}", tags=["Fulfillment"])
def generate_purchase_order(rfq_id: int, db: Session = Depends(get_db)):
    """Generates the official PO and Invoice document based on an approved RFQ."""
    rfq = db.query(models.RFQ).filter(models.RFQ.id == rfq_id).first()
    
    if rfq.status != "Approved":
        raise HTTPException(status_code=400, detail="Cannot generate PO. RFQ is not approved.")
        
    winning_quote = db.query(models.Quotation).filter(
        models.Quotation.rfq_id == rfq.id, 
        models.Quotation.status == "Selected"
    ).first()
    
    vendor = db.query(models.Vendor).filter(models.Vendor.id == winning_quote.vendor_id).first()
    
    # Generate unique PO Number
    po_number = f"PO-2026-{rfq_id:04d}"
    
    # Call our local ReportLab engine
    filepath = generate_invoice_pdf(
        po_number=po_number,
        vendor_name=vendor.name,
        rfq_title=rfq.title,
        quantity=rfq.quantity,
        unit_price=winning_quote.unit_price
    )
    
    # Update RFQ status to Closed/Completed
    rfq.status = "Closed"
    db.commit()
    
    return {"status": "Success", "po_number": po_number, "file_path": filepath}

@app.get("/download-invoice/{po_number}", tags=["Fulfillment"])
def download_invoice(po_number: str):
    """Serves the generated PDF to the frontend."""
    filepath = f"generated_docs/Invoice_{po_number}.pdf"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type='application/pdf', filename=f"{po_number}.pdf")
    raise HTTPException(status_code=404, detail="Invoice file not found.")