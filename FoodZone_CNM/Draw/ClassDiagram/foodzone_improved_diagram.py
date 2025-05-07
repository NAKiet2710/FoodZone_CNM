import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

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
        
        # Box size (reduced for smaller boxes)
        self.box_width = 1.2
        
    def draw_class_box(self, name, attributes, x, y, color):
        """Draw a class box with name and attributes"""
        # Calculate dimensions
        attr_height = 0.18 * len(attributes) if attributes else 0
        header_height = 0.25
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
            boxstyle="round,pad=0.1",
            facecolor=color, alpha=0.9, 
            edgecolor='black', linewidth=0.6
        )
        self.ax.add_patch(box)
        
        # Draw class name
        self.ax.text(x, y + total_height - header_height/2, name, 
                    ha='center', va='center', fontsize=7, fontweight='bold')
        
        # Draw separator line
        if attributes:
            self.ax.plot(
                [x - self.box_width/2, x + self.box_width/2],
                [y + total_height - header_height, y + total_height - header_height],
                color='black', linestyle='-', linewidth=0.6
            )
        
        # Draw attributes
        for i, attr in enumerate(attributes):
            y_pos = y + total_height - header_height - (i + 0.5) * 0.18
            self.ax.text(
                x - self.box_width/2 + 0.1, y_pos, attr,
                ha='left', va='center', fontsize=6
            )
        
        return total_height
    
    def draw_relationship(self, from_class, to_class, rel_type, label):
        """Draw relationship between classes with label in the middle of the arrow"""
        # Get box positions
        from_pos = self.positions[from_class]
        to_pos = self.positions[to_class]
        
        # Calculate connection points based on relative positions
        x1, y1 = from_pos['center_x'], from_pos['center_y']
        x2, y2 = to_pos['center_x'], to_pos['center_y']
        
        # Determine appropriate edge points to avoid touching boxes
        from_edge = self._get_edge_point(from_class, to_class)
        to_edge = self._get_edge_point(to_class, from_class)
        
        # Draw the line
        self.ax.plot([from_edge[0], to_edge[0]], [from_edge[1], to_edge[1]], 
                     color='black', linestyle='-', linewidth=0.6)
        
        # Add arrowhead based on relationship type
        if rel_type == 'association':
            self._draw_arrow(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
        elif rel_type == 'composition':
            self._draw_diamond(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
        
        # Add label in the middle with white background
        mid_x = (from_edge[0] + to_edge[0]) / 2
        mid_y = (from_edge[1] + to_edge[1]) / 2
        
        # Add background for label to prevent overlapping with the line
        self.ax.text(mid_x, mid_y, label, 
                     ha='center', va='center', fontsize=6,
                     bbox=dict(facecolor='white', alpha=1.0, edgecolor='none', 
                               boxstyle='round,pad=0.2'))
    
    def _get_edge_point(self, class_name, target_class_name):
        """Calculate the edge point of a box toward another box"""
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
        
        return (box['center_x'] + x_edge, box['center_y'] + y_edge)
    
    def _draw_arrow(self, x, y, from_x, from_y):
        """Draw a simple arrow"""
        dx = from_x - x
        dy = from_y - y
        angle = np.arctan2(dy, dx)
        
        head_length = 0.07
        arrow = FancyArrowPatch((x, y), 
                               (x + head_length * np.cos(angle), 
                                y + head_length * np.sin(angle)),
                               arrowstyle='->', 
                               connectionstyle="arc3,rad=0", 
                               linewidth=0.6, 
                               color='black',
                               shrinkA=0, shrinkB=0, 
                               mutation_scale=8)
        self.ax.add_patch(arrow)
    
    def _draw_diamond(self, x, y, from_x, from_y):
        """Draw a diamond arrowhead (for composition)"""
        dx = from_x - x
        dy = from_y - y
        angle = np.arctan2(dy, dx)
        
        # Create diamond shape
        h = 0.06
        w = 0.03
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
    
    def draw_diagram(self):
        """Draw the complete FoodZone class diagram"""
        # Define grid positions with more space between boxes
        # Column positions
        col1_x = 2
        col2_x = 6
        col3_x = 10
        
        # Row positions with more vertical spacing
        row1_y = 8
        row2_y = 5
        row3_y = 2
        
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
        
        # Category class
        category_attrs = [
            '+ id: int <<PK>>',
            '+ name: String',
            '+ description: String'
        ]
        self.draw_class_box('Category', category_attrs, col2_x, row2_y, self.colors['food'])
        
        # Dish class
        dish_attrs = [
            '+ id: int <<PK>>',
            '+ name: String',
            '+ category_id: int <<FK>>',
            '+ restaurant_id: int <<FK>>',
            '+ price: Float',
            '+ is_available: Boolean'
        ]
        self.draw_class_box('Dish', dish_attrs, col2_x, row3_y, self.colors['food'])
        
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
        self.draw_relationship('User', 'Profile', 'association', '1:1')
        self.draw_relationship('User', 'Shipper', 'association', '1:1')
        self.draw_relationship('User', 'Restaurant', 'association', '1:1')
        
        # Restaurant and category relationships
        self.draw_relationship('Category', 'Dish', 'composition', '1:n')
        self.draw_relationship('Restaurant', 'Dish', 'composition', '1:n')
        
        # Order relationships
        self.draw_relationship('Profile', 'Order', 'composition', '1:n')
        self.draw_relationship('Profile', 'DeliveryAddress', 'composition', '1:n')
        self.draw_relationship('Dish', 'Order', 'association', '1:n')
        
        # Delivery relationships
        self.draw_relationship('Order', 'Delivery', 'association', '1:1')
        self.draw_relationship('DeliveryAddress', 'Delivery', 'association', '1:n')
        self.draw_relationship('Shipper', 'Delivery', 'association', '1:n')
        
        # Add title
        self.ax.text(6, 10.5, 'FoodZone Class Diagram', ha='center', fontsize=12, fontweight='bold')
        
        # Set plot limits with extra space
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(0, 11)
        self.ax.set_axis_off()
        
        plt.tight_layout()
        plt.savefig('foodzone_improved_diagram.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    diagram = FoodZoneClassDiagram()
    diagram.draw_diagram() 