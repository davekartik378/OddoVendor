from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import pandas as pd
import hashlib
import os
import sys
from dotenv import load_dotenv                 # FIX B08: load .env config
from database import engine, get_db
import models
import schemas
from fastapi.responses import FileResponse

load_dotenv()                                  # reads backend/.env into os.environ

sys.path.append(os.path.dirname(__file__))     # FIX B13: engines/ is inside backend/
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
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """bcrypt password hashing — production-grade."""   # FIX B10
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

@app.post("/users/", response_model=schemas.UserResponse, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", tags=["Users"])
def login(email: str, password: str, db: Session = Depends(get_db)):
    """Validates credentials and returns user info for session."""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"id": user.id, "email": user.email, "role": user.role}

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
    """Fetch all vendors for the directory."""
    return db.query(models.Vendor).all()

@app.patch("/vendors/{vendor_id}/health-score", tags=["Vendors"])
def update_vendor_health_score(vendor_id: int, score: float, db: Session = Depends(get_db)):
    """Manually adjust a vendor's health score (Admin use). Score must be 1.0–5.0."""
    if not (1.0 <= score <= 5.0):
        raise HTTPException(status_code=400, detail="Score must be between 1.0 and 5.0")
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    vendor.health_score = round(score, 2)
    db.commit()
    db.refresh(vendor)
    return {"vendor_id": vendor_id, "name": vendor.name, "health_score": vendor.health_score}

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

    # FIX B11: update vendor health scores so the Smart Advisor has real signal
    # Winner: +0.1 per win (capped at 5.0), Losers: -0.05 per loss (floor at 1.0)
    winning_vendor = db.query(models.Vendor).filter(models.Vendor.id == quote.vendor_id).first()
    if winning_vendor:
        winning_vendor.health_score = min(5.0, round(winning_vendor.health_score + 0.1, 2))
    for lq in losing_quotes:
        losing_vendor = db.query(models.Vendor).filter(models.Vendor.id == lq.vendor_id).first()
        if losing_vendor:
            losing_vendor.health_score = max(1.0, round(losing_vendor.health_score - 0.05, 2))
        
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

    # Calculate totals (18% GST)
    subtotal   = winning_quote.unit_price * rfq.quantity
    tax_amount = round(subtotal * 0.18, 2)
    total      = round(subtotal + tax_amount, 2)

    # Call our local ReportLab engine
    filepath = generate_invoice_pdf(
        po_number=po_number,
        vendor_name=vendor.name,
        rfq_title=rfq.title,
        quantity=rfq.quantity,
        unit_price=winning_quote.unit_price
    )

    # FIX B07: persist PurchaseOrder to DB so analytics and total_pos are accurate
    existing_po = db.query(models.PurchaseOrder).filter(
        models.PurchaseOrder.po_number == po_number
    ).first()
    if not existing_po:
        new_po = models.PurchaseOrder(
            quotation_id=winning_quote.id,
            po_number=po_number,
            total_amount=total,
            tax_amount=tax_amount,
            status="Generated",
        )
        db.add(new_po)

    # Update RFQ status to Closed/Completed
    rfq.status = "Closed"
    db.commit()

    return {"status": "Success", "po_number": po_number, "file_path": filepath, "total": total}

@app.get("/download-invoice/{po_number}", tags=["Fulfillment"])
def download_invoice(po_number: str):
    """Serves the generated PDF to the frontend."""
    filepath = f"generated_docs/Invoice_{po_number}.pdf"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type='application/pdf', filename=f"{po_number}.pdf")
    raise HTTPException(status_code=404, detail="Invoice file not found.")

