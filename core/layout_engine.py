"""
AI Layout Engine - v4 PROFESSIONAL
Homestead Architect Pro 2026 - Global Edition

Fixes:
  - All features have proper x,y coordinates
  - No missing keys for any feature type
  - Tree placement data passed to visualizers
"""

from typing import Dict, Any
import random

class LayoutEngine:

    ZONE_RATIOS = {
        'small':  {'z0': 0.10, 'z1': 0.18, 'z2': 0.22, 'z3': 0.38, 'z4': 0.12},
        'medium': {'z0': 0.08, 'z1': 0.14, 'z2': 0.28, 'z3': 0.35, 'z4': 0.15},
        'large':  {'z0': 0.05, 'z1': 0.10, 'z2': 0.35, 'z3': 0.30, 'z4': 0.20},
    }

    # 12 Tree species with full data
    TREE_SPECIES = {
        'Mango': {'trunk_h': 5, 'canopy_bot': 5, 'canopy_top': 20, 'canopy_r': 9, 'trunk_r': 1.1,
                 'color': '#2E7D32', 'color2': '#388E3C',
                 'income_usd': (300, 1500), 'unit': 'kg/yr', 'yield_val': '80-200'},
        'Jackfruit': {'trunk_h': 8, 'canopy_bot': 8, 'canopy_top': 28, 'canopy_r': 10, 'trunk_r': 1.4,
                     'color': '#1B5E20', 'color2': '#2E7D32',
                     'income_usd': (200, 800), 'unit': 'kg/yr', 'yield_val': '50-200'},
        'Coconut': {'trunk_h': 22, 'canopy_bot': 22, 'canopy_top': 32, 'canopy_r': 6, 'trunk_r': 0.7,
                   'color': '#33691E', 'color2': '#558B2F',
                   'income_usd': (150, 600), 'unit': 'nuts/yr', 'yield_val': '80-200'},
        'Banana': {'trunk_h': 3, 'canopy_bot': 3, 'canopy_top': 10, 'canopy_r': 5, 'trunk_r': 1.6,
                  'color': '#558B2F', 'color2': '#7CB342',
                  'income_usd': (100, 400), 'unit': 'bunch/yr', 'yield_val': '5-20'},
        'Guava': {'trunk_h': 4, 'canopy_bot': 4, 'canopy_top': 14, 'canopy_r': 5, 'trunk_r': 0.8,
                 'color': '#33691E', 'color2': '#43A047',
                 'income_usd': (80, 300), 'unit': 'kg/yr', 'yield_val': '20-60'},
        'Papaya': {'trunk_h': 4, 'canopy_bot': 4, 'canopy_top': 11, 'canopy_r': 3.5, 'trunk_r': 0.5,
                  'color': '#558B2F', 'color2': '#8BC34A',
                  'income_usd': (60, 250), 'unit': 'kg/yr', 'yield_val': '30-80'},
        'Avocado': {'trunk_h': 7, 'canopy_bot': 7, 'canopy_top': 19, 'canopy_r': 7, 'trunk_r': 1.0,
                   'color': '#2E7D32', 'color2': '#1B5E20',
                   'income_usd': (400, 2000), 'unit': 'kg/yr', 'yield_val': '50-200'},
        'Moringa': {'trunk_h': 6, 'canopy_bot': 6, 'canopy_top': 16, 'canopy_r': 4, 'trunk_r': 0.6,
                   'color': '#66BB6A', 'color2': '#4CAF50',
                   'income_usd': (100, 500), 'unit': 'kg/yr', 'yield_val': '200-500'},
        'Citrus': {'trunk_h': 4, 'canopy_bot': 4, 'canopy_top': 13, 'canopy_r': 5, 'trunk_r': 0.7,
                  'color': '#43A047', 'color2': '#66BB6A',
                  'income_usd': (150, 600), 'unit': 'kg/yr', 'yield_val': '30-80'},
        'Neem': {'trunk_h': 9, 'canopy_bot': 9, 'canopy_top': 25, 'canopy_r': 10, 'trunk_r': 1.2,
                'color': '#388E3C', 'color2': '#2E7D32',
                'income_usd': (50, 200), 'unit': 'kg/yr', 'yield_val': '5-15 (seed)'},
        'Teak': {'trunk_h': 15, 'canopy_bot': 15, 'canopy_top': 30, 'canopy_r': 8, 'trunk_r': 1.0,
                'color': '#1B5E20', 'color2': '#2E7D32',
                'income_usd': (500, 3000), 'unit': 'tree at 15yr', 'yield_val': '1 log'},
        'Bamboo': {'trunk_h': 0, 'canopy_bot': 0, 'canopy_top': 18, 'canopy_r': 3, 'trunk_r': 0.4,
                  'color': '#4CAF50', 'color2': '#8BC34A',
                  'income_usd': (100, 600), 'unit': 'culm/yr', 'yield_val': '20-50'},
    }

    def generate(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        dims = answers.get('dimensions', {'length': 100, 'width': 100})
        L, W = float(dims['length']), float(dims['width'])
        total_sqft = L * W
        acres = total_sqft / 43560
        category = 'small' if acres < 0.5 else ('medium' if acres < 5 else 'large')
        zones = self.ZONE_RATIOS[category].copy()
        house_pos = answers.get('house_position', 'Center')
        zone_positions = self._make_zone_positions(L, W, zones, house_pos)
        features = self._make_features(answers, L, W, house_pos, zone_positions)
        
        # Generate tree placements based on user slider
        tree_count = answers.get('tree_count', 15)
        tree_placements = self._generate_tree_placements(tree_count, zone_positions, L, W)
        
        return {
            'total_sqft': total_sqft,
            'acres': acres,
            'category': category,
            'dimensions': {'L': L, 'W': W},
            'zones': zones,
            'zone_positions': zone_positions,
            'house_position': house_pos,
            'features': features,
            'tree_placements': tree_placements,
            'tree_species': self.TREE_SPECIES,
            'water_source': answers.get('water_source', 'Borewell/Well'),
            'slope': answers.get('slope', 'Flat'),
            'livestock': answers.get('livestock', ['None']),
            'tree_count': tree_count,
        }

    def _generate_tree_placements(self, count: int, zone_positions: dict, L: float, W: float) -> list:
        """Generate tree positions with proper spacing"""
        placements = []
        z2 = zone_positions.get('z2')
        z4 = zone_positions.get('z4')
        
        if not z2:
            return placements
            
        species_list = list(self.TREE_SPECIES.keys())
        random.seed(42)  # Consistent placement
        
        # Place trees in z2 (Food Forest)
        for i in range(min(count, 35)):  # Max 35 in z2
            margin = 15  # Keep away from edges
            x = z2['x'] + margin + random.random() * (z2['width'] - 2*margin)
            y = z2['y'] + margin + random.random() * (z2['height'] - 2*margin)
            species = species_list[i % len(species_list)]
            placements.append({
                'x': x, 'y': y, 'species': species,
                'id': f'tree_{i}', 'zone': 'z2'
            })
        
        # Place remaining in z4 (Buffer Zone) - Neem, Teak, Bamboo
        if z4 and count > 35:
            for i in range(count - 35):
                margin = 10
                x = z4['x'] + margin + random.random() * (z4['width'] - 2*margin)
                y = z4['y'] + margin + random.random() * (z4['height'] - 2*margin)
                species = ['Neem', 'Teak', 'Bamboo'][i % 3]
                placements.append({
                    'x': x, 'y': y, 'species': species,
                    'id': f'tree_buffer_{i}', 'zone': 'z4'
                })
        
        return placements

    def _make_zone_positions(self, L, W, zones, house_pos):
        pos = {}
        if house_pos in ('South', 'Not built yet', 'Center'):
            y = 0.0
            for zid in ['z0', 'z1', 'z2', 'z3', 'z4']:
                h = W * zones[zid]
                pos[zid] = {'x': 0, 'y': y, 'width': L, 'height': h}
                y += h
        elif house_pos == 'North':
            y = W
            for zid in ['z0', 'z1', 'z2', 'z3', 'z4']:
                h = W * zones[zid]
                y -= h
                pos[zid] = {'x': 0, 'y': y, 'width': L, 'height': h}
        elif house_pos == 'East':
            x = L
            for zid in ['z0', 'z1', 'z2', 'z3', 'z4']:
                w = L * zones[zid]
                x -= w
                pos[zid] = {'x': x, 'y': 0, 'width': w, 'height': W}
        elif house_pos == 'West':
            x = 0.0
            for zid in ['z0', 'z1', 'z2', 'z3', 'z4']:
                w = L * zones[zid]
                pos[zid] = {'x': x, 'y': 0, 'width': w, 'height': W}
                x += w
        return pos

    def _house_bbox(self, house_pos, L, W, zone_positions):
        z0 = zone_positions.get('z0', {'x': 0, 'y': 0, 'width': L, 'height': W})
        hw = z0['width'] * 0.55
        hh = z0['height'] * 0.65
        hx = z0['x'] + (z0['width'] - hw) / 2
        hy = z0['y'] + (z0['height'] - hh) / 2
        return hx, hy, hw, hh

    def _clamp(self, val, lo, hi):
        return max(lo, min(val, hi))

    def _make_features(self, answers, L, W, house_pos, zone_positions):
        features = {}
        livestock = answers.get('livestock', [])
        water = answers.get('water_source', '')

        hx, hy, hw, hh = self._house_bbox(house_pos, L, W, zone_positions)
        hcx = hx + hw / 2
        hcy = hy + hh / 2

        z1 = zone_positions.get('z1', {})
        z3 = zone_positions.get('z3', {'x': 0, 'y': W*0.5, 'width': L, 'height': W*0.35})

        # Solar — always south of house (low Y), inside plot
        solar_w = self._clamp(hw * 0.45, L * 0.06, L * 0.18)
        solar_h = self._clamp(hh * 0.35, W * 0.04, W * 0.10)
        solar_y = self._clamp(hy - solar_h - W * 0.03, 0, W - solar_h)
        solar_x = self._clamp(hcx - solar_w / 2, 0, L - solar_w)
        features['solar'] = {'x': solar_x, 'y': solar_y, 'width': solar_w, 'height': solar_h}

        # Greenhouse — east of house, same vertical band
        gh_w = self._clamp(hw * 0.50, L * 0.08, L * 0.18)
        gh_h = self._clamp(hh * 0.60, W * 0.08, W * 0.18)
        gh_x = self._clamp(hx + hw + L * 0.025, 0, L - gh_w)
        gh_y = self._clamp(hcy - gh_h / 2, 0, W - gh_h)
        features['greenhouse'] = {'x': gh_x, 'y': gh_y, 'width': gh_w, 'height': gh_h}

        # Water features with proper coordinates
        if 'Borewell' in water or 'Well' in water:
            features['well'] = {
                'x': self._clamp(L * 0.90, 0, L),
                'y': self._clamp(W * 0.90, 0, W),
                'radius': min(L, W) * 0.018,
            }
        
        if 'Pond' in water or 'River' in water:
            features['pond'] = {
                'x': z3['x'] + z3['width'] * 0.08,
                'y': z3['y'] + z3['height'] * 0.15,
                'radius': min(L, W) * 0.07,
            }
        
        if 'Rainwater' in water:
            features['rain_tank'] = {
                'x': self._clamp(hx - L * 0.09, 0, L - L*0.06),
                'y': hy,
                'width': L * 0.06,
                'height': hh * 0.35,
            }

        # Compost — in z1, far from house
        if z1:
            features['compost'] = [
                {'x': self._clamp(z1['x'] + z1['width']*0.07, 0, L),
                 'y': self._clamp(z1['y'] + z1['height']*0.50, 0, W),
                 'size': min(L, W) * 0.016},
                {'x': self._clamp(z1['x'] + z1['width']*0.88, 0, L),
                 'y': self._clamp(z1['y'] + z1['height']*0.50, 0, W),
                 'size': min(L, W) * 0.016},
            ]

        # Swales - now with x,y coordinates for proper rendering
        slope = answers.get('slope', 'Flat')
        if slope != 'Flat' and z3:
            features['swales'] = [
                {'x': z3['x'] + z3['width'] * 0.5,  # Center x
                 'y': z3['y'] + z3['height'] * 0.30,
                 'width': z3['width'] * 0.8,
                 'height': 3,  # Swale width
                 'curve': 'sin'},
                {'x': z3['x'] + z3['width'] * 0.5,
                 'y': z3['y'] + z3['height'] * 0.65,
                 'width': z3['width'] * 0.8,
                 'height': 3,
                 'curve': 'sin'},
            ]

        # Livestock grid in right portion of Z3
        grid_x0 = z3['x'] + z3['width'] * 0.45
        grid_y0 = z3['y'] + z3['height'] * 0.05
        grid_w  = z3['width'] * 0.52
        grid_h  = z3['height'] * 0.90

        animal_keys = []
        if 'Goats'    in livestock: animal_keys.append('goat_shed')
        if 'Chickens' in livestock: animal_keys.append('chicken_coop')
        if 'Pigs'     in livestock: animal_keys.append('piggery')
        if 'Cows'     in livestock: animal_keys.append('cow_shed')
        if 'Bees'     in livestock: animal_keys.append('bee_hives')

        if animal_keys:
            cols = 2
            rows = (len(animal_keys) + cols - 1) // cols
            gap = 4
            cell_w = (grid_w - (cols + 1) * gap) / cols
            cell_h = (grid_h - (rows + 1) * gap) / rows

            size_fracs = {
                'goat_shed':   (0.85, 0.72),
                'chicken_coop':(0.72, 0.65),
                'piggery':     (0.85, 0.78),
                'cow_shed':    (0.90, 0.82),
                'bee_hives':   (0.58, 0.50),
            }

            for idx, key in enumerate(animal_keys):
                col = idx % cols
                row = idx // cols
                cx = grid_x0 + gap + col * (cell_w + gap)
                cy = grid_y0 + gap + row * (cell_h + gap)
                fw, fh = size_fracs.get(key, (0.80, 0.70))
                features[key] = {
                    'x': self._clamp(cx, 0, L - cell_w * fw),
                    'y': self._clamp(cy, 0, W - cell_h * fh),
                    'width':  cell_w * fw,
                    'height': cell_h * fh,
                }

        if 'Fish' in livestock:
            if 'pond' not in features:
                features['pond'] = {
                    'x': z3['x'] + z3['width'] * 0.08,
                    'y': z3['y'] + z3['height'] * 0.15,
                    'radius': min(L, W) * 0.07,
                }
            features['fish_tanks'] = {
                'x': self._clamp(z3['x'] + z3['width'] * 0.05, 0, L - z3['width']*0.14),
                'y': self._clamp(z3['y'] + z3['height'] * 0.55, 0, W - z3['height']*0.25),
                'width': z3['width'] * 0.13,
                'height': z3['height'] * 0.28,
            }

        # Reference to first livestock for backward compatibility
        for k in ('goat_shed', 'chicken_coop', 'piggery', 'cow_shed'):
            if k in features:
                features['livestock'] = features[k]
                break

        return features
