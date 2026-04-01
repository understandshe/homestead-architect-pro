"""
AI Layout Engine â€” v3 PROFESSIONAL
Homestead Architect Pro 2026
"""

from typing import Dict, Any


class LayoutEngine:

    ZONE_RATIOS = {
        'small':  {'z0': 0.10, 'z1': 0.18, 'z2': 0.22, 'z3': 0.38, 'z4': 0.12},
        'medium': {'z0': 0.08, 'z1': 0.14, 'z2': 0.28, 'z3': 0.35, 'z4': 0.15},
        'large':  {'z0': 0.05, 'z1': 0.10, 'z2': 0.35, 'z3': 0.30, 'z4': 0.20},
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
        return {
            'total_sqft': total_sqft, 'acres': acres, 'category': category,
            'dimensions': {'L': L, 'W': W}, 'zones': zones,
            'zone_positions': zone_positions, 'house_position': house_pos,
            'features': features,
            'water_source': answers.get('water_source', 'Borewell/Well'),
            'slope': answers.get('slope', 'Flat'),
            'livestock': answers.get('livestock', ['None']),
        }

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

        # Solar â€” always south of house (low Y), inside plot
        solar_w = self._clamp(hw * 0.45, L * 0.06, L * 0.18)
        solar_h = self._clamp(hh * 0.35, W * 0.04, W * 0.10)
        solar_y = self._clamp(hy - solar_h - W * 0.03, 0, W - solar_h)
        solar_x = self._clamp(hcx - solar_w / 2, 0, L - solar_w)
        features['solar'] = {'x': solar_x, 'y': solar_y, 'width': solar_w, 'height': solar_h}

        # Greenhouse â€” east of house, same vertical band
        gh_w = self._clamp(hw * 0.50, L * 0.08, L * 0.18)
        gh_h = self._clamp(hh * 0.60, W * 0.08, W * 0.18)
        gh_x = self._clamp(hx + hw + L * 0.025, 0, L - gh_w)
        gh_y = self._clamp(hcy - gh_h / 2, 0, W - gh_h)
        features['greenhouse'] = {'x': gh_x, 'y': gh_y, 'width': gh_w, 'height': gh_h}

        # Water
        if 'Borewell' in water or 'Well' in water:
            features['well'] = {
                'x': self._clamp(L * 0.90, 0, L), 'y': self._clamp(W * 0.90, 0, W),
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
                'y': hy, 'width': L * 0.06, 'height': hh * 0.35,
            }

        # Compost â€” in z1, far from house
        if z1:
            features['compost'] = [
                {'x': self._clamp(z1['x'] + z1['width']*0.07, 0, L),
                 'y': self._clamp(z1['y'] + z1['height']*0.50, 0, W),
                 'size': min(L, W) * 0.016},
                {'x': self._clamp(z1['x'] + z1['width']*0.88, 0, L),
                 'y': self._clamp(z1['y'] + z1['height']*0.50, 0, W),
                 'size': min(L, W) * 0.016},
            ]

        # Swales
        slope = answers.get('slope', 'Flat')
        if slope != 'Flat' and z3:
            features['swales'] = [
                {'y': z3['y'] + z3['height'] * 0.30, 'curve': 'sin'},
                {'y': z3['y'] + z3['height'] * 0.65, 'curve': 'sin'},
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

        for k in ('goat_shed', 'chicken_coop', 'piggery', 'cow_shed'):
            if k in features:
                features['livestock'] = features[k]
                break

        return features
