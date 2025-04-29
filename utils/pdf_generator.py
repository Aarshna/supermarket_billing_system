 
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import datetime
from config import COMPANY_NAME, COMPANY_ADDRESS, COMPANY_PHONE, COMPANY_EMAIL, CURRENCY_SYMBOL

def generate_receipt(db_manager, invoice_id):
    """Generate a PDF receipt for an invoice"""
    try:
        # Create invoice model to get invoice data
        from models.invoice import Invoice
        invoice_model = Invoice(db_manager)
        
        # Get invoice data
        invoice = invoice_model.get_invoice_by_id(invoice_id)
        
        if not invoice:
            print(f"Invoice {invoice_id} not found")
            return None
            
        # Create directory for receipts if it doesn't exist
        receipts_dir = os.path.join(os.getcwd(), "receipts")
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
            
        # Create PDF filename
        filename = os.path.join(receipts_dir, f"receipt_{invoice['invoice_number']}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        subtitle_style = styles["Heading2"]
        normal_style = styles["Normal"]
        
        # Add company information
        elements.append(Paragraph(COMPANY_NAME, title_style))
        elements.append(Paragraph(COMPANY_ADDRESS, normal_style))
        elements.append(Paragraph(f"Phone: {COMPANY_PHONE}", normal_style))
        elements.append(Paragraph(f"Email: {COMPANY_EMAIL}", normal_style))
        elements.append(Spacer(1, 0.25 * inch))
        
        # Add invoice information
        elements.append(Paragraph("RECEIPT", subtitle_style))
        elements.append(Paragraph(f"Invoice: {invoice['invoice_number']}", normal_style))
        elements.append(Paragraph(f"Date: {invoice['created_at']}", normal_style))
        elements.append(Paragraph(f"Cashier: {invoice['created_by_user']}", normal_style))
        
        # Add customer information if available
        if invoice['customer_name']:
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(Paragraph("Customer:", subtitle_style))
            elements.append(Paragraph(f"Name: {invoice['customer_name']}", normal_style))
            if invoice['customer_phone']:
                elements.append(Paragraph(f"Phone: {invoice['customer_phone']}", normal_style))
        
        elements.append(Spacer(1, 0.25 * inch))
        
        # Add items table
        data = [["Item", "Qty", "Price", "Total"]]
        
        for item in invoice['items']:
            data.append([
                item['product_name'],
                str(item['quantity']),
                f"{CURRENCY_SYMBOL}{item['unit_price']:.2f}",
                f"{CURRENCY_SYMBOL}{item['total_price']:.2f}"
            ])
            
        # Add totals
        data.append(["", "", "Subtotal:", f"{CURRENCY_SYMBOL}{invoice['total_amount']:.2f}"])
        data.append(["", "", "Tax:", f"{CURRENCY_SYMBOL}{invoice['tax_amount']:.2f}"])
        
        if invoice['discount_amount'] > 0:
            data.append(["", "", "Discount:", f"{CURRENCY_SYMBOL}{invoice['discount_amount']:.2f}"])
            
        data.append(["", "", "Total:", f"{CURRENCY_SYMBOL}{invoice['final_amount']:.2f}"])
        
        # Create table
        table = Table(data, colWidths=[3*inch, 0.5*inch, 1*inch, 1*inch])
        
        # Style the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -len(data)+1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        
        # Add payment information
        elements.append(Spacer(1, 0.25 * inch))
        elements.append(Paragraph(f"Payment Method: {invoice['payment_method']}", normal_style))
        elements.append(Paragraph(f"Payment Status: {invoice['payment_status']}", normal_style))
        
        # Add thank you message
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph("Thank you for your purchase!", subtitle_style))
        
        # Build PDF
        doc.build(elements)
        
        return filename
        
    except Exception as e:
        print(f"Error generating receipt: {e}")
        return None

def generate_sales_report(file_path, sales_data, from_date, to_date, total_sales, total_invoices, average_sale):
    """Generate a PDF sales report with the provided data"""
    try:
        #Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize = letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        subtitle_style = styles["Heading2"]
        normal_style = styles["Normal"]

        # Add company information
        elements.append(Paragraph(COMPANY_NAME, title_style))
        elements.append(Spacer(1, 0.25 * inch))

        # Add report title
        elements.append(Paragraph(f"Sales Report: {from_date} to {to_date}", subtitle_style))
        elements.append(Spacer(1, 0.25 * inch))

        # Add sales table
        data = [["Invoice", "Date", "Customer", "Items", "Total", "Payment"]]

        for sale in sales_data:
            data.append([
                sale["invoice_number"],
                sale["created_at"],
                sale["customer_name"] if sale["customer_name"] else "Walk-in Customer",
                str(sale["item_count"]),
                f"{CURRENCY_SYMBOL}{sale['final_amount']:.2f}",
                sale["payment_method"]
            ])

        # Create and style table
        table = Table(data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 0.5*inch, 0.75*inch, 1*inch])
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
        ])
        table.setStyle(table_style)
        elements.append(table)

        # Add summary
        elements.append(Spacer(1, 0.25 * inch))
        elements.append(Paragraph(f"Total Invoices: {total_invoices}", normal_style))
        elements.append(Paragraph(f"Total Sales: {total_sales}", normal_style))
        elements.append(Paragraph(f"Average Sale: {average_sale}", normal_style))

        # Add generation date
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(f"Report generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))

        # Build PDF
        doc.build(elements)
        return True

    except Exception as e:
        print(f"Error generating sales report: {e}")
        return False
