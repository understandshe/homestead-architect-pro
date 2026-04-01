"""
Professional 2D Architectural Visualizer
Publication-quality site plans
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Arc, PathPatch
from matplotlib.path import Path
import numpy as np
from io import BytesIO


class Visualizer2D:
    """Creates professional architectural drawings"""
    
    def __init__(self):
        self.colors = {
            'residential': '#F5F5DC',
            'kitchen': '#90EE90',
            'forest': '#228B22',
            'pasture': '#F0E68C',
            'buffer': '#DDA0DD',
            'water': '#4682B4',
            'building': '#8B4513',
            'roof': '#A0522D',
            'solar': '#FFD700',
            'greenhouse': '#E0FFE0',
            'livestock': '#DEB887'
        }
    
    def create(self, layout, answers):
        """Generate professional site plan"""
        
        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        
        fig, ax = plt.subplots(1, 1, figsize=(16, 12), dpi=150)
        ax.set_facecolor('#F0F8FF')
        
        # Professional title block
        self._add_title_block(ax, layout, L, W)
        
        # Draw property boundary with survey-style
        self._draw_property_boundary(ax, L, W)
        
        # Draw contour lines if sloped
        if layout.get('slope') != 'Flat':
            self._draw_contour_lines(ax, L, W, layout['slope'])
        
        # Draw zones with professional hatching
        self._draw_zones_professional(ax, layout, L, W)
        
        # Draw house with architectural detail
        self._draw_house_professional(ax, layout, L, W)
        
        # Draw water features
        self._draw_water_features(ax, layout, L, W)
        
        # Draw solar & greenhouse
        self._draw_utilities(ax, layout, L, W)
        
        # Draw livestock housing (PROFESSIONAL)
        self._draw_livestock_housing(ax, layout, L, W)
        
        # Draw trees and vegetation
        self._draw_vegetation(ax, layout, L, W)
        
        # Add north arrow, scale, legend
        self._add_north_arrow(ax, L, W)
        self._add_scale_bar(ax, L, W)
        self._add_legend_professional(ax, L, W)
        
        # Dimension lines
        self._add_dimensions(ax, L, W)
        
        # Set limits
        margin = max(L, W) * 0.15
        ax.set_xlim(-margin, L + margin)
        ax.set_ylim(-margin, W + margin)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    def _draw_property_boundary(self, ax, L, W):
        """Survey-style property boundary"""
        # Main boundary
        rect = Rectangle((0, 0), L, W, linewidth=3, 
                       edgecolor='black', facecolor='none', linestyle='-')
        ax.add_patch(rect)
        
        # Corner markers (survey style)
        corners = [(0, 0), (L, 0), (L, W), (0, W)]
        for i, (x, y) in enumerate(corners, 1):
            circle = Circle((x, y), min(L,W)*0.015, facecolor='white', 
                          edgecolor='black', linewidth=2, zorder=10)
            ax.add_patch(circle)
            ax.text(x, y, str(i), ha='center', va='center', 
                   fontsize=8, fontweight='bold', zorder=11)
    
    def _draw_zones_professional(self, ax, layout, L, W):
        """Draw zones with professional patterns"""
        zone_positions = layout.get('zone_positions', {})
        zone_colors = {
            'z0': self.colors['residential'],
            'z1': self.colors['kitchen'],
            'z2': self.colors['forest'],
            'z3': self.colors['pasture'],
            'z4': self.colors['buffer']
        }
        zone_names = {
            'z0': 'ZONE 0\nRESIDENTIAL',
            'z1': 'ZONE 1\nKITCHEN GARDEN',
            'z2': 'ZONE 2\nFOOD FOREST',
            'z3': 'ZONE 3\nPASTURE/CROPS',
            'z4': 'ZONE 4\nBUFFER'
        }
        
        for zone_id, pos in zone_positions.items():
            # Zone fill with pattern
            rect = Rectangle((pos['x'], pos['y']), pos['width'], pos['height'],
                          facecolor=zone_colors.get(zone_id, '#CCCCCC'),
                          edgecolor='#2E7D32', linewidth=2, alpha=0.6)
            ax.add_patch(rect)
            
            # Zone border
            border = Rectangle((pos['x'], pos['y']), pos['width'], pos['height'],
                              fill=False, edgecolor='#1B5E20', linewidth=3)
            ax.add_patch(border)
            
            # Zone label with background
            cx = pos['x'] + pos['width']/2
            cy = pos['y'] + pos['height']/2
            area = int(pos['width'] * pos['height'])
            
            # White background for text
            text_bg = Rectangle((cx-30, cy-20), 60, 40, 
                               facecolor='white', edgecolor='black',
                               alpha=0.9, zorder=5)
            ax.add_patch(text_bg)
            
            ax.text(cx, cy+5, zone_names.get(zone_id, zone_id.upper()),
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   color='#1B5E20', zorder=6)
            ax.text(cx, cy-10, f'{area:,} sq.ft.',
                   ha='center', va='center', fontsize=8,
                   color='#2E7D32', zorder=6)
    
    def _draw_house_professional(self, ax, layout, L, W):
        """Professional house drawing with architectural details"""
        house_pos = layout.get('house_position', 'Center')
        
        # Determine house position
        if house_pos == 'North':
            hx, hy, hw, hh = L*0.3, W*0.82, L*0.4, W*0.12
        elif house_pos == 'South':
            hx, hy, hw, hh = L*0.3, W*0.06, L*0.4, W*0.12
        elif house_pos == 'East':
            hx, hy, hw, hh = L*0.75, W*0.35, L*0.2, W*0.3
        elif house_pos == 'West':
            hx, hy, hw, hh = L*0.05, W*0.35, L*0.2, W*0.3
        else:
            hx, hy, hw, hh = L*0.35, W*0.4, L*0.3, W*0.2
        
        # Main building (walls)
        walls = Rectangle((hx, hy), hw, hh,
                         facecolor=self.colors['building'],
                         edgecolor='#3E2723', linewidth=3)
        ax.add_patch(walls)
        
        # Roof (gable style)
        roof_height = hh * 0.3
        roof = Polygon([
            [hx - hw*0.05, hy + hh],
            [hx + hw/2, hy + hh + roof_height],
            [hx + hw*1.05, hy + hh]
        ], facecolor=self.colors['roof'], edgecolor='#3E2723', linewidth=2)
        ax.add_patch(roof)
        
        # Door
        door_w = hw * 0.15
        door_h = hh * 0.35
        door = Rectangle((hx + hw/2 - door_w/2, hy), door_w, door_h,
                        facecolor='#4E342E', edgecolor='black', linewidth=2)
        ax.add_patch(door)
        
        # Door knob
        knob = Circle((hx + hw/2 + door_w/3, hy + door_h/2), 
                     min(hw,hh)*0.015, facecolor='#FFD700', edgecolor='black')
        ax.add_patch(knob)
        
        # Windows (2 windows)
        win_w = hw * 0.2
        win_h = hh * 0.2
        for wx in [hx + hw*0.15, hx + hw*0.65]:
            # Window frame
            window = Rectangle((wx, hy + hh*0.5), win_w, win_h,
                              facecolor='#87CEEB', edgecolor='#3E2723', linewidth=2)
            ax.add_patch(window)
            # Window cross
            ax.plot([wx + win_w/2, wx + win_w/2], [hy + hh*0.5, hy + hh*0.7], 
                   'k-', linewidth=1)
            ax.plot([wx, wx + win_w], [hy + hh*0.6, hy + hh*0.6], 
                   'k-', linewidth=1)
        
        # Chimney
        chim = Rectangle((hx + hw*0.7, hy + hh), hw*0.08, hh*0.25,
                        facecolor='#8B4513', edgecolor='black')
        ax.add_patch(chim)
        
        # Smoke
        for i, offset in enumerate([0.1, 0.2, 0.3]):
            smoke = Circle((hx + hw*0.74 + offset*5, hy + hh*1.3 + offset*10), 
                          3+i, facecolor='gray', alpha=0.3-i*0.08, edgecolor='none')
            ax.add_patch(smoke)
        
        # Label
        ax.text(hx + hw/2, hy + hh + roof_height + 15, 'RESIDENCE',
               ha='center', fontsize=10, fontweight='bold', color='#BF360C')
    
    def _draw_livestock_housing(self, ax, layout, L, W):
        """PROFESSIONAL livestock housing - detailed structures"""
        features = layout.get('features', {})
        
        # Goat Shed
        if 'goat_shed' in features:
            f = features['goat_shed']
            self._draw_goat_shed_professional(ax, f['x'], f['y'], 
                                              f['width'], f['height'])
        
        # Chicken Coop
        if 'chicken_coop' in features:
            f = features['chicken_coop']
            self._draw_chicken_coop_professional(ax, f['x'], f['y'],
                                                 f['width'], f['height'])
        
        # Piggery
        if 'piggery' in features:
            f = features['piggery']
            self._draw_piggery_professional(ax, f['x'], f['y'],
                                            f['width'], f['height'])
    
    def _draw_goat_shed_professional(self, ax, x, y, w, h):
        """Detailed goat shed with roof, feeding, ventilation"""
        # Foundation
        foundation = Rectangle((x-2, y-2), w+4, h+4,
                              facecolor='#8D6E63', edgecolor='black', linewidth=1)
        ax.add_patch(foundation)
        
        # Main shed
        shed = Rectangle((x, y), w, h,
                        facecolor=self.colors['livestock'],
                        edgecolor='#5D4037', linewidth=3)
        ax.add_patch(shed)
        
        # Gable roof
        roof = Polygon([
            [x-5, y+h], [x+w/2, y+h+15], [x+w+5, y+h]
        ], facecolor='#A1887F', edgecolor='#3E2723', linewidth=2)
        ax.add_patch(roof)
        
        # Ventilation windows (top)
        for vx in [x + w*0.2, x + w*0.5, x + w*0.8]:
            vent = Rectangle((vx-8, y+h-10), 16, 8,
                            facecolor='#B3E5FC', edgecolor='black')
            ax.add_patch(vent)
        
        # Feeding trough (front)
        trough = Rectangle((x+10, y-8), w-20, 8,
                         facecolor='#5D4037', edgecolor='black')
        ax.add_patch(trough)
        
        # Entry door
        door = Rectangle((x+w/2-12, y), 24, 35,
                        facecolor='#4E342E', edgecolor='black')
        ax.add_patch(door)
        
        # Fence (front)
        for fx in range(int(x), int(x+w), 15):
            ax.plot([fx, fx], [y-25, y-8], color='#8D6E63', linewidth=2)
        ax.plot([x, x+w], [y-8, y-8], color='#8D6E63', linewidth=2)
        
        # Label
        ax.text(x + w/2, y + h + 25, 'GOAT SHED (10 animals)',
               ha='center', fontsize=9, fontweight='bold', color='#5D4037')
    
    def _draw_chicken_coop_professional(self, ax, x, y, w, h):
        """Professional chicken coop with nesting boxes"""
        # Main coop
        coop = Rectangle((x, y), w, h,
                        facecolor='#FFF8E1',
                        edgecolor='#F57F17', linewidth=3)
        ax.add_patch(coop)
        
        # Slanted roof
        roof = Polygon([
            [x-3, y+h], [x+w+3, y+h+10], [x+w+3, y+h], [x-3, y+h-5]
        ], facecolor='#FFCC80', edgecolor='#E65100', linewidth=2)
        ax.add_patch(roof)
        
        # Nesting boxes (side)
        nest = Rectangle((x+w, y+h*0.3), w*0.3, h*0.4,
                        facecolor='#FFE0B2', edgecolor='#E65100', linewidth=2)
        ax.add_patch(nest)
        
        # Nest box openings
        for ny in [y+h*0.4, y+h*0.55, y+h*0.7]:
            nest_open = Arc((x+w+5, ny), 10, 15, angle=0, theta1=0, theta2=180,
                           color='#E65100', linewidth=2)
            ax.add_patch(nest_open)
        
        # Ramp
        ramp = Polygon([
            [x+w*0.3, y], [x+w*0.5, y-20], [x+w*0.7, y]
        ], facecolor='#D7CCC8', edgecolor='#5D4037')
        ax.add_patch(ramp)
        
        # Fence/run area
        run = Rectangle((x-20, y-40), w+60, 40,
                       facecolor='#F1F8E9', edgecolor='#33691E', 
                       linestyle='--', alpha=0.5)
        ax.add_patch(run)
        
        # Label
        ax.text(x + w/2, y + h + 20, 'CHICKEN COOP (50 birds)',
               ha='center', fontsize=8, fontweight='bold', color='#E65100')
    
    def _draw_piggery_professional(self, ax, x, y, w, h):
        """Professional piggery with farrowing crates"""
        # Main building
        building = Rectangle((x, y), w, h,
                            facecolor='#FFCCBC',
                            edgecolor='#BF360C', linewidth=3)
        ax.add_patch(building)
        
        # Sections
        sections = ['FARROWING', 'NURSERY', 'GROWER']
        section_w = w / 3
        
        for i, section in enumerate(sections):
            sx = x + i * section_w
            # Divider walls
            if i > 0:
                ax.plot([sx, sx], [y, y+h], 'k-', linewidth=2)
            
            # Section label
            ax.text(sx + section_w/2, y + h/2, section,
                   ha='center', va='center', fontsize=7,
                   rotation=90 if i == 0 else 0,
                   fontweight='bold', color='#BF360C')
        
        # Roof
        roof = Polygon([
            [x-5, y+h], [x+w/2, y+h+20], [x+w+5, y+h]
        ], facecolor='#FFAB91', edgecolor='#BF360C', linewidth=2)
        ax.add_patch(roof)
        
        # Ventilation fans
        for fx in [x + w*0.15, x + w*0.85]:
            fan = Circle((fx, y+h-15), 8, facecolor='#EEEEEE', 
                        edgecolor='black', linewidth=1)
            ax.add_patch(fan)
            # Fan blades
            for angle in [0, 45, 90, 135]:
                rad = np.radians(angle)
                ax.plot([fx, fx + 6*np.cos(rad)], [y+h-15, y+h-15 + 6*np.sin(rad)],
                       'k-', linewidth=1)
        
        # Label
        ax.text(x + w/2, y + h + 30, 'PIGGERY (5 sows + piglets)',
               ha='center', fontsize=9, fontweight='bold', color='#BF360C')
    
    def _draw_water_features(self, ax, layout, L, W):
        """Draw well, pond, etc."""
        features = layout.get('features', {})
        
        # Borewell
        if 'borewell' in features:
            f = features['borewell']
            # Well circle
            well = Circle((f['x'], f['y']), f['radius'],
                         facecolor=self.colors['water'],
                         edgecolor='#01579B', linewidth=3)
            ax.add_patch(well)
            # Water level
            water = Circle((f['x'], f['y']), f['radius']*0.8,
                          facecolor='#81D4FA', edgecolor='none')
            ax.add_patch(water)
            # Label
            ax.text(f['x'], f['y'], 'W', ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')
            ax.text(f['x'], f['y']-f['radius']-10, 'BOREWELL\n(150 ft)',
                   ha='center', fontsize=8, color='#01579B')
        
        # Pond
        if 'pond' in features:
            f = features['pond']
            # Natural shape
            theta = np.linspace(0, 2*np.pi, 30)
            r = f['radius'] * (1 + 0.15*np.sin(3*theta))
            x_pond = f['x'] + r * np.cos(theta)
            y_pond = f['y'] + r * np.sin(theta)
            
            pond = Polygon(list(zip(x_pond, y_pond)),
                          facecolor='#B3E5FC', edgecolor='#0288D1',
                          linewidth=2, alpha=0.8)
            ax.add_patch(pond)
            
            # Water plants
            for _ in range(5):
                px = f['x'] + np.random.uniform(-f['radius']*0.5, f['radius']*0.5)
                py = f['y'] + np.random.uniform(-f['radius']*0.5, f['radius']*0.5)
                plant = Circle((px, py), 3, facecolor='#4CAF50', edgecolor='none')
                ax.add_patch(plant)
            
            ax.text(f['x'], f['y'], 'POND\n(Aquaculture)', 
                   ha='center', va='center', fontsize=8, color='#01579B')
    
    def _draw_utilities(self, ax, layout, L, W):
        """Solar, greenhouse, etc."""
        features = layout.get('features', {})
        
        # Solar panels
        if 'solar' in features:
            f = features['solar']
            # Panel array
            for i in range(3):
                for j in range(2):
                    panel = Rectangle(
                        (f['x'] + i*(f['width']/3), f['y'] + j*(f['height']/2)),
                        f['width']/3 - 2, f['height']/2 - 2,
                        facecolor=self.colors['solar'],
                        edgecolor='#F57F00', linewidth=1
                    )
                    ax.add_patch(panel)
            
            ax.text(f['x'] + f['width']/2, f['y'] + f['height'] + 10,
                   'SOLAR ARRAY\n(5 kW)', ha='center', fontsize=8, 
                   fontweight='bold', color='#E65100')
        
        # Greenhouse
        if 'greenhouse' in features:
            f = features['greenhouse']
            # Structure
            gh = Rectangle((f['x'], f['y']), f['width'], f['height'],
                          facecolor=self.colors['greenhouse'],
                          edgecolor='#2E7D32', linewidth=2, linestyle='--')
            ax.add_patch(gh)
            
            # Arched roof
            arc = Arc((f['x']+f['width']/2, f['y']+f['height']),
                     f['width'], f['height']*0.3,
                     angle=0, theta1=0, theta2=180,
                     color='#2E7D32', linewidth=2)
            ax.add_patch(arc)
            
            # Internal benches
            for by in [f['y']+10, f['y']+f['height']-20]:
                bench = Rectangle((f['x']+5, by), f['width']-10, 10,
                                 facecolor='#8D6E63', edgecolor='black')
                ax.add_patch(bench)
            
            ax.text(f['x'] + f['width']/2, f['y'] - 10,
                   'GREENHOUSE\n(Seasonal crops)', ha='center', fontsize=8,
                   color='#2E7D32')
    
    def _draw_vegetation(self, ax, layout, L, W):
        """Draw trees and plants"""
        # Sample trees in food forest zone
        zone_pos = layout.get('zone_positions', {})
        if 'z2' in zone_pos:
            z = zone_pos['z2']
            # Tree positions
            tree_positions = [
                (z['x'] + z['width']*0.2, z['y'] + z['height']*0.3),
                (z['x'] + z['width']*0.5, z['y'] + z['height']*0.6),
                (z['x'] + z['width']*0.8, z['y'] + z['height']*0.4),
                (z['x'] + z['width']*0.3, z['y'] + z['height']*0.7),
            ]
            
            for i, (tx, ty) in enumerate(tree_positions):
                # Trunk
                trunk = Rectangle((tx-2, ty-15), 4, 15,
                                 facecolor='#5D4037', edgecolor='black')
                ax.add_patch(trunk)
                
                # Crown (different colors for variety)
                colors = ['#228B22', '#32CD32', '#006400', '#6B8E23']
                crown = Circle((tx, ty+5), 12, 
                              facecolor=colors[i % len(colors)],
                              edgecolor='#1B5E20', linewidth=1)
                ax.add_patch(crown)
                
                # Label
                tree_types = ['Mango', 'Coconut', 'Jackfruit', 'Banana']
                ax.text(tx, ty+20, tree_types[i % len(tree_types)],
                       ha='center', fontsize=7, color='#1B5E20')
    
    def _add_north_arrow(self, ax, L, W):
        """Professional north arrow"""
        nx, ny = L * 0.92, W * 0.08
        
        # Circle
        circle = Circle((nx, ny), 15, facecolor='white', 
                       edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        
        # Arrow
        ax.annotate('', xy=(nx, ny+12), xytext=(nx, ny-5),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        # N label
        ax.text(nx, ny+18, 'N', ha='center', fontsize=12, 
               fontweight='bold', color='red')
    
    def _add_scale_bar(self, ax, L, W):
        """Architectural scale bar"""
        sx, sy = L * 0.05, W * 0.05
        
        # 50 ft scale (or appropriate)
        scale_length = min(50, L * 0.2)
        
        # Bar
        ax.plot([sx, sx + scale_length], [sy, sy], 'k-', linewidth=3)
        ax.plot([sx, sx], [sy-3, sy+3], 'k-', linewidth=2)
        ax.plot([sx + scale_length, sx + scale_length], [sy-3, sy+3], 'k-', linewidth=2)
        
        # Label
        ax.text(sx + scale_length/2, sy - 10, f'{int(scale_length)} ft',
               ha='center', fontsize=9, fontweight='bold')
        ax.text(sx + scale_length/2, sy + 8, 'SCALE',
               ha='center', fontsize=8)
    
    def _add_legend_professional(self, ax, L, W):
        """Professional legend"""
        # Legend box position
        lx, ly = L + 20, W * 0.7
        
        # Box
        legend_box = Rectangle((lx-10, ly-100), 120, 200,
                              facecolor='white', edgecolor='black',
                              linewidth=2, alpha=0.95)
        ax.add_patch(legend_box)
        
        # Title
        ax.text(lx + 50, ly + 85, 'LEGEND', ha='center', 
               fontsize=10, fontweight='bold')
        
        # Items
        items = [
            (self.colors['building'], 'Residence'),
            (self.colors['livestock'], 'Livestock'),
            (self.colors['water'], 'Water'),
            (self.colors['solar'], 'Solar'),
            (self.colors['greenhouse'], 'Greenhouse'),
        ]
        
        for i, (color, label) in enumerate(items):
            y_pos = ly + 60 - i * 25
            rect = Rectangle((lx, y_pos-8), 15, 15, 
                          facecolor=color, edgecolor='black')
            ax.add_patch(rect)
            ax.text(lx + 25, y_pos, label, fontsize=8, va='center')
    
    def _add_dimensions(self, ax, L, W):
        """Dimension lines"""
        # Bottom dimension
        ax.annotate('', xy=(0, -20), xytext=(L, -20),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
        ax.text(L/2, -35, f'{int(L)} ft', ha='center', fontsize=10)
        
        # Left dimension
        ax.annotate('', xy=(-20, 0), xytext=(-20, W),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
        ax.text(-45, W/2, f'{int(W)} ft', ha='center', fontsize=10, rotation=90)
    
    def _add_title_block(self, ax, layout, L, W):
        """Professional title block"""
        title = f"{layout.get('acres', 0):.2f} ACRE HOMESTEAD\n"
        title += f"{int(layout['total_sqft']):,} SQ.FT. | {layout['category'].upper()} SCALE"
        
        ax.text(L/2, W + 40, title, ha='center', va='bottom',
               fontsize=14, fontweight='bold', color='#1B5E20',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9',
                        edgecolor='#2E7D32', linewidth=2))
