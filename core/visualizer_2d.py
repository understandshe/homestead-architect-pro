
# FILE 4: visualizer_2d_v7.py - PREMIUM professional 2D with logical paths

import matplotlib.pyplot as plt
import matplotlib.patches as patches
# ... बाकी सारा कोड सीधा यहाँ से शुरू होगा
"""
Premium 2D Site Plan Visualizer v7
Professional cartographic quality - logical grid-based paths
NO random curves - everything calculated from layout
300 DPI print-ready output
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch, PathPatch
from matplotlib.path import Path
import matplotlib.patheffects as pe
import numpy as np
from io import BytesIO
from typing import Dict, List, Tuple, Optional

class Visualizer2D:
    """Professional 2D site plan generator"""
    
    # Professional color palette
    ZONE_COLORS = {
        'z0': '#FFF8E1',  # Warm cream - residential
        'z1': '#C8E6C9',  # Light green - kitchen garden
        'z2': '#A5D6A7',  # Medium green - food forest
        'z3': '#E6EE9C',  # Yellow-green - pasture
        'z4': '#D1C4E9',  # Light purple - buffer
    }
    
    ZONE_NAMES = {
        'z0': 'ZONE 0\nRESIDENTIAL',
        'z1': 'ZONE 1\nKITCHEN GARDEN', 
        'z2': 'ZONE 2\nFOOD FOREST',
        'z3': 'ZONE 3\nPASTURE/CROPS',
        'z4': 'ZONE 4\nBUFFER',
    }
    
    # Tree colors by species
    TREE_COLORS = {
        'Mango': '#2E7D32', 'Jackfruit': '#1B5E20', 'Coconut': '#33691E',
        'Banana': '#558B2F', 'Guava': '#43A047', 'Papaya': '#66BB6A',
        'Avocado': '#2E7D32', 'Moringa': '#81C784', 'Citrus': '#8BC34A',
        'Neem': '#388E3C', 'Teak': '#1B5E20', 'Bamboo': '#4CAF50',
    }
    
    def __init__(self):
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.size'] = 8
    
    def create(self, layout: Dict, answers: Dict) -> BytesIO:
        """Generate premium 2D site plan"""
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        
        # Create figure with professional size
        fig, ax = plt.subplots(figsize=(16, 12), constrained_layout=True)
        fig.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#E8F5E9')  # Light grass base
        
        # Draw layers from back to front
        self._draw_property_boundary(ax, L, W)
        self._draw_zones(ax, layout)
        self._draw_roads_logical(ax, layout)  # LOGICAL grid roads, not random
        self._draw_water_features(ax, layout)
        self._draw_utilities(ax, layout)
        self._draw_livestock(ax, layout)
        self._draw_kitchen_garden(ax, layout)
        self._draw_trees(ax, layout)
        self._draw_house(ax, layout)
        self._draw_cartographic_elements(ax, L, W, layout)
        
        # Set bounds with margin
        margin = max(L, W) * 0.12
        ax.set_xlim(-margin, L + margin)
        ax.set_ylim(-margin, W + margin)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Export high-res PNG
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none', pad_inches=0.5)
        buf.seek(0)
        plt.close(fig)
        return buf
    
    def _draw_property_boundary(self, ax, L, W):
        """Draw property boundary with fence line"""
        # Main boundary
        ax.add_patch(Rectangle((0, 0), L, W, fill=False, 
                              edgecolor='#3E2723', linewidth=3, linestyle='-'))
        # Fence posts every 20ft
        for x in np.arange(0, L+1, 20):
            ax.plot([x, x], [0, 3], color='#5D4037', linewidth=2)
            ax.plot([x, x], [W-3, W], color='#5D4037', linewidth=2)
        for y in np.arange(0, W+1, 20):
            ax.plot([0, 3], [y, y], color='#5D4037', linewidth=2)
            ax.plot([L-3, L], [y, y], color='#5D4037', linewidth=2)
    
    def _draw_zones(self, ax, layout):
        """Draw zone backgrounds with labels"""
        for zid, pos in layout['zone_positions'].items():
            # Zone fill
            ax.add_patch(Rectangle((pos['x'], pos['y']), pos['width'], pos['height'],
                                  facecolor=self.ZONE_COLORS.get(zid, '#EEE'),
                                  edgecolor='#546E7A', linewidth=1.5, alpha=0.6,
                                  linestyle='--'))
            # Zone label
            cx = pos['x'] + pos['width']/2
            cy = pos['y'] + pos['height']/2
            ax.text(cx, cy, self.ZONE_NAMES.get(zid, zid),
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   color='#1B5E20', alpha=0.8,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            edgecolor='#81C784', alpha=0.9, linewidth=1))
    
    def _draw_roads_logical(self, ax, layout):
        """
        Draw LOGICAL road network based on house position
        Grid system: Main N-S spine + E-W cross road + spurs to features
        """
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        hx, hy, hw, hh = layout['house_bbox']
        hcx, hcy = hx + hw/2, hy + hh/2
        
        road_width_main = max(10, min(L, W) * 0.025)
        road_width_sec = max(8, min(L, W) * 0.018)
        road_color = '#D7CCC8'
        road_edge = '#A1887F'
        
        # 1. MAIN N-S SPINE (from south boundary to north boundary through house)
        spine_x = hcx
        # South approach
        ax.add_patch(Rectangle((spine_x - road_width_main/2, 0),
                              road_width_main, hy,
                              facecolor=road_color, edgecolor=road_edge, linewidth=1))
        # North continuation  
        ax.add_patch(Rectangle((spine_x - road_width_main/2, hy + hh),
                              road_width_main, W - hy - hh,
                              facecolor=road_color, edgecolor=road_edge, linewidth=1))
        
        # 2. E-W CROSS ROAD at house level
        cross_y = hcy
        ax.add_patch(Rectangle((0, cross_y - road_width_sec/2),
                              L, road_width_sec,
                              facecolor=road_color, edgecolor=road_edge, linewidth=1))
        
        # 3. Draw spurs to major features
        features = layout.get('features', {})
        for key, f in features.items():
            if key in ['compost', 'swales']:
                continue
            if isinstance(f, list):
                continue
            if 'x' not in f:
                continue
            
            # Get feature center
            if 'radius' in f:
                fx, fy = f['x'], f['y']
            else:
                fx = f['x'] + f.get('width', 0)/2
                fy = f['y'] + f.get('height', 0)/2
            
            # Draw L-shaped spur from nearest road
            self._draw_spur(ax, fx, fy, spine_x, cross_y, road_width_sec*0.7)
    
    def _draw_spur(self, ax, fx, fy, spine_x, cross_y, width):
        """Draw L-shaped spur road from feature to main road"""
        road_color = '#D7CCC8'
        road_edge = '#A1887F'
        
        # Determine closest road
        dist_to_spine = abs(fx - spine_x)
        dist_to_cross = abs(fy - cross_y)
        
        if dist_to_spine < dist_to_cross:
            # Connect to N-S spine
            # H segment from feature to spine
            y_start = fy - width/2
            x_start = min(fx, spine_x)
            x_end = max(fx, spine_x)
            ax.add_patch(Rectangle((x_start, y_start), 
                                  abs(spine_x - fx), width,
                                  facecolor=road_color, edgecolor=road_edge, linewidth=0.8))
        else:
            # Connect to E-W cross
            x_start = fx - width/2
            y_start = min(fy, cross_y)
            y_end = max(fy, cross_y)
            ax.add_patch(Rectangle((x_start, y_start),
                                  width, abs(cross_y - fy),
                                  facecolor=road_color, edgecolor=road_edge, linewidth=0.8))
    
    def _draw_water_features(self, ax, layout):
        """Draw wells, ponds, tanks"""
        features = layout.get('features', {})
        
        # Well
        if 'well' in features:
            f = features['well']
            r = f['radius']
            # Concrete ring
            ax.add_patch(Circle((f['x'], f['y']), r, 
                               facecolor='#90A4AE', edgecolor='#546E7A', linewidth=2))
            # Water
            ax.add_patch(Circle((f['x'], f['y']), r*0.7,
                               facecolor='#4FC3F7', edgecolor='none'))
            ax.text(f['x'], f['y'], 'W', ha='center', va='center',
                   fontsize=7, fontweight='bold', color='white')
        
        # Pond
        if 'pond' in features:
            f = features['pond']
            r = f['radius']
            # Natural shape (slightly irregular)
            theta = np.linspace(0, 2*np.pi, 40)
            r_var = r * (1 + 0.08*np.sin(4*theta))
            x_pts = f['x'] + r_var * np.cos(theta)
            y_pts = f['y'] + r_var * np.sin(theta)
            ax.add_patch(Polygon(list(zip(x_pts, y_pts)),
                                facecolor='#4FC3F7', edgecolor='#0288D1',
                                linewidth=2, alpha=0.8))
            # Water plants
            for angle in [0.3, 1.2, 2.5, 3.8, 5.1]:
                px = f['x'] + r*0.5*np.cos(angle)
                py = f['y'] + r*0.5*np.sin(angle)
                ax.add_patch(Circle((px, py), 2, facecolor='#4CAF50', edgecolor='none'))
            ax.text(f['x'], f['y'], 'POND', ha='center', va='center',
                   fontsize=7, fontweight='bold', color='#01579B')
        
        # Rain tank
        if 'rain_tank' in features:
            f = features['rain_tank']
            ax.add_patch(FancyBboxPatch((f['x'], f['y']), f['width'], f['height'],
                                       boxstyle='round,pad=0.02',
                                       facecolor='#B3E5FC', edgecolor='#0288D1',
                                       linewidth=2))
            # Water level lines
            for i in range(3):
                y_line = f['y'] + f['height']*(0.2 + i*0.25)
                ax.plot([f['x']+2, f['x']+f['width']-2], [y_line, y_line],
                       color='#0288D1', linewidth=0.8)
            ax.text(f['x']+f['width']/2, f['y']+f['height']/2, 'RAIN\nTANK',
                   ha='center', va='center', fontsize=6, fontweight='bold',
                   color='#01579B')
    
    def _draw_utilities(self, ax, layout):
        """Draw solar and greenhouse"""
        features = layout.get('features', {})
        
        # Solar
        if 'solar' in features:
            f = features['solar']
            # Frame
            ax.add_patch(Rectangle((f['x'], f['y']), f['width'], f['height'],
                                  facecolor='#607D8B', edgecolor='#37474F', linewidth=2))
            # Panels (grid)
            rows, cols = 2, 3
            gap = 1.5
            pw = (f['width'] - gap*(cols+1))/cols
            ph = (f['height'] - gap*(rows+1))/rows
            for row in range(rows):
                for col in range(cols):
                    px = f['x'] + gap + col*(pw+gap)
                    py = f['y'] + gap + row*(ph+gap)
                    ax.add_patch(Rectangle((px, py), pw, ph,
                                          facecolor='#1565C0', edgecolor='#0D47A1',
                                          linewidth=0.8))
            ax.text(f['x']+f['width']/2, f['y']+f['height']+8, 'SOLAR',
                   ha='center', fontsize=7, fontweight='bold', color='#0D47A1')
        
        # Greenhouse
        if 'greenhouse' in features:
            f = features['greenhouse']
            # Base
            ax.add_patch(Rectangle((f['x'], f['y']), f['width'], f['height'],
                                  facecolor='#E0F2F1', edgecolor='#00695C',
                                  linewidth=2, linestyle='--', alpha=0.7))
            # Arched roof
            arc = mpatches.Arc((f['x']+f['width']/2, f['y']+f['height']),
                              f['width'], f['height']*0.3,
                              angle=0, theta1=0, theta2=180,
                              color='#00695C', linewidth=2)
            ax.add_patch(arc)
            # Beds inside
            for by in [f['y']+8, f['y']+f['height']-15]:
                ax.add_patch(Rectangle((f['x']+4, by), f['width']-8, 8,
                                      facecolor='#5D4037', edgecolor='black', linewidth=0.8))
            ax.text(f['x']+f['width']/2, f['y']-10, 'GREENHOUSE',
                   ha='center', fontsize=7, fontweight='bold', color='#004D40')
    
    def _draw_livestock(self, ax, layout):
        """Draw all livestock structures"""
        features = layout.get('features', {})
        configs = {
            'goat_shed': ('#FFCCBC', '#5D4037', 'GOAT SHED'),
            'chicken_coop': ('#FFF9C4', '#F57F17', 'CHICKEN COOP'),
            'piggery': ('#FFCCBC', '#BF360C', 'PIGGERY'),
            'cow_shed': ('#D7CCC8', '#5D4037', 'COW SHED'),
            'fish_tanks': ('#B3E5FC', '#0288D1', 'FISH TANKS'),
            'bee_hives': ('#FFF176', '#F9A825', 'BEE HIVES'),
        }
        
        for key, (fc, ec, label) in configs.items():
            if key not in features:
                continue
            f = features[key]
            
            # Base shed
            ax.add_patch(Rectangle((f['x'], f['y']), f['width'], f['height'],
                                  facecolor=fc, edgecolor=ec, linewidth=2))
            # Roof
            roof_height = min(f['height']*0.25, 12)
            ax.add_patch(Polygon([
                (f['x']-3, f['y']+f['height']),
                (f['x']+f['width']/2, f['y']+f['height']+roof_height),
                (f['x']+f['width']+3, f['y']+f['height'])
            ], facecolor='#A1887F', edgecolor=ec, linewidth=1.5))
            
            # Specific details
            if key == 'fish_tanks':
                # 4 tanks
                tw = (f['width']-8)/2
                th = (f['height']-8)/2
                for tx, ty in [(f['x']+4, f['y']+4), (f['x']+4+tw+2, f['y']+4),
                              (f['x']+4, f['y']+4+th+2), (f['x']+4+tw+2, f['y']+4+th+2)]:
                    ax.add_patch(Rectangle((tx, ty), tw, th,
                                          facecolor='#4FC3F7', edgecolor='#0288D1'))
            
            elif key == 'bee_hives':
                # Row of hives
                n_hives = max(2, int(f['width']/15))
                hw = (f['width']-6)/n_hives - 2
                for i in range(n_hives):
                    hx = f['x'] + 3 + i*(hw+2)
                    ax.add_patch(FancyBboxPatch((hx, f['y']+3), hw, f['height']*0.4,
                                               boxstyle='round,pad=0.5',
                                               facecolor='#FFF176', edgecolor='#F57F17'))
            
            ax.text(f['x']+f['width']/2, f['y']+f['height']+roof_height+5, label,
                   ha='center', fontsize=6, fontweight='bold', color=ec)
    
    def _draw_kitchen_garden(self, ax, layout):
        """Draw raised beds in kitchen garden"""
        zones = layout.get('zone_positions', {})
        if 'z1' not in zones:
            return
        
        z1 = zones['z1']
        # Get house position to avoid overlap
        hx, hy, hw, hh = layout['house_bbox']
        
        # Calculate safe area (away from house)
        margin = 8
        safe_y_start = z1['y'] + margin
        safe_y_end = z1['y'] + z1['height'] - margin
        
        # Adjust if house overlaps
        if hy < z1['y'] + z1['height'] and hy + hh > z1['y']:
            if hy > z1['y']:
                safe_y_end = min(safe_y_end, hy - margin)
            else:
                safe_y_start = max(safe_y_start, hy + hh + margin)
        
        if safe_y_end - safe_y_start < 20:
            return
        
        # Create raised beds
        bed_w = min(14, z1['width']*0.15)
        bed_h = min(35, (safe_y_end - safe_y_start)*0.8)
        gap = 6
        n_beds = int((z1['width'] - 2*margin - gap) / (bed_w + gap))
        
        for i in range(n_beds):
            bx = z1['x'] + margin + i*(bed_w + gap)
            by = safe_y_start + (safe_y_end - safe_y_start - bed_h)/2
            
            if bx + bed_w > z1['x'] + z1['width'] - margin:
                break
            
            # Wooden frame
            ax.add_patch(FancyBboxPatch((bx, by), bed_w, bed_h,
                                       boxstyle='round,pad=0.3',
                                       facecolor='#8D6E63', edgecolor='#5D4037',
                                       linewidth=2))
            # Soil
            ax.add_patch(Rectangle((bx+2, by+2), bed_w-4, bed_h-4,
                                  facecolor='#3E2723', edgecolor='none'))
            # Plants (rows of dots)
            n_rows = 4
            for row in range(n_rows):
                py = by + 4 + row*(bed_h-8)/(n_rows-1)
                for col in range(3):
                    px = bx + 3 + col*(bed_w-6)/2
                    color = ['#4CAF50', '#66BB6A', '#81C784'][(row+col)%3]
                    ax.add_patch(Circle((px, py), 1.5, facecolor=color,
                                       edgecolor='#1B5E20', linewidth=0.5))
    
    def _draw_trees(self, ax, layout):
        """Draw all trees from placements"""
        for tree in layout.get('tree_placements', []):
            x, y = tree['x'], tree['y']
            species = tree.get('species', 'Mango')
            color = self.TREE_COLORS.get(species, '#2E7D32')
            
            # Canopy size based on species
            sizes = {'Coconut': 6, 'Banana': 5, 'Papaya': 4, 'Bamboo': 3,
                    'Moringa': 5, 'Guava': 6, 'Citrus': 6, 'Mango': 9,
                    'Jackfruit': 10, 'Avocado': 8, 'Neem': 10, 'Teak': 9}
            r = sizes.get(species, 7)
            
            # Shadow
            ax.add_patch(Circle((x+1, y-1), r, facecolor='black', alpha=0.15))
            # Canopy
            ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor='#1B5E20',
                              linewidth=1.5, alpha=0.85))
            # Highlight
            ax.add_patch(Circle((x-r*0.3, y+r*0.3), r*0.3, facecolor='white',
                              alpha=0.2, edgecolor='none'))
    
    def _draw_house(self, ax, layout):
        """Draw architectural house plan"""
        hx, hy, hw, hh = layout['house_bbox']
        
        # Shadow
        ax.add_patch(Rectangle((hx+3, hy-3), hw, hh,
                              facecolor='black', alpha=0.15))
        
        # Main building
        ax.add_patch(Rectangle((hx, hy), hw, hh,
                              facecolor='#EFEBE9', edgecolor='#5D4037',
                              linewidth=3))
        
        # Roof (hip roof style)
        roof_overhang = 3
        roof_height = min(hw, hh) * 0.15
        ax.add_patch(Polygon([
            (hx-roof_overhang, hy+hh),
            (hx+hw/2, hy+hh+roof_height),
            (hx+hw+roof_overhang, hy+hh),
            (hx+hw+roof_overhang, hy+hh-roof_overhang),
            (hx-roof_overhang, hy+hh-roof_overhang)
        ], facecolor='#D7CCC8', edgecolor='#8D6E63', linewidth=2))
        
        # Ridge line
        ax.plot([hx+hw/2, hx+hw/2], [hy+hh, hy+hh+roof_height],
               color='#5D4037', linewidth=2, linestyle='-.')
        
        # Rooms (interior walls)
        # Vertical divider
        ax.plot([hx+hw*0.4, hx+hw*0.4], [hy, hy+hh],
               color='#8D6E63', linewidth=2)
        # Horizontal divider
        ax.plot([hx, hx+hw], [hy+hh*0.55, hy+hh*0.55],
               color='#8D6E63', linewidth=2)
        
        # Door (front)
        door_w = hw * 0.12
        door_x = hx + (hw-door_w)/2
        ax.add_patch(Rectangle((door_x, hy), door_w, 3,
                              facecolor='#4E342E', edgecolor='black'))
        # Door swing arc
        arc = mpatches.Arc((door_x, hy+3), door_w*2, door_w*2,
                          angle=0, theta1=0, theta2=90,
                          color='#4E342E', linewidth=1)
        ax.add_patch(arc)
        
        # Windows
        win_w = hw * 0.15
        win_h = 3
        # Left window
        ax.add_patch(Rectangle((hx+hw*0.1, hy+hh*0.65), win_w, win_h,
                              facecolor='#B3E5FC', edgecolor='#1565C0', linewidth=2))
        # Right window
        ax.add_patch(Rectangle((hx+hw*0.75, hy+hh*0.65), win_w, win_h,
                              facecolor='#B3E5FC', edgecolor='#1565C0', linewidth=2))
        
        # Label
        ax.text(hx+hw/2, hy+hh+roof_height+10, 'RESIDENCE',
               ha='center', fontsize=10, fontweight='bold', color='#3E2723',
               path_effects=[pe.withStroke(linewidth=3, foreground='white')])
    
    def _draw_cartographic_elements(self, ax, L, W, layout):
        """Add north arrow, scale bar, legend, title"""
        margin = max(L, W) * 0.05
        
        # North arrow
        nx, ny = L - margin, W - margin
        arrow_size = min(L, W) * 0.04
        ax.add_patch(Circle((nx, ny), arrow_size, facecolor='white',
                           edgecolor='#1A237E', linewidth=2, zorder=10))
        ax.annotate('', xy=(nx, ny+arrow_size*0.7), xytext=(nx, ny-arrow_size*0.3),
                   arrowprops=dict(arrowstyle='->', color='red', lw=3))
        ax.text(nx, ny+arrow_size+5, 'N', ha='center', fontsize=12,
               fontweight='bold', color='red')
        
        # Scale bar
        sx, sy = margin, margin
        scale_len = int(min(L, W) * 0.15 / 10) * 10  # Round to 10ft
        ax.add_patch(Rectangle((sx, sy), scale_len/2, 4, facecolor='black'))
        ax.add_patch(Rectangle((sx+scale_len/2, sy), scale_len/2, 4,
                              facecolor='white', edgecolor='black'))
        ax.text(sx+scale_len/2, sy-8, f'{scale_len} ft',
               ha='center', fontsize=8, fontweight='bold')
        
        # Title block
        acres = layout['acres']
        title_text = f"{acres:.2f} ACRE HOMESTEAD - {layout['location']}\n" \
                    f"{int(layout['total_sqft']):,} SQ.FT. | {layout['house_position']} FACING | " \
                    f"{layout['tree_count']} TREES"
        ax.text(L/2, W + margin*0.8, title_text,
               ha='center', va='bottom', fontsize=14, fontweight='bold',
               color='#1B5E20',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9',
                        edgecolor='#2E7D32', linewidth=2))
        
        # Legend
        lx, ly = L + margin*0.3, W*0.7
        legend_items = [
            ('#EFEBE9', 'Residence'),
            ('#C8E6C9', 'Kitchen Garden'),
            ('#A5D6A7', 'Food Forest'),
            ('#D7CCC8', 'Roads/Paths'),
            ('#4FC3F7', 'Water Features'),
            ('#1565C0', 'Solar Array'),
        ]
        
        # Legend box
        box_h = len(legend_items)*12 + 15
        ax.add_patch(FancyBboxPatch((lx, ly-box_h), 100, box_h,
                                   boxstyle='round,pad=3',
                                   facecolor='white', edgecolor='#546E7A',
                                   linewidth=1.5, alpha=0.95))
        ax.text(lx+50, ly-8, 'LEGEND', ha='center', fontsize=9,
               fontweight='bold', color='#1A237E')
        
        for i, (color, label) in enumerate(legend_items):
            y_pos = ly - 20 - i*12
            ax.add_patch(Rectangle((lx+5, y_pos-3), 10, 8, facecolor=color,
                                  edgecolor='#546E7A', linewidth=0.8))
            ax.text(lx+20, y_pos, label, fontsize=7, va='center')
'''

print("✅ File 4: visualizer_2d_v7.py created")
print(f"   Length: {len(files_content['visualizer_2d_v7.py'])} characters")
