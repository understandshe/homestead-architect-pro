"""
Professional Livestock Housing Designer
2026 Standards - Goat, Chicken, Pig housing
"""

import numpy as np
from typing import Dict, Any, List
import io
from PIL import Image, ImageDraw, ImageFont

class LivestockDesigner:
    """Designs optimal housing for farm animals"""
    
    # 2026 Standards (sq ft per animal)
    SPACE_REQUIREMENTS = {
        'goat': {
            'adult': 15,      # 10-15 sq ft indoors + 25 sq ft outdoors
            'kid': 8,
            'outdoor_multiplier': 2.5
        },
        'chicken': {
            'layer_cage': 0.5,    # Commercial standard
            'free_range': 4,       # Indoor + 10 outdoor
            'brooder': 0.5         # First 4 weeks
        },
        'pig': {
            'farrowing': 50,      # Sow + piglets
            'nursery': 8,         # Per piglet (0-8 weeks)
            'grower': 12,         # Per pig (8-16 weeks)
            'finisher': 20        # Per pig (16+ weeks)
        }
    }
    
    CLIMATE_ADJUSTMENTS = {
        'Tropical': {'ventilation': 2.0, 'roof_height': 1.3, 'insulation': 'minimal'},
        'Dry': {'ventilation': 1.5, 'roof_height': 1.2, 'insulation': 'moderate'},
        'Temperate': {'ventilation': 1.0, 'roof_height': 1.0, 'insulation': 'standard'},
        'Cold': {'ventilation': 0.7, 'roof_height': 0.9, 'insulation': 'heavy'}
    }
    
    def create_housing(self, animal_type: str, count: int, climate: str, budget: str) -> Dict[str, Any]:
        """Generate complete housing design"""
        
        if animal_type == 'Goats':
            return self._design_goat_house(count, climate, budget)
        elif animal_type == 'Chickens':
            return self._design_chicken_house(count, climate, budget)
        elif animal_type == 'Pigs':
            return self._design_piggery(count, climate, budget)
        else:
            return self._design_mixed_system(count, climate, budget)
    
    def _design_goat_house(self, count: int, climate: str, budget: str) -> Dict:
        """Professional goat shed design"""
        
        specs = self.SPACE_REQUIREMENTS['goat']
        climate_adj = self.CLIMATE_ADJUSTMENTS[climate]
        
        # Calculate dimensions
        indoor_area = count * specs['adult'] * climate_adj['ventilation']
        outdoor_area = indoor_area * specs['outdoor_multiplier']
        
        # Dimensions (rectangular shed)
        width = int(np.sqrt(indoor_area) * 1.5)
        length = int(indoor_area / width)
        
        # Height based on climate
        height = int(8 * climate_adj['roof_height'])
        
        # Features based on budget
        features = []
        if budget in ['Standard', 'Premium']:
            features.extend(['Elevated Floor', 'Automatic Water', 'Feed Troughs'])
        if budget == 'Premium':
            features.extend(['Milking Parlor', 'Kidding Pens', 'Solar Ventilation'])
        
        # Generate floor plan
        floor_plan = self._draw_goat_floorplan(width, length, count, features)
        
        materials = self._calculate_goat_materials(width, length, height, budget)
        
        return {
            'floor_plan': floor_plan,
            'specs': {
                'Indoor Area': f"{indoor_area:.0f} sq ft",
                'Outdoor Area': f"{outdoor_area:.0f} sq ft",
                'Dimensions': f"{width}' Ã— {length}' Ã— {height}'",
                'Capacity': f"{count} adult goats",
                'Features': ', '.join(features) if features else 'Basic'
            },
            'materials': materials,
            'estimated_cost': self._estimate_cost(materials, budget)
        }
    
    def _design_chicken_house(self, count: int, climate: str, budget: str) -> Dict:
        """Modern poultry house design"""
        
        specs = self.SPACE_REQUIREMENTS['chicken']
        climate_adj = self.CLIMATE_ADJUSTMENTS[climate]
        
        # Multi-stage housing
        brooder_count = int(count * 0.2)  # 20% chicks
        grower_count = int(count * 0.3)   # 30% growing
        layer_count = count - brooder_count - grower_count
        
        # Areas
        if budget == 'Basic':
            brooder_area = brooder_count * specs['brooder'] * 2
            layer_area = layer_count * specs['layer_cage'] * 3
        else:
            brooder_area = brooder_count * specs['brooder'] * 3
            layer_area = layer_count * specs['free_range'] * 2
        
        total_area = brooder_area + layer_area
        
        features = []
        if budget in ['Standard', 'Premium']:
            features.extend(['Nesting Boxes', 'Roosting Bars', 'Dust Baths'])
        if budget == 'Premium':
            features.extend(['Automatic Feeders', 'Climate Control', 'Egg Conveyor'])
        
        floor_plan = self._draw_chicken_floorplan(total_area, count, features)
        materials = self._calculate_chicken_materials(total_area, budget)
        
        return {
            'floor_plan': floor_plan,
            'specs': {
                'Total Area': f"{total_area:.0f} sq ft",
                'Brooder Area': f"{brooder_area:.0f} sq ft",
                'Layer Area': f"{layer_area:.0f} sq ft",
                'Capacity': f"{count} birds",
                'Features': ', '.join(features)
            },
            'materials': materials,
            'estimated_cost': self._estimate_cost(materials, budget)
        }
    
    def _design_piggery(self, count: int, climate: str, budget: str) -> Dict:
        """Scientific piggery design"""
        
        specs = self.SPACE_REQUIREMENTS['pig']
        climate_adj = self.CLIMATE_ADJUSTMENTS[climate]
        
        # Assume 20% sows, 80% growers/finishers
        sow_count = max(1, int(count * 0.2))
        grower_count = count - sow_count
        
        # Areas
        farrowing_area = sow_count * specs['farrowing']
        nursery_area = sow_count * 8 * specs['nursery']  # 8 piglets per sow
        grower_area = grower_count * specs['grower']
        
        total_area = farrowing_area + nursery_area + grower_area
        
        features = []
        if budget in ['Standard', 'Premium']:
            features.extend(['Slatted Floors', 'Waste Channels', 'Cooling Pads'])
        if budget == 'Premium':
            features.extend(['Automatic Feeding', 'Biogas System', 'Quarantine Unit'])
        
        floor_plan = self._draw_pig_floorplan(total_area, sow_count, grower_count, features)
        materials = self._calculate_pig_materials(total_area, budget)
        
        return {
            'floor_plan': floor_plan,
            'specs': {
                'Total Area': f"{total_area:.0f} sq ft",
                'Farrowing': f"{farrowing_area:.0f} sq ft",
                'Nursery': f"{nursery_area:.0f} sq ft",
                'Grower': f"{grower_area:.0f} sq ft",
                'Features': ', '.join(features)
            },
            'materials': materials,
            'estimated_cost': self._estimate_cost(materials, budget)
        }
    
    def _draw_goat_floorplan(self, width: int, length: int, count: int, features: List[str]) -> io.BytesIO:
        """Generate 2D floor plan image"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        scale = min(700/width, 500/length)
        
        # Draw shed outline
        x1, y1 = 50, 50
        x2, y2 = x1 + int(width * scale), y1 + int(length * scale)
        draw.rectangle([x1, y1, x2, y2], outline='black', width=3)
        
        # Internal divisions
        if 'Kidding Pens' in features:
            # Separate kidding area
            draw.rectangle([x1+10, y1+10, x1+100, y1+100], outline='red', width=2)
            draw.text((x1+20, y1+50), "Kidding", fill='red')
        
        # Feeding area
        draw.rectangle([x1+10, y2-50, x2-10, y2-10], outline='blue', width=2)
        draw.text((x1+20, y2-40), "Feeding", fill='blue')
        
        # Dimensions
        draw.text((x1, y2+10), f"{width}'", fill='black')
        draw.text((x2+10, y1), f"{length}'", fill='black')
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    def _draw_chicken_floorplan(self, area: float, count: int, features: List[str]) -> io.BytesIO:
        """Generate chicken house floor plan"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        width = int(np.sqrt(area) * 2)
        length = int(area / width * 2)
        scale = min(700/width, 500/length)
        
        x1, y1 = 50, 50
        x2, y2 = x1 + int(width * scale), y1 + int(length * scale)
        
        # Main house
        draw.rectangle([x1, y1, x2, y2], outline='black', width=3)
        
        # Nesting boxes
        if 'Nesting Boxes' in features:
            for i in range(5):
                nx = x1 + 50 + i * 60
                draw.rectangle([nx, y1+10, nx+40, y1+60], outline='green', width=2)
        
        # Roosting bars
        if 'Roosting Bars' in features:
            for i in range(3):
                ry = y1 + 100 + i * 80
                draw.line([x1+20, ry, x2-20, ry], fill='brown', width=3)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    def _draw_pig_floorplan(self, area: float, sows: int, growers: int, features: List[str]) -> io.BytesIO:
        """Generate piggery floor plan"""
        img = Image.new('RGB', (1000, 700), 'white')
        draw = ImageDraw.Draw(img)
        
        # Farrowing section
        draw.rectangle([50, 50, 300, 300], outline='red', width=3)
        draw.text((100, 20), "FARROWING", fill='red')
        
        # Nursery
        draw.rectangle([350, 50, 600, 200], outline='orange', width=3)
        draw.text((400, 20), "NURSERY", fill='orange')
        
        # Grower/Finisher
        draw.rectangle([350, 250, 900, 600], outline='blue', width=3)
        draw.text((500, 220), "GROWER/FINISHER", fill='blue')
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    def _calculate_goat_materials(self, width: int, length: int, height: int, budget: str) -> Dict[str, str]:
        """Calculate material requirements"""
        wall_area = 2 * (width + length) * height
        roof_area = width * length * 1.2  # 20% overhang
        
        materials = {
            'Concrete (cubic yards)': f"{(width * length * 0.5) / 27:.1f}",
            'Bricks (units)': f"{int(wall_area * 10)}",
            'Roofing Sheets': f"{int(roof_area / 20)}",
            'Steel Bars (kg)': f"{int(wall_area * 2)}",
            'Doors': "2",
            'Windows': "4"
        }
        
        if budget == 'Premium':
            materials['Solar Panels'] = "2"
            materials['Auto Water System'] = "1 set"
        
        return materials
    
    def _calculate_chicken_materials(self, area: float, budget: str) -> Dict[str, str]:
        """Calculate poultry materials"""
        materials = {
            'Wire Mesh (sq ft)': f"{int(area * 2)}",
            'Wood Planks (ft)': f"{int(area * 0.5)}",
            'Roofing Sheets': f"{int(area / 25)}",
            'Nesting Boxes': "10",
            'Feeders': "5",
            'Waterers': "5"
        }
        return materials
    
    def _calculate_pig_materials(self, area: float, budget: str) -> Dict[str, str]:
        """Calculate piggery materials"""
        materials = {
            'Concrete Slabs': f"{int(area / 10)}",
            'Steel Fencing (ft)': f"{int(np.sqrt(area) * 20)}",
            'PVC Pipes (ft)': f"{int(area * 0.3)}",
            'Feed Troughs': "8",
            'Water Nipples': "20"
        }
        
        if budget == 'Premium':
            materials['Biogas Digester'] = "1"
            materials['Cooling System'] = "1 set"
        
        return materials
    
    def _estimate_cost(self, materials: Dict[str, str], budget: str) -> str:
        """Rough cost estimate"""
        base_cost = len(materials) * 500
        
        if budget == 'Basic':
            multiplier = 1.0
        elif budget == 'Standard':
            multiplier = 1.5
        else:
            multiplier = 2.5
        
        total = base_cost * multiplier
        return f"${total:,.0f} - ${total * 1.3:,.0f}"
