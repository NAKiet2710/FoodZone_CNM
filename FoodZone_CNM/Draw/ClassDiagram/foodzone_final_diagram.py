import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, PathPatch
from matplotlib.lines import Line2D
from matplotlib.path import Path

class FoodZoneClassDiagram:
    def __init__(self):
        # Initialize figure with appropriate size
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        
        # Colors for different class groups
        self.colors = {
            'user': '#e3f2fd',      # Light blue for user models
            'food': '#c8e6c9',      # Light green for food models
            'order': '#fff9c4',     # Light yellow for order models
            'delivery': '#ffccbc',  # Light orange for delivery models
        }
        
        # Store box positions and dimensions
        self.positions = {}
        
        # Box size (very small to avoid touching)
        self.box_width = 1.0
        
    def draw_class_box(self, name, attributes, x, y, color):
        """Draw a class box with name and attributes"""
        # Calculate dimensions
        attr_height = 0.16 * len(attributes) if attributes else 0
        header_height = 0.22
        total_height = header_height + attr_height
        
        # Store position and dimensions
        self.positions[name] = {
            'x': x,
            'y': y,
            'width': self.box_width,
            'height': total_height,
            'center_x': x,
            'center_y': y + total_height/2
        }
        
        # Draw main box
        box = FancyBboxPatch(
            (x - self.box_width/2, y),
            self.box_width, total_height,
            boxstyle="round,pad=0.05",
            facecolor=color, alpha=0.9, 
            edgecolor='black', linewidth=0.5
        )
        self.ax.add_patch(box)
        
        # Draw class name
        self.ax.text(x, y + total_height - header_height/2, name, 
                    ha='center', va='center', fontsize=6, fontweight='bold')
        
        # Draw separator line
        if attributes:
            self.ax.plot(
                [x - self.box_width/2, x + self.box_width/2],
                [y + total_height - header_height, y + total_height - header_height],
                color='black', linestyle='-', linewidth=0.5
            )
        
        # Draw attributes
        for i, attr in enumerate(attributes):
            y_pos = y + total_height - header_height - (i + 0.5) * 0.16
            self.ax.text(
                x - self.box_width/2 + 0.08, y_pos, attr,
                ha='left', va='center', fontsize=5
            )
        
        return total_height
    
    def draw_relationship(self, from_class, to_class, rel_type, label, arrow_direction='to'):
        """Draw relationship between classes with label exactly in the middle of the arrow
        rel_type: 'association' or 'composition'
        label: '1:1', '1:n', etc.
        arrow_direction: 'to', 'from', or 'both'
        """
        # Get box positions
        from_pos = self.positions[from_class]
        to_pos = self.positions[to_class]
        
        # Determine appropriate edge points to avoid touching boxes
        from_edge = self._get_edge_point(from_class, to_class)
        to_edge = self._get_edge_point(to_class, from_class)
        
        # Draw the line with increased thickness
        self.ax.plot([from_edge[0], to_edge[0]], [from_edge[1], to_edge[1]], 
                     color='black', linestyle='-', linewidth=0.7)
        
        # Parse the relationship label to determine cardinality
        cardinalities = label.split(':')
        from_cardinality = cardinalities[0]
        to_cardinality = cardinalities[1]
        
        # Add arrowhead based on relationship type, direction, and cardinality
        if arrow_direction == 'to' or arrow_direction == 'both':
            # Arrow points to target
            if rel_type == 'association':
                if to_cardinality == '1':
                    self._draw_one_arrow(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
                else:  # 'n' or other cardinalities
                    self._draw_many_arrow(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
            elif rel_type == 'composition':
                self._draw_diamond(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
                
        if arrow_direction == 'from' or arrow_direction == 'both':
            # Arrow points from source
            if from_cardinality == '1':
                self._draw_one_arrow(from_edge[0], from_edge[1], to_edge[0], to_edge[1])
            else:  # 'n' or other cardinalities
                self._draw_many_arrow(from_edge[0], from_edge[1], to_edge[0], to_edge[1])
        
        # Add label in the middle with white background
        mid_x = (from_edge[0] + to_edge[0]) / 2
        mid_y = (from_edge[1] + to_edge[1]) / 2
        
        # Add background for label to prevent overlapping with the line
        self.ax.text(mid_x, mid_y, label, 
                     ha='center', va='center', fontsize=6,
                     bbox=dict(facecolor='white', alpha=1.0, edgecolor='none', 
                               boxstyle='round,pad=0.1'))
    
    def _get_edge_point(self, class_name, target_class_name):
        """Calculate the edge point of a box toward another box with extra margin"""
        box = self.positions[class_name]
        target = self.positions[target_class_name]
        
        # Calculate direction vector
        dx = target['center_x'] - box['center_x']
        dy = target['center_y'] - box['center_y']
        
        # Normalize direction vector
        length = np.sqrt(dx**2 + dy**2)
        dx /= length
        dy /= length
        
        # Calculate intersection point with box boundary
        half_width = box['width'] / 2
        half_height = box['height'] / 2
        
        # Determine which edge to use (horizontal or vertical)
        if abs(dx * half_height) < abs(dy * half_width):
            # Intersection with top or bottom edge
            y_edge = half_height if dy > 0 else -half_height
            x_edge = y_edge * dx / dy
            x_edge = max(min(x_edge, half_width), -half_width)
        else:
            # Intersection with left or right edge
            x_edge = half_width if dx > 0 else -half_width
            y_edge = x_edge * dy / dx
            y_edge = max(min(y_edge, half_height), -half_height)
        
        # Add a small margin to avoid touching the box (0.05 units)
        margin = 0.05
        x_edge += margin * dx
        y_edge += margin * dy
        
        return (box['center_x'] + x_edge, box['center_y'] + y_edge)
    
    def _draw_one_arrow(self, x, y, from_x, from_y):
        """Draw a single arrow (for '1' cardinality)"""
        dx = from_x - x
        dy = from_y - y
        angle = np.arctan2(dy, dx)
        
        # Standard arrow for '1' cardinality - make it clearer
        head_length = 0.12
        arrow = FancyArrowPatch((x, y), 
                               (x + head_length * np.cos(angle), 
                                y + head_length * np.sin(angle)),
                               arrowstyle='->', 
                               connectionstyle="arc3,rad=0", 
                               linewidth=0.9, 
                               color='black',
                               shrinkA=0, shrinkB=0, 
                               mutation_scale=12)
        self.ax.add_patch(arrow)
    
    def _draw_many_arrow(self, x, y, from_x, from_y):
        """Draw a standard UML 'many' arrow (crow's foot)"""
        dx = from_x - x
        dy = from_y - y
        angle = np.arctan2(dy, dx)
        
        # Define crow's foot dimensions
        base_length = 0.15  # Length of the straight line before the fork
        prong_length = 0.15  # Length of each prong
        spread_angle = 30   # Angle of spread in degrees
        
        # Calculate the base point where fork starts
        base_x = x + base_length * np.cos(angle)
        base_y = y + base_length * np.sin(angle)
        
        # Draw the straight line to the base point (shaft)
        self.ax.plot([x, base_x], [base_y, base_y], color='black', linewidth=0.9)
        
        # Calculate the angle of each prong
        left_angle = angle - np.radians(spread_angle)
        right_angle = angle + np.radians(spread_angle)
        
        # Calculate end points of prongs
        left_x = base_x + prong_length * np.cos(left_angle)
        left_y = base_y + prong_length * np.sin(left_angle)
        
        center_x = base_x + prong_length * np.cos(angle)
        center_y = base_y + prong_length * np.sin(angle)
        
        right_x = base_x + prong_length * np.cos(right_angle)
        right_y = base_y + prong_length * np.sin(right_angle)
        
        # Draw the three prongs
        self.ax.plot([base_x, left_x], [base_y, left_y], color='black', linewidth=0.7)
        self.ax.plot([base_x, center_x], [base_y, center_y], color='black', linewidth=0.7)
        self.ax.plot([base_x, right_x], [base_y, right_y], color='black', linewidth=0.7)
    
    def _draw_diamond(self, x, y, from_x, from_y):
        """Draw a diamond arrowhead (for composition)"""
        dx = from_x - x
        dy = from_y - y
        angle = np.arctan2(dy, dx)
        
        # Create diamond shape with larger size
        h = 0.08
        w = 0.05
        point1 = (x, y)
        point2 = (x + h * np.cos(angle) + w * np.cos(angle + np.pi/2),
                 y + h * np.sin(angle) + w * np.sin(angle + np.pi/2))
        point3 = (x + 2 * h * np.cos(angle),
                 y + 2 * h * np.sin(angle))
        point4 = (x + h * np.cos(angle) + w * np.cos(angle - np.pi/2),
                 y + h * np.sin(angle) + w * np.sin(angle - np.pi/2))
        
        # Draw filled diamond
        diamond = plt.Polygon([point1, point2, point3, point4], 
                             closed=True, fill=True, facecolor='black', edgecolor='black')
        self.ax.add_patch(diamond)
    
    def add_legend(self):
        """Add a legend explaining the notation used in the diagram"""
        # Create improved legend with better position
        legend_x = 2.5
        legend_y = 0.5
        legend_width = 3.5
        legend_height = 2
        
        # Background rectangle for the legend
        legend_bg = Rectangle((legend_x, legend_y), legend_width, legend_height, 
                             facecolor='white', alpha=0.95, edgecolor='black', linewidth=0.8)
        self.ax.add_patch(legend_bg)
        
        # Legend title
        self.ax.text(legend_x + legend_width/2, legend_y + legend_height - 0.2, 'Relationship Legend', 
                     ha='center', va='center', fontsize=8, fontweight='bold')
        
        spacing = 0.4  # Vertical spacing between legend items
        
        # 1. One-to-One relationship
        y_pos = legend_y + legend_height - 0.6
        line_length = 0.8
        self.ax.plot([legend_x + 0.3, legend_x + 0.3 + line_length], [y_pos, y_pos], 
                     color='black', linewidth=0.8)
        self._draw_one_arrow(legend_x + 0.3, y_pos, legend_x + 0.3 + line_length, y_pos)
        self._draw_one_arrow(legend_x + 0.3 + line_length, y_pos, legend_x + 0.3, y_pos)
        self.ax.text(legend_x + 1.5, y_pos, 'One-to-One Relationship (1:1)', 
                     fontsize=7, va='center')
        
        # 2. One-to-Many relationship
        y_pos -= spacing
        self.ax.plot([legend_x + 0.3, legend_x + 0.3 + line_length], [y_pos, y_pos], 
                     color='black', linewidth=0.8)
        self._draw_one_arrow(legend_x + 0.3, y_pos, legend_x + 0.3 + line_length, y_pos)
        self._draw_many_arrow(legend_x + 0.3 + line_length, y_pos, legend_x + 0.3, y_pos)
        self.ax.text(legend_x + 1.5, y_pos, 'One-to-Many Relationship (1:n)', 
                     fontsize=7, va='center')
        
        # 3. Composition relationship
        y_pos -= spacing
        self.ax.plot([legend_x + 0.3, legend_x + 0.3 + line_length], [y_pos, y_pos], 
                     color='black', linewidth=0.8)
        self._draw_diamond(legend_x + 0.3, y_pos, legend_x + 0.3 + line_length, y_pos)
        self.ax.text(legend_x + 1.5, y_pos, 'Composition Relationship', 
                     fontsize=7, va='center')
        
        # 4. Association relationship
        y_pos -= spacing
        self.ax.plot([legend_x + 0.3, legend_x + 0.3 + line_length], [y_pos, y_pos], 
                     color='black', linewidth=0.8)
        self._draw_one_arrow(legend_x + 0.3 + line_length, y_pos, legend_x + 0.3, y_pos)
        self.ax.text(legend_x + 1.5, y_pos, 'Association Relationship', 
                     fontsize=7, va='center')
            
    def draw_diagram(self):
        """Draw the complete FoodZone class diagram"""
        # Define grid positions with extra space to ensure boxes don't touch
        # Column positions with wider spacing
        col1_x = 2
        col2_x = 6
        col3_x = 10
        
        # Row positions with wider vertical spacing
        row1_y = 8
        row2_y = 5
        row3_y = 2
        
        # Move Category and Dish to different positions to avoid connection lines
        category_x = 4
        category_y = 3.5
        
        # Position Dish to avoid other relationship lines - moved slightly
        dish_x = 7.5
        dish_y = 3.0
        
        # === USER COLUMN ===
        # User class
        user_attrs = [
            '+ id: int <<PK>>',
            '+ username: String',
            '+ email: String'
        ]
        self.draw_class_box('User', user_attrs, col1_x, row1_y, self.colors['user'])
        
        # Profile class
        profile_attrs = [
            '+ id: int <<PK>>', 
            '+ user_id: int <<FK>>',
            '+ contact_number: String',
            '+ address: String'
        ]
        self.draw_class_box('Profile', profile_attrs, col1_x, row2_y, self.colors['user'])
        
        # Shipper class
        shipper_attrs = [
            '+ id: int <<PK>>',
            '+ user_id: int <<FK>>',
            '+ vehicle_type: String',
            '+ availability: Boolean',
            '+ rating: Float'
        ]
        self.draw_class_box('Shipper', shipper_attrs, col1_x, row3_y, self.colors['user'])
        
        # === RESTAURANT COLUMN ===
        # Restaurant class
        restaurant_attrs = [
            '+ id: int <<PK>>',
            '+ owner_id: int <<FK>>',
            '+ name: String',
            '+ address: String',
            '+ is_active: Boolean'
        ]
        self.draw_class_box('Restaurant', restaurant_attrs, col2_x, row1_y, self.colors['food'])
        
        # Category class - moved to a different position
        category_attrs = [
            '+ id: int <<PK>>',
            '+ name: String',
            '+ description: String'
        ]
        self.draw_class_box('Category', category_attrs, category_x, category_y, self.colors['food'])
        
        # Dish class - moved to a different position
        dish_attrs = [
            '+ id: int <<PK>>',
            '+ name: String',
            '+ category_id: int <<FK>>',
            '+ restaurant_id: int <<FK>>',
            '+ price: Float',
            '+ is_available: Boolean'
        ]
        self.draw_class_box('Dish', dish_attrs, dish_x, dish_y, self.colors['food'])
        
        # === ORDER COLUMN ===
        # Order class
        order_attrs = [
            '+ id: int <<PK>>',
            '+ customer_id: int <<FK>>',
            '+ dish_id: int <<FK>>',
            '+ status: String',
            '+ ordered_on: DateTime'
        ]
        self.draw_class_box('Order', order_attrs, col3_x, row1_y, self.colors['order'])
        
        # DeliveryAddress class
        address_attrs = [
            '+ id: int <<PK>>',
            '+ customer_id: int <<FK>>',
            '+ address_line1: String',
            '+ city: String',
            '+ postal_code: String'
        ]
        self.draw_class_box('DeliveryAddress', address_attrs, col3_x, row2_y, self.colors['delivery'])
        
        # Delivery class
        delivery_attrs = [
            '+ id: int <<PK>>',
            '+ order_id: int <<FK>>',
            '+ shipper_id: int <<FK>>',
            '+ address_id: int <<FK>>',
            '+ status: String'
        ]
        self.draw_class_box('Delivery', delivery_attrs, col3_x, row3_y, self.colors['delivery'])
        
        # === RELATIONSHIPS ===
        # User relationships
        self.draw_relationship('User', 'Profile', 'association', '1:1', 'both')
        self.draw_relationship('User', 'Shipper', 'association', '1:1', 'both')
        self.draw_relationship('User', 'Restaurant', 'association', '1:1', 'both')
        
        # Restaurant and category relationships
        self.draw_relationship('Category', 'Dish', 'composition', '1:n', 'both')
        self.draw_relationship('Restaurant', 'Dish', 'composition', '1:n', 'both')
        
        # Order relationships
        self.draw_relationship('Profile', 'Order', 'composition', '1:n', 'both')
        self.draw_relationship('Profile', 'DeliveryAddress', 'composition', '1:n', 'both')
        self.draw_relationship('Dish', 'Order', 'association', '1:n', 'both')
        
        # Delivery relationships
        self.draw_relationship('Order', 'Delivery', 'association', '1:1', 'both')
        self.draw_relationship('DeliveryAddress', 'Delivery', 'association', '1:n', 'both')
        self.draw_relationship('Shipper', 'Delivery', 'association', '1:n', 'both')
        
        # Add legend explaining the notation
        self.add_legend()
        
        # Add title
        self.ax.text(6, 10.5, 'FoodZone Class Diagram', ha='center', fontsize=12, fontweight='bold')
        
        # Set plot limits with extra space
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(0, 11)
        self.ax.set_axis_off()
        
        plt.tight_layout()
        plt.savefig('foodzone_final_diagram.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    diagram = FoodZoneClassDiagram()
    diagram.draw_diagram() 