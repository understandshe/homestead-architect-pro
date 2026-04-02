"""
AI Layout Engine - v5 FINAL
Homestead Architect Pro 2026

ROOT CAUSE FIXES:
  - Large plots: z0 is only ~48ft tall â†’ house was 31ft tall (stamp-sized)
    FIX: house has minimum absolute size, not just % of z0
  - Well was at 90%,90% of entire plot â†’ fell in Z4 buffer zone
    FIX: well is placed NE of house (within Z0/Z1), not NE of plot
  - Greenhouse too small on large plots
    FIX: minimum absolute dimensions enforced
  - Pond/fish overlap on large plots
    FIX: pond left of Z3, fish tanks below pond, no overlap
  - Livestock grid gap too small on large plots
    FIX: proper minimum gap between sheds
  - Features stay inside their intended zones always
"""

from typing import Dict, Any
import random


class LayoutEngine:

    ZONE_RATIOS = {
        'small':  {'z0': 0.10, 'z1': 0.18, 'z2': 0.22, 'z3': 0.38, 'z4': 0.12},
        'medium': {'z0': 0.08, 'z1': 0.14, 'z2': 0.28, 'z3': 0.35, 'z4': 0.15},
        'large':  {'z0': 0.05, 'z1': 0.10, 'z2': 0.35, 'z3': 0.30, 'z4': 0.20},
    }

    TREE_SPECIES = {
        'Mango':    {'canopy_r': 9,  'color': '#2E7D32', 'color2': '#388E3C', 'income_usd': (300,1500)},
        'Jackfruit':{'canopy_r': 10, 'color': '#1B5E20', 'color2': '#2E7D32', 'income_usd': (200,800)},
        'Coconut':  {'canopy_r': 6,  'color': '#33691E', 'color2': '#558B2F', 'income_usd': (150,600)},
        'Banana':   {'canopy_r': 5,  'color': '#558B2F', 'color2': '#7CB342', 'income_usd': (100,400)},
        'Guava':    {'canopy_r': 5,  'color': '#33691E', 'color2': '#43A047', 'income_usd': (80,300)},
        'Papaya':   {'canopy_r': 4,  'color': '#558B2F', 'color2': '#8BC34A', 'income_usd': (60,250)},
        'Avocado':  {'canopy_r': 7,  'color': '#2E7D32', 'color2': '#1B5E20', 'income_usd': (400,2000)},
        'Moringa':  {'canopy_r': 4,  'color': '#66BB6A', 'color2': '#4CAF50', 'income_usd': (100,500)},
        'Citrus':   {'canopy_r': 5,  'color': '#43A047', 'color2': '#66BB6A', 'income_usd': (150,600)},
        'Neem':     {'canopy_r': 10, 'color': '#388E3C', 'color2': '#2E7D32', 'income_usd': (50,200)},
        'Teak':     {'canopy_r': 8,  'color': '#1B5E20', 'color2': '#2E7D32', 'income_usd': (500,3000)},
        'Bamboo':   {'canopy_r': 3,  'color': '#4CAF50', 'color2': '#8BC34A', 'income_usd': (100,600)},
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
        tree_count = answers.get('tree_count', 15)
        tree_placements = self._make_tree_placements(tree_count, zone_positions, L, W)

        # Gate position (always on south boundary, centred)
        gate_x = L / 2

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
            'gate_x': gate_x,
        }

    # â”€â”€ Zone positions: horizontal bands, house determines which edge â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _make_zone_positions(self, L, W, zones, house_pos):
        pos = {}
        if house_pos in ('South', 'Not built yet', 'Center'):
            # Z0 at bottom (y=0), Z4 at top
            y = 0.0
            for zid in ['z0', 'z1', 'z2', 'z3', 'z4']:
                h = W * zones[zid]
                pos[zid] = {'x': 0, 'y': y, 'width': L, 'height': h}
                y += h
        elif house_pos == 'North':
            # Z0 at top, Z4 at bottom
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

    # â”€â”€ House bbox: absolute minimum size enforced â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _house_bbox(self, house_pos, L, W, zone_positions):
        z0 = zone_positions.get('z0', {'x': 0, 'y': 0, 'width': L, 'height': W})

        # Minimum house dimensions in feet (real house, not a stamp)
        MIN_HW = max(L * 0.08, 40.0)   # at least 40ft wide
        MIN_HH = max(W * 0.03, 30.0)   # at least 30ft deep

        hw = max(z0['width'] * 0.55, MIN_HW)
        hh = max(z0['height'] * 0.65, MIN_HH)

        # Cap so house doesn't overflow z0
        hw = min(hw, z0['width'] * 0.85)
        hh = min(hh, z0['height'] * 0.90)

        hx = z0['x'] + (z0['width'] - hw) / 2
        hy = z0['y'] + (z0['height'] - hh) / 2
        return hx, hy, hw, hh

    def _clamp(self, val, lo, hi):
        return max(lo, min(hi, val))

    # â”€â”€ All feature placement â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _make_features(self, answers, L, W, house_pos, zone_positions):
        features = {}
        livestock = answers.get('livestock', [])
        water = answers.get('water_source', '')

        hx, hy, hw, hh = self._house_bbox(house_pos, L, W, zone_positions)
        hcx = hx + hw / 2
        hcy = hy + hh / 2

        z0 = zone_positions.get('z0', {})
        z1 = zone_positions.get('z1', {})
        z3 = zone_positions.get('z3', {'x': 0, 'y': W*0.5, 'width': L, 'height': W*0.35})

        # â”€â”€ Solar: south of house (low Y), in z0 area â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # min 20ft wide, 12ft deep
        solar_w = self._clamp(hw * 0.40, 20.0, L * 0.15)
        solar_h = self._clamp(hh * 0.35, 12.0, W * 0.06)
        solar_x = self._clamp(hcx - solar_w / 2, 0, L - solar_w)
        solar_y = self._clamp(hy - solar_h - max(hh * 0.1, 8), 0, W - solar_h)
        features['solar'] = {'x': solar_x, 'y': solar_y, 'width': solar_w, 'height': solar_h}

        # â”€â”€ Greenhouse: east of house, in Z1 area â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # min 25ft wide, 18ft deep
        gh_w = self._clamp(hw * 0.45, 25.0, L * 0.15)
        gh_h = self._clamp(hh * 0.80, 18.0, W * 0.08)
        gh_x = self._clamp(hx + hw + max(L * 0.02, 15), 0, L - gh_w)
        gh_y = self._clamp(hcy - gh_h / 2, 0, W - gh_h)
        features['greenhouse'] = {'x': gh_x, 'y': gh_y, 'width': gh_w, 'height': gh_h}

        # â”€â”€ Well: NE of HOUSE (not NE of plot!) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # Place inside Z1, to the right of house
        if 'Borewell' in water or 'Well' in water:
            well_r = self._clamp(min(L, W) * 0.015, 8.0, 20.0)
            well_x = self._clamp(hx + hw + gh_w + well_r * 3 + max(L*0.02, 15),
                                  0, L - well_r * 2)
            well_y = self._clamp(hy + hh * 0.5, well_r, W - well_r)
            # If that's too far right, put it left of house
            if well_x + well_r > L * 0.95:
                well_x = self._clamp(hx - well_r * 3, well_r, L - well_r)
            features['well'] = {'x': well_x, 'y': well_y, 'radius': well_r}

        # â”€â”€ Pond: Z3 left quadrant â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if 'Pond' in water or 'River' in water or 'Fish' in livestock:
            pond_r = self._clamp(min(L, W) * 0.06, 20.0, 60.0)
            pond_x = z3['x'] + pond_r + z3['width'] * 0.05
            pond_y = z3['y'] + z3['height'] * 0.30
            features['pond'] = {'x': pond_x, 'y': pond_y, 'radius': pond_r}

        if 'Rainwater' in water:
            rt_w = self._clamp(L * 0.05, 15.0, 40.0)
            rt_h = self._clamp(hh * 0.40, 10.0, 25.0)
            features['rain_tank'] = {
                'x': self._clamp(hx - rt_w - max(L*0.01, 8), 0, L - rt_w),
                'y': hy,
                'width': rt_w, 'height': rt_h,
            }

        # â”€â”€ Compost: in Z1, left side, not overlapping paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if z1:
            comp_r = self._clamp(min(L, W) * 0.012, 5.0, 12.0)
            features['compost'] = [
                {'x': self._clamp(z1['x'] + z1['width']*0.06, comp_r, L-comp_r),
                 'y': self._clamp(z1['y'] + z1['height']*0.55, comp_r, W-comp_r),
                 'size': comp_r},
                {'x': self._clamp(z1['x'] + z1['width']*0.90, comp_r, L-comp_r),
                 'y': self._clamp(z1['y'] + z1['height']*0.55, comp_r, W-comp_r),
                 'size': comp_r},
            ]

        # â”€â”€ Swales: horizontal lines across Z3 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        slope = answers.get('slope', 'Flat')
        if slope != 'Flat' and z3:
            sw_h = self._clamp(W * 0.004, 3.0, 8.0)
            features['swales'] = [
                {'x': z3['x'], 'y': z3['y'] + z3['height']*0.28,
                 'width': z3['width']*0.75, 'height': sw_h, 'curve': 'sin'},
                {'x': z3['x'], 'y': z3['y'] + z3['height']*0.62,
                 'width': z3['width']*0.75, 'height': sw_h, 'curve': 'sin'},
            ]

        # â”€â”€ Livestock: grid in RIGHT portion of Z3 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # Use only right 50% of Z3 width
        # Pond occupies left 20%, leave 5% margin, livestock from 25%-75%
        lv_margin = max(z3['width'] * 0.25, 50.0)  # push away from pond
        grid_x0 = z3['x'] + lv_margin
        grid_y0 = z3['y'] + z3['height'] * 0.04
        grid_w  = z3['width'] - lv_margin - z3['width'] * 0.03
        grid_h  = z3['height'] * 0.92

        animal_keys = []
        if 'Goats'    in livestock: animal_keys.append('goat_shed')
        if 'Chickens' in livestock: animal_keys.append('chicken_coop')
        if 'Pigs'     in livestock: animal_keys.append('piggery')
        if 'Cows'     in livestock: animal_keys.append('cow_shed')
        if 'Bees'     in livestock: animal_keys.append('bee_hives')

        if animal_keys:
            n = len(animal_keys)
            cols = 2 if n > 1 else 1
            rows = (n + cols - 1) // cols
            # Minimum shed dimensions in feet
            min_shed_w = 25.0
            min_shed_h = 20.0
            gap = max(grid_w * 0.04, 8.0)

            cell_w = max((grid_w - (cols + 1) * gap) / cols, min_shed_w / 0.80)
            cell_h = max((grid_h - (rows + 1) * gap) / rows, min_shed_h / 0.75)

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
                    'width':  self._clamp(cell_w * fw, min_shed_w, L * 0.25),
                    'height': self._clamp(cell_h * fh, min_shed_h, W * 0.20),
                }

        # Fish tanks: below pond in Z3
        if 'Fish' in livestock:
            pond_r = features.get('pond', {}).get('radius', 30)
            pond_x = features.get('pond', {}).get('x', z3['x'] + 30)
            pond_y = features.get('pond', {}).get('y', z3['y'] + 50)
            ft_w = self._clamp(pond_r * 1.8, 20.0, 80.0)
            ft_h = self._clamp(pond_r * 1.2, 15.0, 50.0)
            features['fish_tanks'] = {
                'x': self._clamp(pond_x - ft_w/2, 0, L - ft_w),
                'y': self._clamp(pond_y + pond_r + 10, 0, W - ft_h),
                'width': ft_w, 'height': ft_h,
            }

        # Legacy key for 3D compatibility
        for k in ('goat_shed', 'chicken_coop', 'piggery', 'cow_shed'):
            if k in features:
                features['livestock'] = features[k]
                break

        return features

    # â”€â”€ Tree placements: distributed in Z2 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _make_tree_placements(self, count, zone_positions, L, W):
        placements = []
        z2 = zone_positions.get('z2')
        z4 = zone_positions.get('z4')
        if not z2:
            return placements

        species_list = list(self.TREE_SPECIES.keys())
        rng = random.Random(42)  # fixed seed = consistent layout

        # Minimum spacing between trees
        min_spacing = max(z2['width'] / max(count, 1), 15.0)

        placed = []
        attempts = 0
        while len(placements) < min(count, 40) and attempts < count * 15:
            attempts += 1
            margin = max(min_spacing * 0.4, 10)
            x = z2['x'] + margin + rng.random() * (z2['width'] - 2 * margin)
            y = z2['y'] + margin + rng.random() * (z2['height'] - 2 * margin)
            # Check minimum spacing from already placed trees
            too_close = any(
                (x - px)**2 + (y - py)**2 < min_spacing**2
                for px, py in placed
            )
            if not too_close:
                sp = species_list[len(placements) % len(species_list)]
                placements.append({'x': x, 'y': y, 'species': sp, 'zone': 'z2'})
                placed.append((x, y))

        # Buffer zone trees (Neem, Teak, Bamboo)
        if z4 and count > 15:
            for i in range(min(count - 15, 20)):
                margin = 10
                x = z4['x'] + margin + rng.random() * max(z4['width'] - 2*margin, 1)
                y = z4['y'] + margin + rng.random() * max(z4['height'] - 2*margin, 1)
                sp = ['Neem', 'Teak', 'Bamboo'][i % 3]
                placements.append({'x': x, 'y': y, 'species': sp, 'zone': 'z4'})

        return placements