# --- RFQ STATUS UPDATE (Publish Draft → Open) ---
@app.patch("/rfqs/{rfq_id}/status", tags=["Procurement"])
def update_rfq_status(rfq_id: int, new_status: str, db: Session = Depends(get_db)):
    """Updates the status of an RFQ. Used to publish a Draft to Open."""
    rfq = db.query(models.RFQ).filter(models.RFQ.id == rfq_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    rfq.status = new_status
    db.commit()
    db.refresh(rfq)
    return {"status": "success", "rfq_id": rfq_id, "new_status": new_status}


# --- SEND INVOICE VIA EMAIL ---
@app.post("/send-invoice/{po_number}", tags=["Fulfillment"])
def send_invoice_email(po_number: str, recipient_email: str):
    """Sends the generated invoice PDF to a recipient email via SMTP."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders

    filepath = f"generated_docs/Invoice_{po_number}.pdf"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Invoice PDF not found. Generate PO first.")

    # FIX B08: read from .env — never hardcode credentials
    SMTP_SERVER   = os.environ.get("SMTP_SERVER",   "smtp.gmail.com")
    SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
    SENDER_EMAIL  = os.environ.get("SMTP_EMAIL",    "")
    SENDER_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise HTTPException(
            status_code=503,
            detail="Email not configured. Add SMTP_EMAIL and SMTP_PASSWORD to backend/.env"
        )

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"VendorBridge — Invoice {po_number}"

        body = f"""Dear Vendor,

Please find attached the official Purchase Order & Invoice document: {po_number}.

This document has been generated and authorized through the VendorBridge ERP system.

Regards,
VendorBridge Procurement Team"""
        msg.attach(MIMEText(body, 'plain'))

        with open(filepath, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="Invoice_{po_number}.pdf"')
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())

        return {"status": "success", "message": f"Invoice sent to {recipient_email}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email failed: {str(e)}")


# --- AUDIT LEDGER RETRIEVAL ---
@app.get("/audit-logs/", tags=["Activity"])
def get_audit_logs(db: Session = Depends(get_db)):
    """Returns full audit ledger for the Activity Logs page."""
    logs = db.query(models.AuditLedger).order_by(models.AuditLedger.id.desc()).all()
    result = []
    for log in logs:
        result.append({
            "id":            log.id,
            "user_id":       log.user_id,
            "action":        log.action,
            "timestamp":     log.timestamp.isoformat() if log.timestamp else "",
            "current_hash":  log.current_hash[:16] + "…",   # truncated for display
            "previous_hash": log.previous_hash[:16] + "…",
        })
    return result


# --- ANALYTICS ENGINE ---
@app.get("/analytics/summary", tags=["Analytics"])
def get_analytics_summary(db: Session = Depends(get_db)):
    """Aggregated procurement statistics for the Reports page."""
    rfqs       = db.query(models.RFQ).all()
    vendors    = db.query(models.Vendor).all()
    quotations = db.query(models.Quotation).all()
    pos        = db.query(models.PurchaseOrder).all()

    # Status breakdown
    status_counts = {}
    for r in rfqs:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1

    # Monthly RFQ trend (last 6 months)
    from collections import defaultdict
    monthly = defaultdict(int)
    for r in rfqs:
        if r.created_at:
            key = r.created_at.strftime("%b %Y")
            monthly[key] += 1

    # Vendor spend — sum of (unit_price * rfq.quantity) for Selected quotations
    vendor_spend = defaultdict(float)
    for q in quotations:
        if q.status == "Selected":
            rfq = db.query(models.RFQ).filter(models.RFQ.id == q.rfq_id).first()
            vendor = db.query(models.Vendor).filter(models.Vendor.id == q.vendor_id).first()
            if rfq and vendor:
                spend = q.unit_price * rfq.quantity
                vendor_spend[vendor.name] += spend

    # Category distribution
    cat_counts = defaultdict(int)
    for v in vendors:
        cat_counts[v.category] += 1

    # Top vendor by health score
    top_vendor = max(vendors, key=lambda v: v.health_score, default=None)

    return {
        "total_rfqs":      len(rfqs),
        "total_vendors":   len(vendors),
        "total_quotations": len(quotations),
        "total_pos":       len(pos),
        "status_breakdown": status_counts,
        "monthly_trend":   dict(monthly),
        "vendor_spend":    dict(vendor_spend),
        "category_dist":   dict(cat_counts),
        "top_vendor":      {"name": top_vendor.name, "score": top_vendor.health_score} if top_vendor else None,
        "avg_health_score": round(sum(v.health_score for v in vendors) / len(vendors), 2) if vendors else 0,
    }
