"""
shared_geometry.py — SINGLE SOURCE OF TRUTH
Homestead Architect Pro 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOTH 2D and 3D MUST use this for ALL positions.
This ensures maps are IDENTICAL.

ROAD LOGIC:
  - Gate always on boundary OPPOSITE to house
  - North house → gate South (y=0), road goes UP
  - South house → gate South (y=0), road goes UP  
  - East house  → gate West (x=0),  road goes RIGHT
  - West house  → gate East (x=L),  road goes LEFT
  - Door always faces gate (nearest face to gate)
  - Branch roads to ONLY the sheds user selected
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
        self._hp = layout.get('house_position', 'South')

    # ══════════════════════════════════════════════════
    #  HOUSE BBOX
    # ══════════════════════════════════════════════════
    def house_bbox(self) -> Tuple[float, float, float, float]:
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
    #  GATE — always on boundary FACING the road
    #  Rule: gate is on the boundary closest to public road
    #        which is OPPOSITE to where house_pos is
    # ══════════════════════════════════════════════════
    def main_gate(self) -> Tuple[float, float]:
        hp = self._hp
        if hp == 'East':
            return 0.0, self.W / 2        # gate on West boundary
        elif hp == 'West':
            return self.L, self.W / 2     # gate on East boundary
        else:
            # North, South, Center, Not built yet → gate always South
            return self.L / 2, 0.0

    # ══════════════════════════════════════════════════
    #  DOOR — face of house nearest to gate
    # ══════════════════════════════════════════════════
    def house_door(self) -> Tuple[float, float]:
        hx, hy, hw, hh = self.house_bbox()
        hp = self._hp
        if hp == 'East':
            # House on right → door on LEFT face (faces west gate)
            return hx, hy + hh / 2
        elif hp == 'West':
            # House on left → door on RIGHT face (faces east gate)
            return hx + hw, hy + hh / 2
        elif hp == 'North':
            # House at top → door on BOTTOM face (faces south gate)
            return hx + hw / 2, hy
        else:
            # South / Center → door on BOTTOM face
            return hx + hw / 2, hy

    # ══════════════════════════════════════════════════
    #  ROAD NETWORK
    #  - Main road: Gate → House door (straight, correct direction)
    #  - Secondary: House → Z1 (kitchen garden side)
    #  - Secondary: House → Z3 entry
    #  - Branch roads: Z3 entry → ONLY sheds user selected
    # ══════════════════════════════════════════════════
    def road_network(self) -> List[Dict[str, Any]]:
        hx, hy, hw, hh = self.house_bbox()
        gcx, gcy = self.main_gate()
        door_cx, door_cy = self.house_door()
        hp = self._hp

        rw_main = max(7, self.unit * 0.030)
        rw_sec  = max(5, self.unit * 0.018)
        rw_br   = max(3, self.unit * 0.012)
        zones = self.layout.get('zone_positions', {})
        feats = self.layout.get('features', {})
        roads = []

        # ── 1. MAIN ROAD: Gate → House door ──────────────────────────
        # Simple curve: 1 control point, road goes directly toward door
        # No zigzag, no wrong direction
        if hp in ('East', 'West'):
            # Horizontal road
            ctrl_x = gcx + (door_cx - gcx) * 0.5
            ctrl_y = gcy + (door_cy - gcy) * 0.3
        else:
            # Vertical road (North, South, Center)
            # ctrl point: X shifts slightly toward door, Y halfway
            ctrl_x = gcx + (door_cx - gcx) * 0.3
            ctrl_y = gcy + (door_cy - gcy) * 0.5

        roads.append({
            'name': 'main_road',
            'points': [(gcx, gcy), (ctrl_x, ctrl_y), (door_cx, door_cy)],
            'width': rw_main, 'color': '#D2B48C', 'alpha': 0.90, 'zorder': 4,
        })

        if self.unit < 150:
            return roads

        # ── 2. SECONDARY: House → Z1 edge ────────────────────────────
        if 'z1' in zones:
            z1 = zones['z1']
            z1_entry_x = z1['x'] + z1['width'] * 0.5

            # Find which face of z1 is nearest to house
            if z1['y'] >= hy + hh:
                z1_entry_y = z1['y']               # z1 is above house
            elif z1['y'] + z1['height'] <= hy:
                z1_entry_y = z1['y'] + z1['height'] # z1 is below house
            elif z1['x'] >= hx + hw:
                z1_entry_x = z1['x']               # z1 is right of house
                z1_entry_y = z1['y'] + z1['height'] * 0.5
            else:
                z1_entry_x = z1['x'] + z1['width'] # z1 is left of house
                z1_entry_y = z1['y'] + z1['height'] * 0.5

            # Start from house face nearest z1
            if z1['y'] >= hy + hh:
                start_x = hx + hw * 0.4
                start_y = hy + hh
            elif z1['y'] + z1['height'] <= hy:
                start_x = hx + hw * 0.4
                start_y = hy
            elif z1['x'] >= hx + hw:
                start_x = hx + hw
                start_y = hy + hh * 0.5
            else:
                start_x = hx
                start_y = hy + hh * 0.5

            ctrl_x = start_x + (z1_entry_x - start_x) * 0.4
            ctrl_y = start_y + (z1_entry_y - start_y) * 0.5
            roads.append({
                'name': 'house_to_z1',
                'points': [(start_x, start_y), (ctrl_x, ctrl_y),
                           (z1_entry_x, z1_entry_y)],
                'width': rw_sec, 'color': '#D7CCC8', 'alpha': 0.76, 'zorder': 4,
            })

        # ── 3. SECONDARY: House → Z3 entry ───────────────────────────
        z3 = zones.get('z3')
        if z3:
            z3_entry_x = z3['x'] + z3['width'] * 0.35

            if z3['y'] >= hy + hh:
                z3_entry_y = z3['y']
            elif z3['y'] + z3['height'] <= hy:
                z3_entry_y = z3['y'] + z3['height']
            elif z3['x'] >= hx + hw:
                z3_entry_x = z3['x']
                z3_entry_y = z3['y'] + z3['height'] * 0.35
            else:
                z3_entry_x = z3['x'] + z3['width']
                z3_entry_y = z3['y'] + z3['height'] * 0.35

            # Start from house face nearest z3
            if z3['y'] >= hy + hh:
                start_x2 = hx + hw * 0.75
                start_y2 = hy + hh
            elif z3['y'] + z3['height'] <= hy:
                start_x2 = hx + hw * 0.75
                start_y2 = hy
            elif z3['x'] >= hx + hw:
                start_x2 = hx + hw
                start_y2 = hy + hh * 0.5
            else:
                start_x2 = hx
                start_y2 = hy + hh * 0.5

            ctrl2_x = start_x2 + (z3_entry_x - start_x2) * 0.5
            ctrl2_y = start_y2 + (z3_entry_y - start_y2) * 0.5
            roads.append({
                'name': 'house_to_z3',
                'points': [(start_x2, start_y2), (ctrl2_x, ctrl2_y),
                           (z3_entry_x, z3_entry_y)],
                'width': rw_sec, 'color': '#D7CCC8', 'alpha': 0.72, 'zorder': 4,
            })

            # ── 4. BRANCH ROADS: Z3 entry → ONLY existing sheds ──────
            # Only sheds that user actually selected will be in feats
            shed_keys = [
                'goat_shed', 'chicken_coop', 'piggery',
                'cow_shed', 'fish_tanks', 'bee_hives'
            ]
            for sk in shed_keys:
                if sk not in feats or not feats[sk]:
                    continue                        # user didn't select → skip
                f = feats[sk]
                if not isinstance(f, dict):
                    continue
                # Road goes to FRONT of shed (center-x, front-y)
                shed_cx = float(f.get('x', 0)) + float(f.get('width', 30)) / 2
                shed_front_y = float(f.get('y', 0))

                # Clamp inside z3
                bx1 = max(z3['x'], min(z3_entry_x, z3['x'] + z3['width']))
                by1 = z3_entry_y
                bx2 = max(z3['x'] + 1, min(shed_cx, z3['x'] + z3['width'] - 1))
                by2 = max(z3['y'] + 1, min(shed_front_y, z3['y'] + z3['height'] - 1))

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
    #  HELPERS
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
