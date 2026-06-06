import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# Ensure a directory exists to save our generated documents
os.makedirs("generated_docs", exist_ok=True)

def generate_invoice_pdf(po_number: str, vendor_name: str, rfq_title: str, quantity: int, unit_price: float, tax_rate: float = 0.18):
    """
    Generates a professional PDF Invoice locally using ReportLab.
    No shortcuts taken here—this builds a properly styled financial document.
    """
    filename = f"generated_docs/Invoice_{po_number}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # --- HEADER ---
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "VendorBridge ERP")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 65, "Automated Procurement System")
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(450, height - 50, "INVOICE")
    
    # --- DOCUMENT INFO ---
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 120, f"Vendor: {vendor_name}")
    c.drawString(50, height - 140, f"Reference RFQ: {rfq_title}")
    
    c.drawString(400, height - 120, f"PO Number: {po_number}")
    c.drawString(400, height - 140, "Terms: Net 30")

    # --- FINANCIAL MATH ---
    subtotal = quantity * unit_price
    tax_amount = subtotal * tax_rate
    grand_total = subtotal + tax_amount

    # --- LINE ITEMS TABLE ---
    data = [
        ["Description", "Qty", "Unit Price", "Total"],
        [rfq_title, str(quantity), f"Rs. {unit_price:.2f}", f"Rs. {subtotal:.2f}"],
        ["", "", "Subtotal:", f"Rs. {subtotal:.2f}"],
        ["", "", f"GST ({(tax_rate*100):.0f}%):", f"Rs. {tax_amount:.2f}"],
        ["", "", "GRAND TOTAL:", f"Rs. {grand_total:.2f}"]
    ]

    table = Table(data, colWidths=[250, 50, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (2, 4), (3, 4), 'Helvetica-Bold'), # Bold the Grand Total
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 300)

    # --- FOOTER ---
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Generated securely by VendorBridge Offline Engine.")
    
    c.save()
    return filename