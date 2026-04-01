"""
Watermark System - chundalgardens.com
FIXED VERSION - Crop error resolved
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Union


class WatermarkEngine:
    """
    Professional watermarking with two modes
    """
    
    WATERMARK_TEXT = "chundalgardens.com"
    
    @classmethod
    def apply_visible_watermark(cls, image_buffer: io.BytesIO, 
                                opacity: float = 0.15, 
                                rotation: int = 30) -> io.BytesIO:
        """
        MODE 1: User checks "Add Watermark"
        Large diagonal watermark across entire image
        """
        img = Image.open(image_buffer).convert("RGBA")
        width, height = img.size
        
        # Create transparent overlay
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate font size
        font_size = int(min(width, height) * 0.08)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Calculate text size
        bbox = draw.textbbox((0, 0), cls.WATERMARK_TEXT, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Create large canvas for rotation
        diagonal = int(np.sqrt(width**2 + height**2)) + 200
        large_overlay = Image.new("RGBA", (diagonal, diagonal), (0, 0, 0, 0))
        large_draw = ImageDraw.Draw(large_overlay)
        
        # Draw watermarks
        center = diagonal // 2
        spacing = text_height * 3
        
        positions = [
            (center, center),
            (center, center - spacing),
            (center, center + spacing),
        ]
        
        for px, py in positions:
            large_draw.text(
                (px - text_width//2, py - text_height//2),
                cls.WATERMARK_TEXT,
                font=font,
                fill=(128, 128, 128, int(255 * opacity))
            )
        
        # Rotate
        rotated = large_overlay.rotate(rotation, expand=True)
        
        # FIXED: Proper centering and sizing
        # Calculate position to center rotated image on original
        paste_x = (width - rotated.width) // 2
        paste_y = (height - rotated.height) // 2
        
        # Create final overlay matching original size
        final_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Paste rotated image, handling boundaries
        # Only paste visible portion
        x1 = max(0, paste_x)
        y1 = max(0, paste_y)
        x2 = min(width, paste_x + rotated.width)
        y2 = min(height, paste_y + rotated.height)
        
        # Calculate source coordinates in rotated image
        src_x1 = max(0, -paste_x)
        src_y1 = max(0, -paste_y)
        src_x2 = src_x1 + (x2 - x1)
        src_y2 = src_y1 + (y2 - y1)
        
        if x2 > x1 and y2 > y1:  # Valid region
            region = rotated.crop((src_x1, src_y1, src_x2, src_y2))
            final_overlay.paste(region, (x1, y1))
        
        # Composite
        result = Image.alpha_composite(img, final_overlay)
        
        # Convert to RGB
        final = Image.new("RGB", (width, height), (255, 255, 255))
        final.paste(result, mask=result.split()[3] if result.mode == 'RGBA' else None)
        
        # Save
        output = io.BytesIO()
        final.save(output, format='PNG', quality=95)
        output.seek(0)
        return output
    
    @classmethod
    def apply_protection_watermark(cls, image_buffer: io.BytesIO) -> io.BytesIO:
        """
        MODE 2: User unchecks watermark
        Small corner watermarks, survives cropping
        """
        img = Image.open(image_buffer).convert("RGBA")
        width, height = img.size
        
        draw = ImageDraw.Draw(img)
        
        # Small font
        font_size = max(8, int(min(width, height) * 0.015))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # 16 Strategic positions
        positions = [
            (width * 0.02, height * 0.02),
            (width * 0.98, height * 0.02),
            (width * 0.02, height * 0.98),
            (width * 0.98, height * 0.98),
            (width * 0.50, height * 0.02),
            (width * 0.50, height * 0.98),
            (width * 0.02, height * 0.50),
            (width * 0.98, height * 0.50),
            (width * 0.25, height * 0.25),
            (width * 0.75, height * 0.25),
            (width * 0.25, height * 0.75),
            (width * 0.75, height * 0.75),
            (width * 0.33, height * 0.02),
            (width * 0.66, height * 0.02),
            (width * 0.33, height * 0.98),
            (width * 0.66, height * 0.98),
        ]
        
        for x, y in positions:
            # Shadow
            draw.text((x+1, y+1), cls.WATERMARK_TEXT, font=font, 
                     fill=(100, 100, 100, 30))
            # Main
            draw.text((x, y), cls.WATERMARK_TEXT, font=font, 
                     fill=(150, 150, 150, 60))
        
        # Convert to RGB
        final = Image.new("RGB", (width, height), (255, 255, 255))
        final.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
        
        output = io.BytesIO()
        final.save(output, format='PNG', quality=95)
        output.seek(0)
        return output


class PDFWatermark:
    """PDF watermark implementation"""
    
    WATERMARK_TEXT = "chundalgardens.com"
    
    @staticmethod
    def add_visible_watermark(canvas, doc):
        """Large diagonal watermark"""
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
    def add_protection_watermark(canvas, doc):
        """Small corner watermarks"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor
        
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(HexColor('#999999'))
        
        positions = [
            (40, 40), (A4[0]/2, 40), (A4[0]-40, 40),
            (40, A4[1]/2), (A4[0]-40, A4[1]/2),
            (40, A4[1]-40), (A4[0]/2, A4[1]-40), (A4[0]-40, A4[1]-40),
        ]
        
        for x, y in positions:
            canvas.drawCentredString(x, y, PDFWatermark.WATERMARK_TEXT)
        
        canvas.restoreState()
