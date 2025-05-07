import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle, PathPatch, ConnectionPatch
from matplotlib.path import Path

class FoodZoneDatabaseDiagram:
    def __init__(self):
        # Initialize figure with appropriate size
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        
        # Colors for different tables
        self.colors = {
            'user': '#e6f2ff',      # Light blue for user-related tables
            'food': '#e6ffe6',      # Light green for food-related tables
            'order': '#fff7e6',     # Light yellow for order-related tables
            'delivery': '#ffe6e6',  # Light red for delivery-related tables
        }
        
        # Store table positions and dimensions
        self.positions = {}
        
        # Table size (small to avoid touching)
        self.table_width = 1.4
        
    def draw_table(self, name, columns, x, y, color):
        """Draw a database table with name and columns"""
        # Calculate dimensions
        columns_height = 0.25 * len(columns) if columns else 0
        header_height = 0.3
        total_height = header_height + columns_height
        
        # Store position and dimensions
        self.positions[name] = {
            'x': x,
            'y': y,
            'width': self.table_width,
            'height': total_height,
            'center_x': x,
            'center_y': y + total_height/2
        }
        
        # Draw main table box
        box = FancyBboxPatch(
            (x - self.table_width/2, y),
            self.table_width, total_height,
            boxstyle="round,pad=0.02",
            facecolor=color, alpha=0.9, 
            edgecolor='black', linewidth=0.7
        )
        self.ax.add_patch(box)
        
        # Draw table name header
        self.ax.text(x, y + total_height - header_height/2, name, 
                    ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Draw header separator line
        self.ax.plot(
            [x - self.table_width/2, x + self.table_width/2],
            [y + total_height - header_height, y + total_height - header_height],
            color='black', linestyle='-', linewidth=0.7
        )
        
        # Draw column attributes with symbols for primary/foreign keys
        for i, column in enumerate(columns):
            y_pos = y + total_height - header_height - (i + 0.5) * 0.25
            
            # Format with appropriate symbols
            if "[PK]" in column:
                col_text = column.replace("[PK]", "").strip()
                col_format = f"🔑 {col_text}"
            elif "[FK]" in column:
                col_text = column.replace("[FK]", "").strip()
                col_format = f"🔗 {col_text}"
            else:
                col_format = column
                
            self.ax.text(
                x - self.table_width/2 + 0.1, y_pos, col_format,
                ha='left', va='center', fontsize=7
            )
            
            # Add line separator between columns (except after the last one)
            if i < len(columns) - 1:
                self.ax.plot(
                    [x - self.table_width/2, x + self.table_width/2],
                    [y + total_height - header_height - (i + 1) * 0.25, y + total_height - header_height - (i + 1) * 0.25],
                    color='black', linestyle=':', linewidth=0.3
                )
            
        return total_height

    def _get_edge_point(self, table_name, target_table_name):
        """Calculate the edge point of a box toward another box with extra margin"""
        box = self.positions[table_name]
        target = self.positions[target_table_name]
        
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
        
        # Add a small margin to avoid touching the box
        margin = 0.05
        x_edge += margin * dx
        y_edge += margin * dy
        
        return (box['center_x'] + x_edge, box['center_y'] + y_edge)
    
    def draw_relationship(self, from_table, to_table, rel_type="1:n", color='black'):
        """Draw a relationship line between two tables
        rel_type: '1:1', '1:n', 'n:m'
        """
        # Get edge points
        from_edge = self._get_edge_point(from_table, to_table)
        to_edge = self._get_edge_point(to_table, from_table)
        
        # Draw the connecting line
        self.ax.plot([from_edge[0], to_edge[0]], [from_edge[1], to_edge[1]], 
                     color=color, linestyle='-', linewidth=0.7)
        
        # Add relationship annotation
        mid_x = (from_edge[0] + to_edge[0]) / 2
        mid_y = (from_edge[1] + to_edge[1]) / 2
        
        # Add markers based on relationship type
        if rel_type == "1:1":
            # Draw single line markers at both ends
            self._draw_one_marker(from_edge[0], from_edge[1], to_edge[0], to_edge[1])
            self._draw_one_marker(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
            
        elif rel_type == "1:n":
            # 1 marker at from_edge, crow's foot at to_edge
            self._draw_one_marker(from_edge[0], from_edge[1], to_edge[0], to_edge[1])
            self._draw_many_marker(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
            
        elif rel_type == "n:1":
            # Crow's foot at from_edge, 1 marker at to_edge
            self._draw_many_marker(from_edge[0], from_edge[1], to_edge[0], to_edge[1])
            self._draw_one_marker(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
            
        elif rel_type == "n:m":
            # Crow's foot at both ends
            self._draw_many_marker(from_edge[0], from_edge[1], to_edge[0], to_edge[1])
            self._draw_many_marker(to_edge[0], to_edge[1], from_edge[0], from_edge[1])
        
        # Add relationship type as text
        self.ax.text(mid_x, mid_y, rel_type, 
                     ha='center', va='center', fontsize=7, fontweight='bold',
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', 
                               boxstyle='round,pad=0.1'))
    
    def _draw_one_marker(self, x, y, to_x, to_y):
        """Draw '1' marker (single perpendicular line)"""
        dx = to_x - x
        dy = to_y - y
        
        # Calculate perpendicular direction
        length = np.sqrt(dx**2 + dy**2)
        dx, dy = dx/length, dy/length
        
        # Perpendicular vector
        perp_x, perp_y = -dy, dx
        
        # Scale for the marker size
        marker_size = 0.08
        
        # Draw the perpendicular line
        x1 = x - perp_x * marker_size
        y1 = y - perp_y * marker_size
        x2 = x + perp_x * marker_size
        y2 = y + perp_y * marker_size
        
        self.ax.plot([x1, x2], [y1, y2], color='black', linewidth=0.9)
    
    def _draw_many_marker(self, x, y, to_x, to_y):
        """Draw 'many' marker (crow's foot)"""
        dx = to_x - x
        dy = to_y - y
        
        # Calculate angle
        angle = np.arctan2(dy, dx)
        
        # Define crow's foot dimensions
        foot_length = 0.12
        spread_angle = 25  # degrees
        
        # Calculate the three points of the crow's foot
        left_angle = angle - np.radians(spread_angle)
        right_angle = angle + np.radians(spread_angle)
        
        # Endpoints of the three prongs
        left_x = x + foot_length * np.cos(left_angle)
        left_y = y + foot_length * np.sin(left_angle)
        
        center_x = x + foot_length * np.cos(angle)
        center_y = y + foot_length * np.sin(angle)
        
        right_x = x + foot_length * np.cos(right_angle)
        right_y = y + foot_length * np.sin(right_angle)
        
        # Draw the three lines
        self.ax.plot([x, left_x], [y, left_y], color='black', linewidth=0.7)
        self.ax.plot([x, center_x], [y, center_y], color='black', linewidth=0.7)
        self.ax.plot([x, right_x], [y, right_y], color='black', linewidth=0.7)
    
    def add_legend(self):
        """Add a legend explaining the diagram notation"""
        # Position the legend
        legend_x = 0.5
        legend_y = 0.5
        legend_width = 3.5
        legend_height = 2.0
        
        # Create legend background
        legend_bg = Rectangle((legend_x, legend_y), legend_width, legend_height,
                            facecolor='white', edgecolor='black', alpha=0.9, linewidth=0.8)
        self.ax.add_patch(legend_bg)
        
        # Add legend title
        self.ax.text(legend_x + legend_width/2, legend_y + legend_height - 0.2,
                    'Database Relationship Legend', fontsize=9, ha='center', fontweight='bold')
        
        # Space between legend items
        spacing = 0.4
        
        # 1:1 relationship
        y_pos = legend_y + legend_height - 0.6
        self.ax.plot([legend_x + 0.4, legend_x + 1.2], [y_pos, y_pos], color='black', linewidth=0.7)
        self._draw_one_marker(legend_x + 0.4, y_pos, legend_x + 1.2, y_pos)
        self._draw_one_marker(legend_x + 1.2, y_pos, legend_x + 0.4, y_pos)
        self.ax.text(legend_x + 1.5, y_pos, "One-to-One (1:1)", fontsize=8, va='center')
        
        # 1:n relationship
        y_pos -= spacing
        self.ax.plot([legend_x + 0.4, legend_x + 1.2], [y_pos, y_pos], color='black', linewidth=0.7)
        self._draw_one_marker(legend_x + 0.4, y_pos, legend_x + 1.2, y_pos)
        self._draw_many_marker(legend_x + 1.2, y_pos, legend_x + 0.4, y_pos)
        self.ax.text(legend_x + 1.5, y_pos, "One-to-Many (1:n)", fontsize=8, va='center')
        
        # n:m relationship
        y_pos -= spacing
        self.ax.plot([legend_x + 0.4, legend_x + 1.2], [y_pos, y_pos], color='black', linewidth=0.7)
        self._draw_many_marker(legend_x + 0.4, y_pos, legend_x + 1.2, y_pos)
        self._draw_many_marker(legend_x + 1.2, y_pos, legend_x + 0.4, y_pos)
        self.ax.text(legend_x + 1.5, y_pos, "Many-to-Many (n:m)", fontsize=8, va='center')
        
        # Key symbols
        y_pos -= spacing
        self.ax.text(legend_x + 0.4, y_pos, "🔑", fontsize=9, va='center')
        self.ax.text(legend_x + 1.5, y_pos, "Primary Key (PK)", fontsize=8, va='center', ha='left')
        
        y_pos -= spacing/1.5
        self.ax.text(legend_x + 0.4, y_pos, "🔗", fontsize=9, va='center')
        self.ax.text(legend_x + 1.5, y_pos, "Foreign Key (FK)", fontsize=8, va='center', ha='left')
    
    def draw_diagram(self):
        """Draw the complete FoodZone Database Diagram"""
        # Define grid positions for tables
        # Position tables with enough space to avoid overlapping
        
        # User-related tables (left column)
        user_x = 2
        users_y = 8.5
        profiles_y = 6.5
        shippers_y = 4.5
        
        # Food-related tables (middle column)
        restaurant_x = 6
        restaurant_y = 8.5
        category_x = 4
        category_y = 3
        dish_x = 7
        dish_y = 5.5
        
        # Order and delivery tables (right column)
        order_x = 10
        order_y = 8.5
        delivery_address_y = 6.5
        delivery_y = 4.5
        
        # === USER RELATED TABLES ===
        # Users table
        users_columns = [
            "id [PK]",
            "username",
            "email",
            "password",
            "is_active",
            "created_at"
        ]
        self.draw_table("Users", users_columns, user_x, users_y, self.colors['user'])
        
        # Profiles table
        profiles_columns = [
            "id [PK]",
            "user_id [FK]",
            "full_name",
            "phone_number",
            "address",
            "profile_pic",
            "updated_at"
        ]
        self.draw_table("Profiles", profiles_columns, user_x, profiles_y, self.colors['user'])
        
        # Shippers table
        shippers_columns = [
            "id [PK]",
            "user_id [FK]",
            "vehicle_type",
            "vehicle_number",
            "license_number",
            "availability_status",
            "current_location",
            "rating",
            "total_deliveries"
        ]
        self.draw_table("Shippers", shippers_columns, user_x, shippers_y, self.colors['user'])
        
        # === FOOD RELATED TABLES ===
        # Restaurants table
        restaurants_columns = [
            "id [PK]",
            "owner_id [FK]",
            "name",
            "address",
            "phone",
            "email",
            "description",
            "open_time",
            "close_time",
            "is_active"
        ]
        self.draw_table("Restaurants", restaurants_columns, restaurant_x, restaurant_y, self.colors['food'])
        
        # Categories table
        categories_columns = [
            "id [PK]",
            "name",
            "image",
            "description"
        ]
        self.draw_table("Categories", categories_columns, category_x, category_y, self.colors['food'])
        
        # Dishes table
        dishes_columns = [
            "id [PK]",
            "name",
            "category_id [FK]",
            "restaurant_id [FK]",
            "image",
            "ingredients",
            "price",
            "discounted_price",
            "is_available"
        ]
        self.draw_table("Dishes", dishes_columns, dish_x, dish_y, self.colors['food'])
        
        # === ORDER RELATED TABLES ===
        # Orders table
        orders_columns = [
            "id [PK]",
            "customer_id [FK]",
            "status",
            "total_amount",
            "payment_method",
            "payment_status",
            "ordered_on"
        ]
        self.draw_table("Orders", orders_columns, order_x, order_y, self.colors['order'])
        
        # Order Items table
        order_items_columns = [
            "id [PK]",
            "order_id [FK]",
            "dish_id [FK]",
            "quantity",
            "price",
            "subtotal"
        ]
        self.draw_table("OrderItems", order_items_columns, order_x, order_y - 2, self.colors['order'])
        
        # Delivery Addresses table
        delivery_addresses_columns = [
            "id [PK]",
            "customer_id [FK]",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "is_default"
        ]
        self.draw_table("DeliveryAddresses", delivery_addresses_columns, order_x, delivery_address_y, self.colors['delivery'])
        
        # Deliveries table
        deliveries_columns = [
            "id [PK]",
            "order_id [FK]",
            "shipper_id [FK]",
            "address_id [FK]",
            "status",
            "estimated_time",
            "actual_time",
            "notes"
        ]
        self.draw_table("Deliveries", deliveries_columns, order_x, delivery_y, self.colors['delivery'])
        
        # === RELATIONSHIPS ===
        # User relationships
        self.draw_relationship("Users", "Profiles", "1:1")
        self.draw_relationship("Users", "Shippers", "1:1")
        self.draw_relationship("Users", "Restaurants", "1:1")
        
        # Restaurant relationships
        self.draw_relationship("Restaurants", "Dishes", "1:n")
        self.draw_relationship("Categories", "Dishes", "1:n")
        
        # Order relationships
        self.draw_relationship("Profiles", "Orders", "1:n")
        self.draw_relationship("Orders", "OrderItems", "1:n")
        self.draw_relationship("Dishes", "OrderItems", "1:n")
        
        # Delivery relationships
        self.draw_relationship("Profiles", "DeliveryAddresses", "1:n")
        self.draw_relationship("Orders", "Deliveries", "1:1")
        self.draw_relationship("DeliveryAddresses", "Deliveries", "1:n")
        self.draw_relationship("Shippers", "Deliveries", "1:n")
        
        # Add legend
        self.add_legend()
        
        # Add title
        self.ax.text(6, 10.5, 'FoodZone Database Schema', ha='center', fontsize=14, fontweight='bold')
        
        # Set the figure limits with padding
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(0, 11)
        self.ax.set_axis_off()
        
        plt.tight_layout()
        plt.savefig('foodzone_database_diagram.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    diagram = FoodZoneDatabaseDiagram()
    diagram.draw_diagram() 