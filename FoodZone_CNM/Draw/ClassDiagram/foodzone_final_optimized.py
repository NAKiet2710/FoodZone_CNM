import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

class FoodZoneFinalOptimizedDiagram:
    def __init__(self):
        # Khởi tạo figure với kích thước phù hợp
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        
        # Màu sắc cho các nhóm class
        self.colors = {
            'user': '#e3f2fd',      # Xanh nhạt cho user model
            'food': '#c8e6c9',      # Xanh lá cho đồ ăn
            'order': '#fff9c4',     # Vàng cho đơn hàng
            'delivery': '#ffccbc',  # Cam cho giao hàng
        }
        
        # Vị trí các class
        self.positions = {}
        # Kích thước box
        self.box_width = 1.5
        
    def draw_class_box(self, name, attributes, x, y, color):
        """Vẽ một class box với tên và thuộc tính"""
        # Tính toán kích thước
        attr_height = 0.2 * len(attributes) if attributes else 0
        header_height = 0.3
        total_height = header_height + attr_height
        
        # Lưu vị trí
        self.positions[name] = (x, y, total_height)
        
        # Vẽ box chính
        box = FancyBboxPatch(
            (x - self.box_width/2, y),
            self.box_width, total_height,
            boxstyle="round,pad=0.1",
            facecolor=color, alpha=0.9, 
            edgecolor='black', linewidth=0.6
        )
        self.ax.add_patch(box)
        
        # Vẽ tên class
        self.ax.text(x, y + total_height - header_height/2, name, 
                    ha='center', va='center', fontsize=7, fontweight='bold')
        
        # Vẽ đường ngăn cách
        if attributes:
            self.ax.plot(
                [x - self.box_width/2, x + self.box_width/2],
                [y + total_height - header_height, y + total_height - header_height],
                color='black', linestyle='-', linewidth=0.6
            )
        
        # Vẽ thuộc tính
        for i, attr in enumerate(attributes):
            y_pos = y + total_height - header_height - (i + 0.5) * 0.2
            self.ax.text(
                x - self.box_width/2 + 0.1, y_pos, attr,
                ha='left', va='center', fontsize=6
            )
        
        return total_height
    
    def draw_relationship(self, from_class, to_class, rel_type='association', label=None):
        """Vẽ mối quan hệ giữa các class với nhãn ở chính giữa mũi tên"""
        # Lấy thông tin vị trí
        from_x, from_y, from_height = self.positions[from_class]
        to_x, to_y, to_height = self.positions[to_class]
        
        # Xác định điểm kết nối
        if from_x == to_x:  # Cùng cột
            if from_y > to_y:  # from ở trên to
                start_x, start_y = from_x, from_y
                end_x, end_y = to_x, to_y + to_height
            else:  # from ở dưới to
                start_x, start_y = from_x, from_y + from_height
                end_x, end_y = to_x, to_y
        else:  # Khác cột
            # Xác định điểm kết nối ngang
            if from_x < to_x:  # from ở bên trái to
                start_x = from_x + self.box_width/2
                end_x = to_x - self.box_width/2
            else:  # from ở bên phải to
                start_x = from_x - self.box_width/2
                end_x = to_x + self.box_width/2
            
            # Xác định điểm kết nối dọc
            start_y = from_y + from_height/2
            end_y = to_y + to_height/2
            
        # Vẽ đường nối
        self.ax.plot([start_x, end_x], [start_y, end_y], 
                     color='black', linestyle='-', linewidth=0.6)
        
        # Vẽ đầu mũi tên theo loại quan hệ 
        if rel_type == 'association':
            self._draw_association_arrow(end_x, end_y, start_x, start_y)
        elif rel_type == 'composition':
            self._draw_composition_arrow(end_x, end_y, start_x, start_y)
        
        # Thêm nhãn nếu có - đặt ở chính giữa mũi tên
        if label:
            # Tính điểm giữa của đường kết nối
            middle_x = (start_x + end_x) / 2
            middle_y = (start_y + end_y) / 2
            
            # Thêm background trắng cho nhãn để tránh bị đè lên đường
            self.ax.text(middle_x, middle_y, label, 
                         ha='center', va='center', fontsize=6,
                         bbox=dict(facecolor='white', alpha=0.9, edgecolor='none', 
                                   boxstyle='round,pad=0.2'))
    
    def _draw_association_arrow(self, x, y, from_x, from_y):
        """Vẽ mũi tên association thông thường"""
        dx = from_x - x
        dy = from_y - y
        angle = np.arctan2(dy, dx)
        
        head_length = 0.07
        head_width = 0.04
        arrow = FancyArrowPatch((x, y), 
                               (x + head_length * np.cos(angle), 
                                y + head_length * np.sin(angle)),
                               arrowstyle='->', 
                               connectionstyle=f"arc3, rad=0", 
                               linewidth=0.6, 
                               color='black',
                               shrinkA=0, shrinkB=0, 
                               mutation_scale=8)
        self.ax.add_patch(arrow)
    
    def _draw_composition_arrow(self, x, y, from_x, from_y):
        """Vẽ mũi tên composition (hình thoi đầy đặn)"""
        dx = from_x - x
        dy = from_y - y
        angle = np.arctan2(dy, dx)
        
        # Tạo các điểm cho hình thoi
        h = 0.06  # Nửa chiều dài hình thoi
        w = 0.03  # Nửa chiều rộng hình thoi
        point1 = (x, y)
        point2 = (x + h * np.cos(angle) + w * np.cos(angle + np.pi/2),
                 y + h * np.sin(angle) + w * np.sin(angle + np.pi/2))
        point3 = (x + 2 * h * np.cos(angle),
                 y + 2 * h * np.sin(angle))
        point4 = (x + h * np.cos(angle) + w * np.cos(angle - np.pi/2),
                 y + h * np.sin(angle) + w * np.sin(angle - np.pi/2))
        
        # Vẽ hình thoi đầy đặn
        diamond = plt.Polygon([point1, point2, point3, point4], 
                             closed=True, fill=True, facecolor='black', edgecolor='black')
        self.ax.add_patch(diamond)
    
    def draw_foodzone_diagram(self):
        """Vẽ class diagram được tối ưu hóa và chỉnh sửa theo yêu cầu"""
        # ===== VỊ TRÍ CỦA CÁC CỘT VÀ HÀNG =====
        col1_x = 2
        col2_x = 6
        col3_x = 10
        
        row1_y = 7
        row2_y = 4.5
        row3_y = 2
        
        # ===== USER COLUMN =====
        # Vẽ class User
        user_attrs = [
            '+ user_id: PK',
            '+ username: String',
            '+ email: String'
        ]
        user_height = self.draw_class_box('User', user_attrs, col1_x, row1_y, self.colors['user'])
        
        # Vẽ class Profile
        profile_attrs = [
            '+ profile_id: PK', 
            '+ user_id: FK(User)',
            '+ address: String',
            '+ phone: String'
        ]
        profile_height = self.draw_class_box('Profile', profile_attrs, col1_x, row2_y, self.colors['user'])
        
        # Vẽ class Shipper
        shipper_attrs = [
            '+ shipper_id: PK',
            '+ user_id: FK(User)',
            '+ vehicle_type: String',
            '+ is_available: Boolean'
        ]
        shipper_height = self.draw_class_box('Shipper', shipper_attrs, col1_x, row3_y, self.colors['user'])
        
        # ===== FOOD COLUMN =====
        # Vẽ class Restaurant
        restaurant_attrs = [
            '+ restaurant_id: PK',
            '+ owner_id: FK(User)',
            '+ name: String',
            '+ address: String'
        ]
        restaurant_height = self.draw_class_box('Restaurant', restaurant_attrs, col2_x, row1_y, self.colors['food'])
        
        # Vẽ class Category
        category_attrs = [
            '+ category_id: PK',
            '+ name: String',
            '+ image_url: String'
        ]
        category_height = self.draw_class_box('Category', category_attrs, col2_x, row2_y, self.colors['food'])
        
        # Vẽ class Dish
        dish_attrs = [
            '+ dish_id: PK',
            '+ name: String',
            '+ price: Float',
            '+ category_id: FK(Category)',
            '+ restaurant_id: FK(Restaurant)'
        ]
        dish_height = self.draw_class_box('Dish', dish_attrs, col2_x, row3_y, self.colors['food'])
        
        # ===== ORDER COLUMN =====
        # Vẽ class Order
        order_attrs = [
            '+ order_id: PK',
            '+ profile_id: FK(Profile)',
            '+ dish_id: FK(Dish)',
            '+ status: String'
        ]
        order_height = self.draw_class_box('Order', order_attrs, col3_x, row1_y, self.colors['order'])
        
        # Vẽ class DeliveryAddress
        address_attrs = [
            '+ address_id: PK',
            '+ profile_id: FK(Profile)',
            '+ street: String',
            '+ city: String'
        ]
        address_height = self.draw_class_box('DeliveryAddress', address_attrs, col3_x, row2_y, self.colors['delivery'])
        
        # Vẽ class Delivery
        delivery_attrs = [
            '+ delivery_id: PK',
            '+ order_id: FK(Order)',
            '+ shipper_id: FK(Shipper)',
            '+ address_id: FK(Address)',
            '+ status: String'
        ]
        delivery_height = self.draw_class_box('Delivery', delivery_attrs, col3_x, row3_y, self.colors['delivery'])
        
        # ===== RELATIONSHIPS =====
        # User - Restaurant
        self.draw_relationship('User', 'Restaurant', 'association', '1:1')
        
        # User - Profile
        self.draw_relationship('User', 'Profile', 'association', '1:1')
        
        # User - Shipper
        self.draw_relationship('User', 'Shipper', 'association', '1:1')
        
        # Profile - DeliveryAddress
        self.draw_relationship('Profile', 'DeliveryAddress', 'composition', '1:n')
        
        # Profile - Order
        self.draw_relationship('Profile', 'Order', 'composition', '1:n')
        
        # Category - Dish
        self.draw_relationship('Category', 'Dish', 'composition', '1:n')
        
        # Restaurant - Dish
        self.draw_relationship('Restaurant', 'Dish', 'composition', '1:n')
        
        # Dish - Order
        self.draw_relationship('Dish', 'Order', 'association', '1:n')
        
        # Order - Delivery
        self.draw_relationship('Order', 'Delivery', 'association', '1:1')
        
        # Shipper - Delivery
        self.draw_relationship('Shipper', 'Delivery', 'association', '1:n')
        
        # DeliveryAddress - Delivery
        self.draw_relationship('DeliveryAddress', 'Delivery', 'association', '1:n')

        # Chỉ thêm tiêu đề biểu đồ
        self.ax.text(6, 10, 'Class Diagram - FoodZone', ha='center', fontsize=12, fontweight='bold')
        
        # Hoàn thiện biểu đồ với nhiều không gian trống
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(1, 11)
        self.ax.set_axis_off()
        
        plt.tight_layout()
        
        # Lưu biểu đồ
        plt.savefig('foodzone_final_optimized.png', dpi=350, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    diagram = FoodZoneFinalOptimizedDiagram()
    diagram.draw_foodzone_diagram() 