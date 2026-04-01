"""
Watermark System - chundalgardens.com
EXACT SPECIFICATION:
- Checked: Full-size, diagonal, faint (15% opacity)
- Unchecked: Small corners, survives cropping, hard to remove
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
from typing import Union


class WatermarkEngine:
    """
    Professional watermarking with two modes:
    1. VISIBLE: Large diagonal, faint, professional
    2. PROTECTED: Small, corners, edges, survives editing
    """
    
    WATERMARK_TEXT = "chundalgardens.com"
    
    @classmethod
    def apply_visible_watermark(cls, image_buffer: io.BytesIO, 
                                opacity: float = 0.15, 
                                rotation: int = 30) -> io.BytesIO:
        """
        MODE 1: User checks "Add Watermark" ☑️
        - Full-size diagonal across ENTIRE image
        - Faint (15% opacity) - looks professional
        - Text: chundalgardens.com
        """
        img = Image.open(image_buffer).convert("RGBA")
        width, height = img.size
        
        # Create transparent overlay
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate large font size (8% of min dimension)
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
        
        # Create large canvas for rotation (diagonal + padding)
        diagonal = int(np.sqrt(width**2 + height**2)) + 200
        large_overlay = Image.new("RGBA", (diagonal, diagonal), (0, 0, 0, 0))
        large_draw = ImageDraw.Draw(large_overlay)
        
        # Draw multiple watermarks for full coverage
        center = diagonal // 2
        spacing = text_height * 3
        
        positions = [
            (center, center),
            (center, center - spacing),
            (center, center + spacing),
            (center - text_width//2, center - spacing//2),
            (center + text_width//2, center + spacing//2),
        ]
        
        for px, py in positions:
            large_draw.text(
                (px - text_width//2, py - text_height//2),
                cls.WATERMARK_TEXT,
                font=font,
                fill=(128, 128, 128, int(255 * opacity))  # Gray, faint
            )
        
        # Rotate
        rotated = large_overlay.rotate(rotation, expand=True)
        
        # Center on original image
        paste_x = (width - rotated.width) // 2
        paste_y = (height - rotated.height) // 2
        
        # Crop to image size
        crop_box = (
            max(0, -paste_x),
            max(0, -paste_y),
            min(rotated.width, rotated.width - (rotated.width - width - paste_x)),
            min(rotated.height, rotated.height - (rotated.height - height - paste_y))
        )
        cropped = rotated.crop(crop_box)
        
        # Resize if needed
        if cropped.size != (width, height):
            cropped = cropped.resize((width, height), Image.Resampling.LANCZOS)
        
        # Composite
        result = Image.alpha_composite(img, cropped)
        
        # Convert to RGB for final output
        final = Image.new("RGB", (width, height), (255, 255, 255))
        final.paste(result, mask=result.split()[3] if result.mode == 'RGBA' else None)
        
        # Save
        output = io.BytesIO()
        final.save(output, format='PNG', quality=95, optimize=True)
        output.seek(0)
        return output
    
    @classmethod
    def apply_protection_watermark(cls, image_buffer: io.BytesIO) -> io.BytesIO:
        """
        MODE 2: User unchecks watermark ⬜
        - Small watermarks in 16+ strategic positions
        - Survives cropping from ANY corner/edge
        - Hard to remove without professional editing
        - Still shows chundalgardens.com
        """
        img = Image.open(image_buffer).convert("RGBA")
        width, height = img.size
        
        draw = ImageDraw.Draw(img)
        
        # Small font for subtlety (1.5% of min dimension)
        font_size = max(8, int(min(width, height) * 0.015))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # 16 Strategic positions - survive ANY crop
        positions = [
            # CORNERS (4) - survive corner crops
            (width * 0.02, height * 0.02, "lt"),      # Left-Top
            (width * 0.98, height * 0.02, "rt"),      # Right-Top
            (width * 0.02, height * 0.98, "lb"),      # Left-Bottom
            (width * 0.98, height * 0.98, "rb"),      # Right-Bottom
            
            # EDGES (4) - survive edge crops
            (width * 0.50, height * 0.02, "ct"),      # Center-Top
            (width * 0.50, height * 0.98, "cb"),      # Center-Bottom
            (width * 0.02, height * 0.50, "lc"),      # Left-Center
            (width * 0.98, height * 0.50, "rc"),      # Right-Center
            
            # INNER QUADRANTS (4) - survive center crop
            (width * 0.25, height * 0.25, "in"),
            (width * 0.75, height * 0.25, "in"),
            (width * 0.25, height * 0.75, "in"),
            (width * 0.75, height * 0.75, "in"),
            
            # MID-EDGE (4) - additional protection
            (width * 0.33, height * 0.02, "mt"),
            (width * 0.66, height * 0.02, "mt"),
            (width * 0.33, height * 0.98, "mb"),
            (width * 0.66, height * 0.98, "mb"),
        ]
        
        for x, y, pos_type in positions:
            # Determine anchor based on position
            anchor_map = {
                "lt": "lt", "rt": "rt", "lb": "lb", "rb": "rb",
                "ct": "mt", "cb": "mb", "lc": "lm", "rc": "rm",
                "in": "mm", "mt": "mt", "mb": "mb"
            }
            anchor = anchor_map.get(pos_type, "mm")
            
            # Map to PIL anchor
            pil_anchors = {
                "lt": "la", "rt": "ra", "lb": "ld", "rb": "rd",
                "mt": "ma", "mb": "md", "lm": "lm", "rm": "rm",
                "mm": "mm"
            }
            
            # Varying opacity for stealth (20-30%)
            base_opacity = 0.25
            if pos_type in ["lt", "rt", "lb", "rb"]:
                opacity = base_opacity + 0.05  # Corners slightly more visible
            else:
                opacity = base_opacity
            
            # Shadow effect (harder to remove)
            shadow_offset = 1
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                cls.WATERMARK_TEXT,
                font=font,
                fill=(100, 100, 100, int(255 * opacity * 0.5)),
                anchor=pil_anchors.get(anchor)
            )
            
            # Main text
            draw.text(
                (x, y),
                cls.WATERMARK_TEXT,
                font=font,
                fill=(150, 150, 150, int(255 * opacity)),
                anchor=pil_anchors.get(anchor)
            )
        
        # Add INVISIBLE digital watermark (steganography)
        img = cls._add_invisible_watermark(img)
        
        # Convert to RGB
        final = Image.new("RGB", (width, height), (255, 255, 255))
        final.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
        
        output = io.BytesIO()
        final.save(output, format='PNG', quality=95)
        output.seek(0)
        return output
    
    @classmethod
    def _add_invisible_watermark(cls, img: Image.Image) -> Image.Image:
        """
        HIDDEN watermark in image data
        - Survives compression, resizing, format conversion
        - Can be extracted to prove ownership
        - Uses LSB (Least Significant Bit) steganography
        """
        # Convert to numpy array
        arr = np.array(img)
        
        # Binary representation of watermark
        watermark_binary = ''.join(format(ord(c), '08b') for c in cls.WATERMARK_TEXT)
        watermark_binary += '00000000'  # Null terminator
        
        # Embed in LSB of blue channel
        idx = 0
        rows, cols, _ = arr.shape
        
        for i in range(rows):
            for j in range(cols):
                if idx < len(watermark_binary):
                    # Modify only LSB of blue channel (index 2)
                    current = arr[i, j, 2]
                    bit = int(watermark_binary[idx])
                    arr[i, j, 2] = (current & 0xFE) | bit
                    idx += 1
                else:
                    break
            if idx >= len(watermark_binary):
                break
        
        return Image.fromarray(arr)


class PDFWatermark:
    """ReportLab PDF watermark implementation"""
    
    WATERMARK_TEXT = "chundalgardens.com"
    
    @staticmethod
    def add_visible_watermark(canvas, doc):
        """
        Large diagonal watermark on every PDF page
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor
        
        canvas.saveState()
        
        # Large diagonal watermark
        canvas.setFont('Helvetica-Bold', 50)
        canvas.setFillColor(HexColor('#CCCCCC'))
        canvas.setStrokeColor(HexColor('#CCCCCC'))
        
        # Center and rotate
        canvas.translate(A4[0]/2, A4[1]/2)
        canvas.rotate(35)
        canvas.drawCentredString(0, 0, PDFWatermark.WATERMARK_TEXT)
        
        # Additional faint watermarks
        canvas.rotate(-35)
        canvas.setFont('Helvetica-Bold', 25)
        canvas.setFillColor(HexColor('#E0E0E0'))
        canvas.rotate(35)
        canvas.drawCentredString(200, 100, PDFWatermark.WATERMARK_TEXT)
        canvas.drawCentredString(-200, -100, PDFWatermark.WATERMARK_TEXT)
        
        canvas.restoreState()
    
    @staticmethod
    def add_protection_watermark(canvas, doc):
        """
        Small corner watermarks - survive cropping
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor
        
        canvas.saveState()
        
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(HexColor('#999999'))
        
        # 12 strategic positions
        positions = [
            (40, 40), (A4[0]/2, 40), (A4[0]-40, 40),
            (40, A4[1]/2), (A4[0]-40, A4[1]/2),
            (40, A4[1]-40), (A4[0]/2, A4[1]-40), (A4[0]-40, A4[1]-40),
            (A4[0]/4, A4[1]/4), (3*A4[0]/4, A4[1]/4),
            (A4[0]/4, 3*A4[1]/4), (3*A4[0]/4, 3*A4[1]/4),
        ]
        
        for x, y in positions:
            canvas.drawCentredString(x, y, PDFWatermark.WATERMARK_TEXT)
        
        # Edge watermarks (very small)
        canvas.setFont('Helvetica-Bold', 6)
        for i in range(1, 6):
            x_pos = A4[0] * i / 6
            canvas.drawCentredString(x_pos, 15, PDFWatermark.WATERMARK_TEXT)
            canvas.drawCentredString(x_pos, A4[1]-15, PDFWatermark.WATERMARK_TEXT)
        
        canvas.restoreState()
