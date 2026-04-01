"""
PDF Report Generator - SIMPLIFIED WORKING VERSION
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from io import BytesIO
from typing import Dict, Any, List


class PDFWatermark:
    """PDF watermark"""
    WATERMARK_TEXT = "chundalgardens.com"
    
    @staticmethod
    def add_visible(canvas, doc):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 50)
        canvas.setFillColor(HexColor('#CCCCCC'))
        canvas.translate(A4[0]/2, A4[1]/2)
        canvas.rotate(35)
        canvas.drawCentredString(0, 0, PDFWatermark.WATERMARK_TEXT)
        canvas.restoreState()
    
    @staticmethod
    def add_protection(canvas, doc):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(HexColor('#999999'))
        positions = [(40, 40), (A4[0]-40, 40), (40, A4[1]-40), (A4[0]-40, A4[1]-40)]
        for x, y in positions:
            canvas.drawCentredString(x, y, PDFWatermark.WATERMARK_TEXT)
        canvas.restoreState()


class PDFGenerator:
    """Generate PDF reports"""
    
    # Affiliate products
    PRODUCTS = [
        {
            'name': 'Premier 1 Electric Fence Kit',
            'price': '$299',
            'desc': 'Solar-powered fencing for goats/poultry. 1-mile coverage.',
            'why': 'Essential for predator protection'
        },
        {
            'name': 'Automatic Chicken Waterer',
            'price': '$45',
            'desc': '3.5 gallon, auto-refill. Reduces maintenance 80%.',
            'why': 'Perfect for 50-bird coop'
        },
        {
            'name': 'VIVOSUN Greenhouse 10x8 ft',
            'price': '$189',
            'desc': 'Heavy-duty 4-season greenhouse with steel frame.',
            'why': 'Matches your kitchen garden'
        },
        {
            'name': 'Solar Water Pump Kit',
            'price': '$249',
            'desc': '12V pump with 100W panel. 3.2 GPM, 230ft lift.',
            'why': 'Ideal for your borewell'
        },
        {
            'name': 'Heated Water Bucket',
            'price': '$65',
            'desc': '5-gallon, thermostatically controlled.',
            'why': 'Prevents freezing in winter'
        },
        {
            'name': 'Farm Gate 12 ft',
            'price': '$179',
            'desc': 'Heavy-duty steel tube, powder coated.',
            'why': 'Professional buffer entry'
        }
    ]
    
    def create(self, layout_data: Dict, watermark_enabled: bool, map_buffer=None) -> BytesIO:
        """Create PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=50, leftMargin=50,
            topMargin=50, bottomMargin=30
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'Title', parent=styles['Heading1'],
            fontSize=20, textColor=HexColor('#1B5E20'),
            spaceAfter=15, alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'Heading', parent=styles['Heading2'],
            fontSize=14, textColor=HexColor('#2E7D32'),
            spaceAfter=10
        )
        
        body_style = ParagraphStyle(
            'Body', parent=styles['BodyText'],
            fontSize=10, alignment=TA_JUSTIFY, spaceAfter=8
        )
        
        story = []
        
        # Page 1: Cover
        story.append(Paragraph("HOMESTEAD ARCHITECT PRO", title_style))
        story.append(Paragraph("Professional Site Plan Report | 2026", 
                              ParagraphStyle('sub', parent=body_style, alignment=TA_CENTER)))
        story.append(Spacer(1, 0.2*inch))
        
        # Project info
        story.append(Paragraph(f"<b>Project:</b> {layout_data.get('project_name', 'My Homestead')}", 
                              heading_style))
        
        # Disclaimer
        disc = ("<b>DISCLAIMER:</b> This report is for informational purposes only. "
                "Consult experts before construction. chundalgardens.com assumes no liability.")
        story.append(Paragraph(disc, ParagraphStyle('disc', parent=body_style, 
                                                    textColor=HexColor('#D32F2F'), 
                                                    borderPadding=5)))
        story.append(Spacer(1, 0.2*inch))
        
        # Details table
        data = [
            ['Parameter', 'Value'],
            ['Total Area', f"{layout_data.get('total_sqft', 0):,} sq.ft."],
            ['Category', layout_data.get('category', 'Unknown').title()],
            ['Dimensions', f"{layout_data['dimensions']['L']:.0f}' × {layout_data['dimensions']['W']:.0f}'"],
            ['House Position', layout_data.get('house_position', 'Unknown')],
            ['Water Source', layout_data.get('water_source', 'Unknown')],
        ]
        
        t = Table(data, colWidths=[2.5*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#E8F5E9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(t)
        
        # Page 2: Zone Analysis
        story.append(PageBreak())
        story.append(Paragraph("Zone Analysis", heading_style))
        
        zone_data = [['Zone', 'Description', 'Area (sq.ft.)', 'Percentage']]
        zone_names = {
            'z0': 'Residential', 'z1': 'Kitchen Garden',
            'z2': 'Food Forest', 'z3': 'Pasture/Crops', 'z4': 'Buffer'
        }
        
        total = layout_data.get('total_sqft', 0)
        for zid, ratio in layout_data.get('zones', {}).items():
            zone_data.append([
                zid.upper(),
                zone_names.get(zid, zid),
                f"{int(total * ratio):,}",
                f"{ratio*100:.0f}%"
            ])
        
        zt = Table(zone_data, colWidths=[0.8*inch, 2*inch, 1.5*inch, 1.2*inch])
        zt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#C8E6C9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(zt)
        
        # Page 3: Cost Analysis
        story.append(PageBreak())
        story.append(Paragraph("Financial Analysis", heading_style))
        
        cost_data = [
            ['Category', 'Minimum', 'Maximum'],
            ['Setup Cost', '$5,000', '$15,000'],
            ['Annual Income', '$2,000', '$6,000'],
            ['Annual Expense', '$1,000', '$2,500'],
            ['ROI Timeline', '2-3 years', ''],
        ]
        
        ct = Table(cost_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#E3F2FD')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(ct)
        
        # Page 4-5: Affiliate Products (Pages 6-7 in full version, here 4-5)
        story.append(PageBreak())
        story.append(Paragraph("RECOMMENDED PRODUCTS", 
                              ParagraphStyle('aff', parent=heading_style, 
                                          textColor=HexColor('#E65100'))))
        story.append(Paragraph("Essential equipment for your homestead:", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Products 1-3
        for i, prod in enumerate(self.PRODUCTS[:3], 1):
            story.append(Paragraph(f"<b>#{i} {prod['name']}</b> - {prod['price']}", 
                                  ParagraphStyle('prod', parent=body_style, 
                                                textColor=HexColor('#1B5E20'))))
            story.append(Paragraph(prod['desc'], body_style))
            story.append(Paragraph(f"<i>Why: {prod['why']}</i>", 
                                  ParagraphStyle('why', parent=body_style, 
                                                textColor=HexColor('#2E7D32'))))
            story.append(Spacer(1, 0.1*inch))
        
        # Page 5: More products
        story.append(PageBreak())
        story.append(Paragraph("MORE RECOMMENDED PRODUCTS", 
                              ParagraphStyle('aff2', parent=heading_style, 
                                          textColor=HexColor('#E65100'))))
        story.append(Spacer(1, 0.1*inch))
        
        for i, prod in enumerate(self.PRODUCTS[3:], 4):
            story.append(Paragraph(f"<b>#{i} {prod['name']}</b> - {prod['price']}", 
                                  ParagraphStyle('prod', parent=body_style, 
                                                textColor=HexColor('#1B5E20'))))
            story.append(Paragraph(prod['desc'], body_style))
            story.append(Paragraph(f"<i>Why: {prod['why']}</i>", 
                                  ParagraphStyle('why', parent=body_style, 
                                                textColor=HexColor('#2E7D32'))))
            story.append(Spacer(1, 0.1*inch))
        
        # Footer note
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            "<i>Affiliate disclosure: We earn commission from recommended products. "
            "chundalgardens.com participates in Amazon Associates.</i>",
            ParagraphStyle('foot', parent=body_style, fontSize=8, 
                         textColor=HexColor('#999'), alignment=TA_CENTER)))
        
        # Build with watermark
        watermark_func = PDFWatermark.add_visible if watermark_enabled else PDFWatermark.add_protection
        
        doc.build(story, onFirstPage=watermark_func, onLaterPages=watermark_func)
        
        buffer.seek(0)
        return buffer
