"""
AI Layout Engine
Generates optimal homestead layout based on user inputs
"""

import numpy as np
from typing import Dict, Any, List, Tuple
import random

class LayoutEngine:
    """Core algorithm for homestead layout generation"""
    
    ZONE_RATIOS = {
        'small': {'z0': 0.10, 'z1': 0.15, 'z2': 0.25, 'z3': 0.40, 'z4': 0.10},
        'medium': {'z0': 0.08, 'z1': 0.12, 'z2': 0.30, 'z3': 0.35, 'z4': 0.15},
        'large': {'z0': 0.05, 'z1': 0.10, 'z2': 0.35, 'z3': 0.30, 'z4': 0.20}
    }
    
    def generate(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete layout"""
        
        # Get dimensions
        dims = answers.get('dimensions', {'length': 100, 'width': 100})
        L, W = dims['length'], dims['width']
        total_sqft = L * W
        
        # Determine size category
        acres = total_sqft / 43560
        if acres < 0.5:
            category = 'small'
        elif acres < 5:
            category = 'medium'
        else:
            category = 'large'
        
        # Get zone ratios
        zones = self.ZONE_RATIOS[category].copy()
        
        # Adjust based on house position
        house_pos = answers.get('house_position', 'Center')
        
        # Calculate feature placement
        features = self._calculate_features(answers, L, W)
        
        # Generate zones with positions
        zone_positions = self._calculate_zone_positions(L, W, zones, house_pos)
        
        return {
            'total_sqft': total_sqft,
            'acres': acres,
            'category': category,
            'dimensions': {'L': L, 'W': W},
            'zones': zones,
            'zone_positions': zone_positions,
            'house_position': house_pos,
            'features': features,
            'water_source': answers.get('water_source', 'Unknown'),
            'slope': answers.get('slope', 'Flat'),
            'livestock': answers.get('livestock', ['None'])
        }
    
    def _calculate_features(self, answers: Dict, L: float, W: float) -> Dict[str, Any]:
        """Calculate positions for all features"""
        features = {}
        
        # Water source
        water = answers.get('water_source', '')
        if 'Borewell' in water:
            features['borewell'] = {
                'x': L * 0.85, 'y': W * 0.85,  # North-East (Vaastu friendly)
                'radius': min(L, W) * 0.02
            }
        
        if 'Pond' in water or 'River' in water:
            features['pond'] = {
                'x': L * 0.2, 'y': W * 0.2,
                'radius': min(L, W) * 0.08
            }
        
        # Solar (south of house for max sun)
        features['solar'] = {
            'x': L * 0.6, 'y': W * 0.75,
            'width': L * 0.15, 'height': L * 0.10
        }
        
        # Greenhouse (Zone 1 or 2)
        features['greenhouse'] = {
            'x': L * 0.15, 'y': W * 0.55,
            'width': L * 0.20, 'height': W * 0.15
        }
        
        # Livestock areas
        livestock = answers.get('livestock', [])
        if 'Goats' in livestock:
            features['goat_shed'] = {
                'x': L * 0.75, 'y': W * 0.15,
                'width': L * 0.20, 'height': W * 0.20
            }
        
        if 'Chickens' in livestock:
            features['chicken_coop'] = {
                'x': L * 0.05, 'y': W * 0.70,
                'width': L * 0.10, 'height': W * 0.10
            }
        
        if 'Pigs' in livestock:
            features['piggery'] = {
                'x': L * 0.80, 'y': W * 0.40,
                'width': L * 0.15, 'height': W * 0.25
            }
        
        # Compost (multiple locations)
        features['compost'] = [
            {'x': L * 0.10, 'y': W * 0.45, 'size': min(L,W)*0.015},
            {'x': L * 0.90, 'y': W * 0.60, 'size': min(L,W)*0.015}
        ]
        
        # Swales (water harvesting)
        slope = answers.get('slope', 'Flat')
        if slope != 'Flat':
            features['swales'] = [
                {'y': W * 0.25, 'curve': 'sin'},
                {'y': W * 0.50, 'curve': 'sin'},
                {'y': W * 0.75, 'curve': 'sin'}
            ]
        
        return features
    
    def _calculate_zone_positions(self, L: float, W: float, zones: Dict, house_pos: str) -> Dict:
        """Calculate actual coordinates for each zone"""
        positions = {}
        
        if house_pos in ['North', 'South']:
            # Linear layout
            y = 0
            order = ['z4', 'z3', 'z2', 'z1', 'z0'] if house_pos == 'North' else ['z0', 'z1', 'z2', 'z3', 'z4']
            
            for zone in order:
                height = W * zones[zone]
                positions[zone] = {
                    'x': 0, 'y': y,
                    'width': L, 'height': height
                }
                y += height
        else:
            # Cluster layout for East/West/Center
            # Zone 0 (House) in center
            positions['z0'] = {
                'x': L * 0.35, 'y': W * 0.40,
                'width': L * 0.30, 'height': W * 0.20
            }
            # Zone 1 around house
            positions['z1'] = {
                'x': L * 0.20, 'y': W * 0.20,
                'width': L * 0.60, 'height': W * 0.20
            }
            # Zone 2 (Food forest)
            positions['z2'] = {
                'x': L * 0.10, 'y': W * 0.60,
                'width': L * 0.80, 'height': W * 0.25
            }
            # Zone 3 (Crops)
            positions['z3'] = {
                'x': 0, 'y': 0,
                'width': L, 'height': W * 0.20
            }
            # Zone 4 (Buffer)
            positions['z4'] = {
                'x': 0, 'y': W * 0.85,
                'width': L, 'height': W * 0.15
            }
        
        return positions
