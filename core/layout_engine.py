"""
AI Layout Engine — FIXED
Homestead Architect Pro 2026
Fixes:
  - Feature keys now match what visualizer_2d / visualizer_3d expect
  - 'borewell' → 'well' (visualizer looks for 'well')
  - Individual livestock sheds per animal type (goat_shed, chicken_coop, etc.)
  - Fish pond added when Fish selected
  - Positions calculated relative to house_position so features are
    always inside property boundary and logically placed
"""

import numpy as np
from typing import Dict, Any


class LayoutEngine:
    """Core algorithm for homestead layout generation."""

    ZONE_RATIOS = {
        'small':  {'z0': 0.10, 'z1': 0.15, 'z2': 0.25, 'z3': 0.40, 'z4': 0.10},
        'medium': {'z0': 0.08, 'z1': 0.12, 'z2': 0.30, 'z3': 0.35, 'z4': 0.15},
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
        zone_positions = self._calculate_zone_positions(L, W, zones, house_pos)
        features = self._calculate_features(answers, L, W, house_pos)

        return {
            'total_sqft': total_sqft,
            'acres': acres,
            'category': category,
            'dimensions': {'L': L, 'W': W},
            'zones': zones,
            'zone_positions': zone_positions,
            'house_position': house_pos,
            'features': features,
            'water_source': answers.get('water_source', 'Borewell/Well'),
            'slope': answers.get('slope', 'Flat'),
            'livestock': answers.get('livestock', ['None']),
        }

    # ── Feature placement ────────────────────────────────────────────────────

    def _calculate_features(self, answers: Dict, L: float, W: float,
                            house_pos: str) -> Dict[str, Any]:
        features: Dict[str, Any] = {}
        livestock = answers.get('livestock', [])

        # ── House anchor determines compass of surrounding features ──────
        # We define four quadrants relative to house center
        hx, hy, hw, hh = self._house_bbox(house_pos, L, W)
        hcx, hcy = hx + hw / 2, hy + hh / 2   # house centre

        # Helper: place a box at (frac_x, frac_y) of the FULL plot,
        # but snap away from house centre if too close.
        def place(fx, fy, fw, fh):
            return {
                'x':      max(0.0, min(L * fx, L - L * fw)),
                'y':      max(0.0, min(W * fy, W - W * fh)),
                'width':  L * fw,
                'height': W * fh,
            }

        # ── Water source ─────────────────────────────────────────────────
        water = answers.get('water_source', '')
        if 'Borewell' in water or 'Well' in water:
            # NE corner — Vaastu-friendly, away from house
            features['well'] = {
                'x': L * 0.86, 'y': W * 0.86,
                'radius': min(L, W) * 0.022,
            }
        if 'Pond' in water or 'River' in water or 'Fish' in livestock:
            features['pond'] = {
                'x': L * 0.18, 'y': W * 0.20,
                'radius': min(L, W) * 0.09,
            }
        if 'Rainwater' in water:
            # Rainwater tank near house
            features['rain_tank'] = place(0.70, 0.72, 0.07, 0.05)

        # ── Solar — south of house (max sun gain) ────────────────────────
        # Placed below house centre in the plot (south = low Y in our grid)
        solar_y_frac = max(0.02, (hy / W) - 0.18)
        features['solar'] = {
            'x':      hcx - L * 0.08,
            'y':      W * solar_y_frac,
            'width':  L * 0.16,
            'height': W * 0.10,
        }

        # ── Greenhouse — east of house (morning sun) ──────────────────────
        gh_x = min(L - L * 0.22, hx + hw + L * 0.04)
        features['greenhouse'] = {
            'x':      gh_x,
            'y':      hcy - W * 0.08,
            'width':  L * 0.20,
            'height': W * 0.15,
        }

        # ── Compost — between kitchen garden and food forest ─────────────
        features['compost'] = [
            {'x': L * 0.08, 'y': W * 0.45, 'size': min(L, W) * 0.015},
            {'x': L * 0.88, 'y': W * 0.58, 'size': min(L, W) * 0.015},
        ]

        # ── Swales ───────────────────────────────────────────────────────
        slope = answers.get('slope', 'Flat')
        if slope != 'Flat':
            features['swales'] = [
                {'y': W * 0.25, 'curve': 'sin'},
                {'y': W * 0.50, 'curve': 'sin'},
                {'y': W * 0.75, 'curve': 'sin'},
            ]

        # ── Livestock housing — each animal type separately ───────────────
        # Placed in Zone 3 area (upper portion of plot, away from house)
        livestock_zone_x = L * 0.60   # right side of plot
        livestock_zone_y = W * 0.72   # top portion
        offset = 0                    # cascade vertically

        if 'Goats' in livestock:
            features['goat_shed'] = {
                'x':      livestock_zone_x,
                'y':      livestock_zone_y - offset,
                'width':  L * 0.18,
                'height': W * 0.12,
                'label':  '🐐 Goat Shed',
            }
            offset += W * 0.14

        if 'Chickens' in livestock:
            features['chicken_coop'] = {
                'x':      livestock_zone_x,
                'y':      livestock_zone_y - offset,
                'width':  L * 0.12,
                'height': W * 0.10,
                'label':  '🐔 Chicken Coop',
            }
            offset += W * 0.12

        if 'Pigs' in livestock:
            features['piggery'] = {
                'x':      livestock_zone_x + L * 0.20,
                'y':      livestock_zone_y - offset,
                'width':  L * 0.16,
                'height': W * 0.14,
                'label':  '🐷 Piggery',
            }
            offset += W * 0.16

        if 'Cows' in livestock:
            features['cow_shed'] = {
                'x':      livestock_zone_x + L * 0.20,
                'y':      livestock_zone_y,
                'width':  L * 0.18,
                'height': W * 0.16,
                'label':  '🐄 Cow Shed',
            }

        if 'Fish' in livestock:
            # Fish pond — if not already added from water source
            if 'pond' not in features:
                features['pond'] = {
                    'x': L * 0.18, 'y': W * 0.20,
                    'radius': min(L, W) * 0.09,
                }
            features['fish_tanks'] = {
                'x':      L * 0.05,
                'y':      W * 0.65,
                'width':  L * 0.10,
                'height': W * 0.08,
                'label':  '🐟 Fish Tanks',
            }

        if 'Bees' in livestock:
            features['bee_hives'] = {
                'x':      L * 0.05,
                'y':      W * 0.55,
                'width':  L * 0.06,
                'height': W * 0.05,
                'label':  '🐝 Bee Hives',
            }

        # ── Legacy single 'livestock' key for 3D backward compat ─────────
        # Pick first animal shed as the "main" livestock feature
        for k in ('goat_shed', 'chicken_coop', 'piggery', 'cow_shed'):
            if k in features:
                features['livestock'] = features[k]
                break

        return features

    # ── House bounding-box helper ────────────────────────────────────────────
    @staticmethod
    def _house_bbox(pos: str, L: float, W: float):
        positions = {
            'North':       (L*0.30, W*0.82, L*0.40, W*0.12),
            'South':       (L*0.30, W*0.06, L*0.40, W*0.12),
            'East':        (L*0.75, W*0.35, L*0.20, W*0.30),
            'West':        (L*0.05, W*0.35, L*0.20, W*0.30),
            'Center':      (L*0.35, W*0.40, L*0.30, W*0.20),
            'Not built yet': (L*0.35, W*0.40, L*0.30, W*0.20),
        }
        return positions.get(pos, positions['Center'])

    # ── Zone positions ───────────────────────────────────────────────────────
    def _calculate_zone_positions(self, L: float, W: float,
                                   zones: Dict, house_pos: str) -> Dict:
        positions = {}

        if house_pos in ('North', 'South'):
            y = 0.0
            order = (['z4', 'z3', 'z2', 'z1', 'z0'] if house_pos == 'North'
                     else ['z0', 'z1', 'z2', 'z3', 'z4'])
            for zone in order:
                height = W * zones[zone]
                positions[zone] = {'x': 0, 'y': y, 'width': L, 'height': height}
                y += height

        elif house_pos in ('East', 'West'):
            x = 0.0
            order = (['z0', 'z1', 'z2', 'z3', 'z4'] if house_pos == 'East'
                     else ['z4', 'z3', 'z2', 'z1', 'z0'])
            for zone in order:
                width = L * zones[zone]
                positions[zone] = {'x': x, 'y': 0, 'width': width, 'height': W}
                x += width

        else:  # Center / Not built yet
            positions['z0'] = {'x': L*0.35, 'y': W*0.40, 'width': L*0.30, 'height': W*0.20}
            positions['z1'] = {'x': L*0.20, 'y': W*0.26, 'width': L*0.60, 'height': W*0.14}
            positions['z2'] = {'x': L*0.08, 'y': W*0.08, 'width': L*0.84, 'height': W*0.18}
            positions['z3'] = {'x': 0,      'y': W*0.60, 'width': L,       'height': W*0.28}
            positions['z4'] = {'x': 0,      'y': W*0.88, 'width': L,       'height': W*0.12}

        return positions

                    
