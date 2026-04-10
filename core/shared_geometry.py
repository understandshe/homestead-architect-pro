"""
shared_geometry.py — SINGLE SOURCE OF TRUTH
Homestead Architect Pro 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOTH 2D and 3D MUST use this for ALL positions.
This ensures maps are IDENTICAL.
"""
import math
from typing import Dict, Any, Tuple, List, Optional


class HomesteadGeometry:
    """ONE geometry engine for BOTH 2D and 3D."""

    def __init__(self, layout: Dict[str, Any]):
        self.layout = layout
        dims = layout.get('dimensions', {})
        self.L = max(50.0, float(dims.get('L', dims.get('length', 300))))
        self.W = max(50.0, float(dims.get('W', dims.get('width', 300))))
        self.unit = min(self.L, self.W)
        self.scale = max(self.L, self.W) / 300.0

    # ══════════════════════════════════════════════════
    #  HOUSE BBOX — EXACTLY SAME FOR 2D + 3D
    #  This MUST match what layout_engine uses for features
    # ══════════════════════════════════════════════════
    def house_bbox(self) -> Tuple[float, float, float, float]:
        """
        Returns (hx, hy, hw, hh) — IDENTICAL for both maps.
        Matches layout_engine._house_bbox formula exactly.
        """
        zp = self.layout.get('zone_positions', {})
        z0 = zp.get('z0', {'x': 0, 'y': 0, 'width': self.L, 'height': self.W})

        MIN_HW = max(self.L * 0.08, 40.0)
        MIN_HH = max(self.W * 0.03, 30.0)
        hw = max(z0['width'] * 0.55, MIN_HW)
        hh = max(z0['height'] * 0.65, MIN_HH)
        hw = min(hw, z0['width'] * 0.85)
        hh = min(hh, z0['height'] * 0.90)
        hx = z0['x'] + (z0['width'] - hw) / 2
        hy = z0['y'] + (z0['height'] - hh) / 2
        return hx, hy, hw, hh

    # ══════════════════════════════════════════════════
    #  DOOR POSITION
    # ══════════════════════════════════════════════════
    def house_door(self) -> Tuple[float, float]:
        hx, hy, hw, hh = self.house_bbox()
        return hx + hw / 2, hy

    # ══════════════════════════════════════════════════
    #  GATE POSITION
    # ══════════════════════════════════════════════════
    def main_gate(self) -> Tuple[float, float]:
        return self.L / 2, 0

    # ══════════════════════════════════════════════════
    #  ROAD NETWORK — shared for both 2D + 3D
    # ══════════════════════════════════════════════════
    def road_network(self) -> List[Dict[str, Any]]:
        """
        Returns list of road segments for BOTH maps.
        Each: {name, points:[(x,y),...], width, color, alpha, zorder}
        """
        hx, hy, hw, hh = self.house_bbox()
        gcx, _ = self.main_gate()
        door_cx, door_cy = self.house_door()
        rw_main = max(7, self.unit * 0.030)
        rw_sec = max(5, self.unit * 0.018)
        rw_br = max(3, self.unit * 0.012)
        zones = self.layout.get('zone_positions', {})
        feats = self.layout.get('features', {})
        roads = []

        # 1. MAIN ROAD: Gate → House front
        mid_x = door_cx + (gcx - door_cx) * 0.15
        mid_y = door_cy * 0.45
        roads.append({
            'name': 'main_road',
            'points': [(gcx, 0), (mid_x, mid_y), (door_cx, door_cy)],
            'width': rw_main, 'color': '#D2B48C', 'alpha': 0.90, 'zorder': 4,
        })

        if self.unit < 150:
            return roads

        # 2. SECONDARY: House → Z1 edge
        if 'z1' in zones:
            z1 = zones['z1']
            z1_entry_x = z1['x'] + z1['width'] * 0.5
            if z1['y'] > hy + hh:
                z1_entry_y = z1['y']
            elif z1['y'] + z1['height'] < hy:
                z1_entry_y = z1['y'] + z1['height']
            else:
                z1_entry_y = z1['y']
            start_x = hx + hw * 0.4
            start_y = hy + hh
            ctrl_x = start_x + (z1_entry_x - start_x) * 0.4
            ctrl_y = (start_y + z1_entry_y) * 0.5
            roads.append({
                'name': 'house_to_z1',
                'points': [(start_x, start_y), (ctrl_x, ctrl_y), (z1_entry_x, z1_entry_y)],
                'width': rw_sec, 'color': '#D7CCC8', 'alpha': 0.76, 'zorder': 4,
            })

        # 3. SECONDARY: House → Z3 entry
        z3 = zones.get('z3')
        if z3:
            z3_entry_x = z3['x'] + z3['width'] * 0.35
            if z3['y'] > hy + hh:
                z3_entry_y = z3['y']
            elif z3['y'] + z3['height'] < hy:
                z3_entry_y = z3['y'] + z3['height']
            else:
                z3_entry_y = z3['y']
            start_x2 = hx + hw * 0.75
            ctrl2_x = start_x2 + self.L * 0.015
            ctrl2_y = (hy + hh + z3_entry_y) * 0.5
            roads.append({
                'name': 'house_to_z3',
                'points': [(start_x2, hy + hh), (ctrl2_x, ctrl2_y), (z3_entry_x, z3_entry_y)],
                'width': rw_sec, 'color': '#D7CCC8', 'alpha': 0.72, 'zorder': 4,
            })

            # 4. BRANCH ROADS inside Z3 → each shed
            shed_keys = ['goat_shed', 'chicken_coop', 'piggery', 'cow_shed', 'fish_tanks', 'bee_hives']
            for sk in shed_keys:
                if sk not in feats or not feats[sk]:
                    continue
                f = feats[sk]
                if not isinstance(f, dict):
                    continue
                sx = float(f.get('x', 0)) + float(f.get('width', 30)) / 2
                sy = float(f.get('y', 0))
                bx1 = max(z3['x'], min(z3_entry_x, z3['x'] + z3['width']))
                by1 = z3_entry_y
                bx2 = max(z3['x'], min(sx, z3['x'] + z3['width']))
                by2 = max(z3['y'], min(sy, z3['y'] + z3['height']))
                roads.append({
                    'name': f'z3_to_{sk}',
                    'points': [(bx1, by1), (bx2, by2)],
                    'width': rw_br, 'color': '#BCAAA4', 'alpha': 0.62, 'zorder': 3,
                })

        return roads

    # ══════════════════════════════════════════════════
    #  SLOPE Z — shared terrain height for 3D
    # ══════════════════════════════════════════════════
    def slope_z(self, x: float, y: float) -> float:
        slope = self.layout.get('slope', 'Flat')
        sf = max(self.L, self.W) * 0.018 * self.scale
        if slope == 'South':    return y / self.W * sf
        if slope == 'North':    return (1 - y / self.W) * sf
        if slope == 'East':     return x / self.L * sf
        if slope == 'West':     return (1 - x / self.L) * sf
        if slope == 'Mixed/Undulating':
            return (math.sin(x / self.L * math.pi) * 0.5 +
                    math.cos(y / self.W * math.pi) * 0.3) * sf
        return 0.0

    # ══════════════════════════════════════════════════
    #  FEATURE / ZONE helpers
    # ══════════════════════════════════════════════════
    def get_feature(self, key: str) -> Optional[Dict]:
        feats = self.layout.get('features', {})
        f = feats.get(key)
        return f if (f and isinstance(f, dict)) else None

    def get_zone(self, key: str) -> Optional[Dict]:
        return self.layout.get('zone_positions', {}).get(key)

    def tree_count(self) -> int:
        tc = self.layout.get('tree_count', 15)
        try: tc = int(tc)
        except: tc = 15
        return max(3, min(60, tc))
