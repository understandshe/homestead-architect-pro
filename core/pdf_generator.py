"""
PDF Report Generator - PROFESSIONAL
With affiliate products on pages 6-7
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from io import BytesIO
from typing import Dict, Any, List

from core.watermark_system import PDFWatermark


class PDFGenerator:
    """Generates professional PDF reports with affiliate marketing"""
    
    # Sample affiliate products (replace with real ones)
    AFFILIATE_PRODUCTS = [
        {
            'name': 'Premier 1 Supplies Electric Fence Kit',
            'description': 'Complete solar-powered electric fencing system for goats and poultry. 1-mile coverage, 0.5 joule output.',
            'price': '$299',
            'cta_level': 'high',
            'url': 'https://amazon.com/dp/B08XXXXX?tag=chundalgardens-20',
            'why': 'Essential for predator protection in your 0.23 acre homestead'
        },
        {
            'name': 'Little Giant Automatic Chicken Waterer',
            'description': '3.5 gallon capacity, automatic refill system. Reduces daily maintenance by 80%.',
            'price': '$45',
            'cta_level': 'medium',
            'url': 'https://amazon.com/dp/B00XXXXX?tag=chundalgardens-20',
            'why': 'Perfect for your 50-bird chicken coop design'
        },
        {
            'name': 'VIVOSUN Greenhouse 10x8 ft',
            'description': 'Heavy-duty walk-in greenhouse with reinforced cover and steel frame. 4-season growing.',
            'price': '$189',
            'cta_level': 'high',
            'url': 'https://amazon.com/dp/B07XXXXX?tag=chundalgardens-20',
            'why': 'Matches your Zone 1 kitchen garden perfectly'
        },
        {
            'name': 'Farm Innovators Heated Water Bucket',
            'description': '5-gallon heated bucket, thermostatically controlled. Prevents freezing in winter.',
            'price': '$65',
            'cta_level': 'medium',
            'url': 'https://amazon.com/dp/B01XXXXX?tag=chundalgardens-20',
            'why': 'Critical for your borewell water system in cold months'
        },
        {
            'name': 'Solar Powered Water Pump Kit',
            'description': '12V DC pump, 100W solar panel included. 3.2 GPM flow rate, 230ft lift.',
            'price': '$249',
            'cta_level': 'high',
            'url': 'https://amazon.com/dp/B09XXXXX?tag=chundalgardens-20',
            'why': 'Ideal for your 150ft borewell to irrigate 4000 sq.ft pasture'
        },
        {
            'name': 'Tarter Farm & Ranch Gate',
            'description': 'Heavy-duty 12 ft steel tube gate, powder coated. Complete with hinges and latch.',
            'price': '$179',
            'cta_level': 'medium',
            'url': 'https://amazon.com/dp/B06XXXXX?tag=chundalgardens-20',
            'why': 'Professional entry for your buffer zone'
        }
    ]
    
    def create(self, layout_data: Dict[str, Any], watermark_enabled: bool,
               map_image_buffer: BytesIO = None) -> BytesIO:
        """Generate complete professional PDF report"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=50, leftMargin=50,
            topMargin=50, bottomMargin=30
        )
        
        styles = getSampleStyleSheet()
        
        # Custom professional styles
        title_style = ParagraphStyle(
            'Title', parent=styles['Heading1'],
            fontSize=22, textColor=HexColor('#1B5E20'),
            spaceAfter=20, alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'Heading', parent=styles['Heading2'],
            fontSize=14, textColor=HexColor('#2E7D32'),
            spaceAfter=10, spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'SubHeading', parent=styles['Heading3'],
            fontSize=12, textColor=HexColor('#388E3C'),
            spaceAfter=8, fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'Body', parent=styles['BodyText'],
            fontSize=10, alignment=TA_JUSTIFY,
            spaceAfter=8, leading=14
        )
        
        disclaimer_style = ParagraphStyle(
            'Disclaimer', parent=styles['BodyText'],
            fontSize=8, textColor=HexColor('#D32F2F'),
            alignment=TA_JUSTIFY, spaceAfter=10,
            borderWidth=1, borderColor=HexColor('#FFCDD2'),
            borderPadding=8, backColor=HexColor('#FFEBEE')
        )
        
        affiliate_title_style = ParagraphStyle(
            'AffiliateTitle', parent=styles['Heading1'],
            fontSize=18, textColor=HexColor('#E65100'),
            spaceAfter=15, alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        affiliate_box_style = ParagraphStyle(
            'AffiliateBox', parent=styles['Normal'],
            fontSize=10, textColor=HexColor('#333'),
            spaceAfter=12, borderWidth=2,
            borderColor=HexColor('#FF9800'),
            borderPadding=10, backColor=HexColor('#FFF3E0')
        )
        
        story = []
        
        # ========== PAGE 1: COVER & PROJECT INFO ==========
        story.append(Paragraph("HOMESTEAD ARCHITECT PRO", title_style))
        story.append(Paragraph("Professional Site Plan Report | 2026 Edition", 
                              ParagraphStyle('Subtitle', parent=body_style, 
                                           alignment=TA_CENTER, textColor=HexColor('#666'))))
        story.append(Spacer(1, 0.3*inch))
        
        # Project details box
        project_title = f"<b>Project:</b> {layout_data.get('project_name', 'My Homestead')}"
        story.append(Paragraph(project_title, heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Disclaimer
        disclaimer = (
            "<b>IMPORTANT DISCLAIMER:</b> This report is generated for informational purposes only. "
            "All cost estimates, income projections, and recommendations are approximate and may vary "
            "based on local conditions, market rates, and individual circumstances. Consult with "
            "qualified agricultural experts, financial advisors, and local authorities before making "
            "financial commitments. chundalgardens.com assumes no liability for decisions made "
            "based on this report."
        )
        story.append(Paragraph(disclaimer, disclaimer_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Project specifications table
        data = [
            ['PARAMETER', 'VALUE', 'NOTES'],
            ['Total Area', f"{layout_data.get('total_sqft', 0):,} sq.ft.", 
             f"~{layout_data.get('acres', 0):.2f} acres"],
            ['Plot Dimensions', f"{layout_data['dimensions']['L']:.0f}' × {layout_data['dimensions']['W']:.0f}'",
             'As per survey'],
            ['Homestead Category', layout_data.get('category', 'Unknown').upper(),
             'Based on total area'],
            ['House Position', layout_data.get('house_position', 'Unknown'),
             'Affects solar gain'],
            ['Primary Water', layout_data.get('water_source', 'Unknown'),
             'Borewell depth: 150ft'],
            ['Terrain Slope', layout_data.get('slope', 'Flat'),
             'Drainage consideration'],
            ['Climate Zone', 'Tropical', 'Monsoon pattern'],
        ]
        
        t = Table(data, colWidths=[2.2*inch, 2*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1B5E20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#E8F5E9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t)
        
        # ========== PAGE 2: SITE MAP ==========
        story.append(PageBreak())
        story.append(Paragraph("SITE PLAN & ZONING", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        if map_image_buffer:
            map_image_buffer.seek(0)
            img = Image(map_image_buffer, width=7*inch, height=5.25*inch)
            story.append(img)
        
        story.append(Spacer(1, 0.2*inch))
        
        # Zone analysis
        story.append(Paragraph("Permaculture Zone Analysis", subheading_style))
        
        zone_data = [['ZONE', 'FUNCTION', 'AREA', '% OF TOTAL', 'KEY FEATURES']]
        zone_names = {
            'z0': ('Residential', 'House, solar, compost'),
            'z1': ('Kitchen Garden', 'Daily vegetables, herbs'),
            'z2': ('Food Forest', 'Fruit trees, perennials'),
            'z3': ('Pasture/Crops', 'Grains, fodder, poultry'),
            'z4': ('Buffer', 'Windbreak, privacy, road')
        }
        
        total = layout_data.get('total_sqft', 0)
        for zid, ratio in layout_data.get('zones', {}).items():
            name, features = zone_names.get(zid, (zid, ''))
            zone_data.append([
                zid.upper(),
                name,
                f"{int(total * ratio):,} sq.ft.",
                f"{ratio*100:.0f}%",
                features
            ])
        
        zt = Table(zone_data, colWidths=[0.8*inch, 1.5*inch, 1.2*inch, 0.9*inch, 2.2*inch])
        zt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#C8E6C9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(zt)
        
        # ========== PAGE 3: LIVESTOCK HOUSING ==========
        story.append(PageBreak())
        story.append(Paragraph("LIVESTOCK HOUSING SPECIFICATIONS", heading_style))
        
        features = layout_data.get('features', {})
        
        if 'goat_shed' in features:
            story.append(Paragraph("Goat Housing (10 Animals)", subheading_style))
            goat_specs = [
                ['SPECIFICATION', 'VALUE', 'STANDARD'],
                ['Indoor Space', '150 sq.ft.', '15 sq.ft./animal'],
                ['Outdoor Run', '375 sq.ft.', '2.5× indoor'],
                ['Roof Height', '10 ft', 'Minimum 8 ft'],
                ['Ventilation', '3 windows', '1 per 50 sq.ft.'],
                ['Feeding Trough', '20 ft linear', '2 ft per animal'],
                ['Fence Height', '6 ft', 'Predator-proof'],
            ]
            gt = Table(goat_specs, colWidths=[2*inch, 2*inch, 2.2*inch])
            gt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#8D6E63')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            story.append(gt)
            story.append(Spacer(1, 0.2*inch))
        
        if 'chicken_coop' in features:
            story.append(Paragraph("Poultry Housing (50 Birds)", subheading_style))
            chicken_specs = [
                ['SPECIFICATION', 'VALUE', 'STANDARD'],
                ['Indoor Space', '100 sq.ft.', '2 sq.ft./bird (free-range)'],
                ['Outdoor Run', '500 sq.ft.', '10 sq.ft./bird'],
                ['Nesting Boxes', '13 units', '1 per 4 hens'],
                ['Roosting Bars', '42 ft', '10 inches per bird'],
                ['Feeders', '5 units', 'Linear access'),
            ]
            ct = Table(chicken_specs, colWidths=[2*inch, 2*inch, 2.2*inch])
            ct.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#F57F17')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            story.append(ct)
        
        # ========== PAGE 4: COST ANALYSIS ==========
        story.append(PageBreak())
        story.append(Paragraph("FINANCIAL ANALYSIS & ROI", heading_style))
        
        # Cost breakdown
        story.append(Paragraph("Investment Breakdown", subheading_style))
        
        cost_data = [
            ['CATEGORY', 'MINIMUM', 'MAXIMUM', 'NOTES'],
            ['Land Preparation', '$500', '$1,500', 'Clearing, leveling'],
            ['Infrastructure', '$2,000', '$5,000', 'Fencing, roads, utilities'],
            ['Livestock Housing', '$1,500', '$3,500', 'Sheds, coops, equipment'],
            ['Initial Stock', '$800', '$2,000', 'Animals, feed, medicine'],
            ['Tools & Equipment', '$300', '$800', 'Hand tools, small machinery'],
            ['Contingency (10%)', '$510', '$1,280', 'Unexpected costs'],
            ['TOTAL INVESTMENT', '$5,610', '$14,080', 'One-time setup'],
        ]
        
        cost_table = Table(cost_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 2.2*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#E3F2FD')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(cost_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ROI Projections
        story.append(Paragraph("Income Projections (Annual)", subheading_style))
        
        income_data = [
            ['SOURCE', 'YEAR 1', 'YEAR 2', 'YEAR 3+'],
            ['Eggs (50 hens)', '$1,200', '$1,800', '$2,000'],
            ['Goat Milk/Meat', '$800', '$1,500', '$2,200'],
            ['Vegetables', '$400', '$800', '$1,200'],
            ['Fruits', '$200', '$600', '$1,000'],
            ['TOTAL', '$2,600', '$4,700', '$6,400'],
        ]
        
        inc_table = Table(income_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        inc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#C8E6C9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(inc_table)
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            "<b>ROI Analysis:</b> Break-even expected in Year 2. Full return on investment "
            "by Year 3-4. Annual operating costs estimated at $1,200-1,800.",
            body_style
        ))
        
        # ========== PAGE 5: IMPLEMENTATION TIMELINE ==========
        story.append(PageBreak())
        story.append(Paragraph("IMPLEMENTATION TIMELINE", heading_style))
        
        phases = [
            ['PHASE', 'DURATION', 'ACTIVITIES', 'PRIORITY'],
            ['Phase 1: Infrastructure', 'Month 1-2', 
             'Fencing, water system, access roads', 'CRITICAL'],
            ['Phase 2: Housing', 'Month 2-3',
             'Livestock sheds, chicken coop, storage', 'HIGH'],
            ['Phase 3: Planting', 'Month 3-4',
             'Zone 1-2 establishment, trees, perennials', 'HIGH'],
            ['Phase 4: Livestock', 'Month 4-5',
             'Purchase animals, quarantine, integration', 'MEDIUM'],
            ['Phase 5: Optimization', 'Month 6-12',
             'System refinement, expansion planning', 'ONGOING'],
        ]
        
        phase_table = Table(phases, colWidths=[1.5*inch, 1.2*inch, 3*inch, 1*inch])
        phase_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#6A1B9A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(phase_table)
        
        # ========== PAGE 6-7: AFFILIATE PRODUCTS (YOUR REQUIREMENT) ==========
        story.append(PageBreak())
        story.append(Paragraph("RECOMMENDED EQUIPMENT & SUPPLIES", affiliate_title_style))
        story.append(Paragraph(
            "Based on your homestead design, we've selected these professional-grade "
            "products to help you succeed faster. These are affiliate links - we earn "
            "a small commission at no extra cost to you.",
            ParagraphStyle('AffiliateNote', parent=body_style, 
                         alignment=TA_CENTER, textColor=HexColor('#666'),
                         fontSize=9, spaceAfter=15)
        ))
        
        # Product 1-2 on Page 6
        for i, product in enumerate(self.AFFILIATE_PRODUCTS[:3], 1):
            story.append(self._create_product_box(product, i))
            story.append(Spacer(1, 0.15*inch))
        
        # Page 7 - More products
        story.append(PageBreak())
        story.append(Paragraph("MORE ESSENTIAL EQUIPMENT", affiliate_title_style))
        story.append(Spacer(1, 0.1*inch))
        
        for i, product in enumerate(self.AFFILIATE_PRODUCTS[3:], 4):
            story.append(self._create_product_box(product, i))
            story.append(Spacer(1, 0.15*inch))
        
        # Disclaimer
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            "<i>Product recommendations are based on homestead size, climate, and livestock "
            "type. Prices subject to change. Always verify specifications before purchase. "
            "chundalgardens.com is a participant in the Amazon Services LLC Associates Program.</i>",
            ParagraphStyle('FinePrint', parent=body_style, fontSize=8, 
                         textColor=HexColor('#999'), alignment=TA_CENTER)
        ))
        
        # Build PDF
        def get_watermark():
            return PDFWatermark.add_visible_watermark if watermark_enabled else PDFWatermark.add_protection_watermark
        
        doc.build(story, onFirstPage=get_watermark(), onLaterPages=get_watermark())
        
        buffer.seek(0)
        return buffer
    
    def _create_product_box(self, product: Dict, number: int) -> Paragraph:
        """Create formatted affiliate product box"""
        cta_colors = {
            'high': '#D32F2F',  # Red for high priority
            'medium': '#F57C00',  # Orange for medium
            'low': '#388E3C'  # Green for low
        }
        
        cta_texts = {
            'high': '⭐ HIGHLY RECOMMENDED - Get Best Price',
            'medium': '✓ Recommended - Check Availability',
            'low': 'Learn More'
        }
        
        color = cta_colors.get(product.get('cta_level', 'medium'), '#F57C00')
        cta = cta_texts.get(product.get('cta_level', 'medium'), 'Learn More')
        
        html = f"""
        <table width="100%" border="1" bordercolor="{color}" cellpadding="10" 
               bgcolor="#FFF3E0" cellspacing="0">
            <tr>
                <td>
                    <b><font size="12" color="{color}">#{number} {product['name']}</font></b><br/>
                    <font size="10"><b>Price:</b> {product['price']}</font><br/>
                    <font size="9">{product['description']}</font><br/>
                    <font size="9" color="#2E7D32"><i>Why we recommend: {product['why']}</i></font><br/>
                    <br/>
                    <font size="10" color="{color}"><b>&gt;&gt; {cta}</b></font><br/>
                    <font size="8" color="#666">{product['url']}</font>
                </td>
            </tr>
        </table>
        """
        
        return Paragraph(html, ParagraphStyle('Product', parent=None, spaceAfter=10))
