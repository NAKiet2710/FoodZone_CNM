import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
import numpy as np

class SimpleDatabaseDiagram:
    def __init__(self):
        # Thiết lập kích thước hình vẽ
        self.fig, self.ax = plt.subplots(figsize=(16, 10))
        
        # Màu sắc cho các bảng - giống với mẫu
        self.colors = {
            'header_bg': '#1A5276',  # Màu xanh dương đậm cho header
            'header_text': 'white',  # Màu text header
            'body_bg': '#F8F9F9',    # Màu nền body
            'border': '#D5D8DC'      # Màu viền
        }
        
        # Kích thước bảng - nhỏ gọn để không chạm vào nhau
        self.table_width = 2.0
        self.table_height = 0.25  # Chiều cao của mỗi dòng
        
        # Lưu vị trí của các bảng
        self.table_positions = {}
        
    def draw_table(self, name, columns, x, y):
        """Vẽ một bảng database với tên và các cột"""
        # Tính toán kích thước
        num_columns = len(columns)
        table_total_height = self.table_height * (num_columns + 1)  # +1 cho header
        
        # Lưu vị trí
        self.table_positions[name] = {
            'x': x,
            'y': y,
            'width': self.table_width,
            'height': table_total_height,
            'center_x': x + self.table_width/2,
            'center_y': y + table_total_height/2
        }
        
        # Vẽ header
        header = Rectangle(
            (x, y + table_total_height - self.table_height),
            self.table_width, self.table_height,
            facecolor=self.colors['header_bg'],
            edgecolor=self.colors['border'],
            linewidth=1
        )
        self.ax.add_patch(header)
        
        # Thêm tên bảng vào header
        self.ax.text(
            x + self.table_width/2, 
            y + table_total_height - self.table_height/2,
            name, 
            color=self.colors['header_text'],
            ha='center', 
            va='center', 
            fontsize=9, 
            fontweight='bold'
        )
        
        # Vẽ các dòng thân bảng
        for i in range(num_columns):
            row_y = y + table_total_height - self.table_height * (i + 2)
            row = Rectangle(
                (x, row_y),
                self.table_width, self.table_height,
                facecolor=self.colors['body_bg'],
                edgecolor=self.colors['border'],
                linewidth=0.5
            )
            self.ax.add_patch(row)
            
            # Tách tên cột và kiểu dữ liệu
            col_name = columns[i]['name']
            col_type = columns[i]['type']
            
            # Vẽ tên trường
            self.ax.text(
                x + 0.1, 
                row_y + self.table_height/2,
                col_name, 
                ha='left', 
                va='center', 
                fontsize=7.5
            )
            
            # Vẽ kiểu dữ liệu
            self.ax.text(
                x + self.table_width - 0.1, 
                row_y + self.table_height/2,
                col_type, 
                ha='right', 
                va='center', 
                fontsize=7.5,
                color='gray'
            )
            
            # Thêm ký hiệu khóa nếu cần
            if 'key' in columns[i] and columns[i]['key']:
                # Vẽ hình tròn nhỏ thay cho emoji (để tránh vấn đề font)
                if columns[i]['key'] == 'PK':
                    # Ký hiệu PK (khóa chính) - hình vuông
                    self.ax.plot(
                        [x + 0.7], 
                        [row_y + self.table_height/2],
                        marker='s',  # Hình vuông
                        markersize=4,
                        color='black'
                    )
                else:
                    # Ký hiệu FK (khóa ngoại) - hình tròn
                    self.ax.plot(
                        [x + 0.7], 
                        [row_y + self.table_height/2],
                        marker='o',  # Hình tròn
                        markersize=4,
                        color='gray'
                    )
        
        return table_total_height
    
    def find_best_connection_point(self, source_table, target_table):
        """Tìm điểm kết nối tốt nhất giữa hai bảng dựa trên vị trí tương đối"""
        source = self.table_positions[source_table]
        target = self.table_positions[target_table]
        
        # Xác định mối quan hệ không gian giữa hai bảng
        if abs(source['center_x'] - target['center_x']) > abs(source['center_y'] - target['center_y']):
            # Bảng nằm bên cạnh nhau (quan hệ ngang)
            if source['center_x'] < target['center_x']:
                # Source bên trái target
                source_x = source['x'] + source['width']
                source_y = source['center_y']
                target_x = target['x']
                target_y = target['center_y']
            else:
                # Source bên phải target
                source_x = source['x']
                source_y = source['center_y']
                target_x = target['x'] + target['width']
                target_y = target['center_y']
        else:
            # Bảng nằm trên dưới nhau (quan hệ dọc)
            if source['center_y'] < target['center_y']:
                # Source bên dưới target
                source_x = source['center_x']
                source_y = source['y'] + source['height']
                target_x = target['center_x']
                target_y = target['y']
            else:
                # Source bên trên target
                source_x = source['center_x']
                source_y = source['y']
                target_x = target['center_x']
                target_y = target['y'] + target['height']
                
        return (source_x, source_y), (target_x, target_y)
    
    def draw_relationship(self, source_table, target_table, relation_type="1:n"):
        """Vẽ mối quan hệ giữa hai bảng"""
        if source_table not in self.table_positions or target_table not in self.table_positions:
            return
        
        # Lấy điểm kết nối tốt nhất
        (source_x, source_y), (target_x, target_y) = self.find_best_connection_point(source_table, target_table)
        
        # Kiểm tra xem hai bảng có quá gần nhau không
        source = self.table_positions[source_table]
        target = self.table_positions[target_table]
        is_horizontal = abs(source['center_x'] - target['center_x']) > abs(source['center_y'] - target['center_y'])
        
        # Vẽ đường kết nối
        if is_horizontal:
            # Nếu hai bảng nằm ngang với nhau
            mid_x = (source_x + target_x) / 2
            self.ax.plot([source_x, mid_x, mid_x, target_x], 
                          [source_y, source_y, target_y, target_y],
                          color='black', linewidth=0.8)
            
            # Thêm mũi tên hướng về bảng đích
            if mid_x != target_x:  # Tránh trường hợp điểm giữa trùng với điểm cuối
                # Vẽ mũi tên
                arrow_length = 0.1
                if target_x > mid_x:
                    self.ax.arrow(target_x - arrow_length, target_y, arrow_length * 0.8, 0,
                              head_width=0.06, head_length=0.06, fc='black', ec='black', linewidth=0.8)
                else:
                    self.ax.arrow(target_x + arrow_length, target_y, -arrow_length * 0.8, 0,
                              head_width=0.06, head_length=0.06, fc='black', ec='black', linewidth=0.8)
        else:
            # Nếu hai bảng nằm dọc với nhau
            mid_y = (source_y + target_y) / 2
            self.ax.plot([source_x, source_x, target_x, target_x], 
                          [source_y, mid_y, mid_y, target_y],
                          color='black', linewidth=0.8)
            
            # Thêm mũi tên hướng về bảng đích
            if mid_y != target_y:  # Tránh trường hợp điểm giữa trùng với điểm cuối
                # Vẽ mũi tên
                arrow_length = 0.1
                if target_y > mid_y:
                    self.ax.arrow(target_x, target_y - arrow_length, 0, arrow_length * 0.8,
                              head_width=0.06, head_length=0.06, fc='black', ec='black', linewidth=0.8)
                else:
                    self.ax.arrow(target_x, target_y + arrow_length, 0, -arrow_length * 0.8,
                              head_width=0.06, head_length=0.06, fc='black', ec='black', linewidth=0.8)
    
    def draw_diagram(self):
        """Vẽ hoàn chỉnh biểu đồ database FoodZone theo bố cục trong hình mẫu mới"""
        # === BỐ TRÍ CÁC BẢNG THEO HÌNH MẪU ===
        
        # Cột bên trái
        users_x, users_y = 3, 6
        dishes_x, dishes_y = 3, 3
        delivery_addresses_x, delivery_addresses_y = 3, 0.5
        
        # Cột giữa (categories)
        categories_x, categories_y = 6.5, 3
        
        # Cột bên phải
        restaurants_x, restaurants_y = 10, 6
        orders_x, orders_y = 10, 3
        deliveries_x, deliveries_y = 10, 0.5
        
        # Cột ngoài cùng bên phải
        order_items_x, order_items_y = 13, 4.5
        
        # === BẢNG USERS ===
        users_columns = [
            {'name': 'id', 'type': 'int NN', 'key': 'PK'},
            {'name': 'email', 'type': 'varchar NN'},
            {'name': 'password', 'type': 'varchar NN'},
            {'name': 'firstname', 'type': 'varchar'},
            {'name': 'lastname', 'type': 'varchar'},
            {'name': 'age', 'type': 'int'},
            {'name': 'gender', 'type': 'varchar'},
            {'name': 'address', 'type': 'varchar'},
            {'name': 'phone', 'type': 'varchar'}
        ]
        self.draw_table('users', users_columns, users_x, users_y)
        
        # === BẢNG RESTAURANTS ===
        restaurants_columns = [
            {'name': 'id', 'type': 'int NN', 'key': 'PK'},
            {'name': 'owner_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'name', 'type': 'varchar NN'},
            {'name': 'address', 'type': 'varchar'},
            {'name': 'phone', 'type': 'varchar'},
            {'name': 'email', 'type': 'varchar'},
            {'name': 'open_time', 'type': 'time'},
            {'name': 'close_time', 'type': 'time'},
            {'name': 'is_active', 'type': 'boolean NN'}
        ]
        self.draw_table('restaurants', restaurants_columns, restaurants_x, restaurants_y)
        
        # === BẢNG CATEGORIES ===
        categories_columns = [
            {'name': 'id', 'type': 'int NN', 'key': 'PK'},
            {'name': 'name', 'type': 'varchar NN'},
            {'name': 'description', 'type': 'text'}
        ]
        self.draw_table('categories', categories_columns, categories_x, categories_y)
        
        # === BẢNG DISHES ===
        dishes_columns = [
            {'name': 'id', 'type': 'int NN', 'key': 'PK'},
            {'name': 'name', 'type': 'varchar NN'},
            {'name': 'restaurant_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'category_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'price', 'type': 'decimal NN'},
            {'name': 'description', 'type': 'text'},
            {'name': 'ingredients', 'type': 'text'},
            {'name': 'image_url', 'type': 'varchar'},
            {'name': 'is_available', 'type': 'boolean NN'}
        ]
        self.draw_table('dishes', dishes_columns, dishes_x, dishes_y)
        
        # === BẢNG ORDERS ===
        orders_columns = [
            {'name': 'id', 'type': 'int NN', 'key': 'PK'},
            {'name': 'user_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'status', 'type': 'varchar NN'},
            {'name': 'order_date', 'type': 'timestamp NN'},
            {'name': 'total_amount', 'type': 'decimal NN'},
            {'name': 'payment_method', 'type': 'varchar'},
            {'name': 'payment_status', 'type': 'varchar'}
        ]
        self.draw_table('orders', orders_columns, orders_x, orders_y)
        
        # === BẢNG ORDER_ITEMS ===
        order_items_columns = [
            {'name': 'id', 'type': 'int NN', 'key': 'PK'},
            {'name': 'order_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'dish_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'quantity', 'type': 'int NN'},
            {'name': 'price', 'type': 'decimal NN'},
            {'name': 'subtotal', 'type': 'decimal NN'}
        ]
        self.draw_table('order_items', order_items_columns, order_items_x, order_items_y)
        
        # === BẢNG DELIVERY_ADDRESSES ===
        delivery_addresses_columns = [
            {'name': 'id', 'type': 'int NN', 'key': 'PK'},
            {'name': 'user_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'address_line', 'type': 'varchar NN'},
            {'name': 'city', 'type': 'varchar NN'},
            {'name': 'state', 'type': 'varchar'},
            {'name': 'postal_code', 'type': 'varchar'},
            {'name': 'is_default', 'type': 'boolean'}
        ]
        self.draw_table('delivery_addresses', delivery_addresses_columns, delivery_addresses_x, delivery_addresses_y)
        
        # === BẢNG DELIVERIES ===
        deliveries_columns = [
            {'name': 'id', 'type': 'int NN', 'key': 'PK'},
            {'name': 'order_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'shipper_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'address_id', 'type': 'int NN', 'key': 'FK'},
            {'name': 'status', 'type': 'varchar NN'},
            {'name': 'start_time', 'type': 'timestamp'},
            {'name': 'end_time', 'type': 'timestamp'},
            {'name': 'notes', 'type': 'text'}
        ]
        self.draw_table('deliveries', deliveries_columns, deliveries_x, deliveries_y)
        
        # === VẼ MỐI QUAN HỆ - TỐI ƯU THEO HÌNH MẪU ===
        # 1. User -> Restaurant (Owner)
        self.draw_relationship('users', 'restaurants')
        
        # 2. Restaurant -> Dishes
        self.draw_relationship('restaurants', 'dishes')
        
        # 3. Categories -> Dishes
        self.draw_relationship('categories', 'dishes')
        
        # 4. User -> Orders
        self.draw_relationship('users', 'orders')
        
        # 5. Orders -> Order_Items
        self.draw_relationship('orders', 'order_items')
        
        # 6. Dishes -> Order_Items
        self.draw_relationship('dishes', 'order_items')
        
        # 7. User -> Delivery_Addresses
        self.draw_relationship('users', 'delivery_addresses')
        
        # 8. Delivery_Addresses -> Deliveries
        self.draw_relationship('delivery_addresses', 'deliveries')
        
        # 9. Orders -> Deliveries
        self.draw_relationship('orders', 'deliveries')
        
        # === THIẾT LẬP KHÔNG GIAN VẼ ===
        self.ax.set_xlim(1, 16)
        self.ax.set_ylim(0, 9)
        self.ax.set_axis_off()
        
        # Thêm tiêu đề
        self.ax.text(8, 8.5, 'FoodZone Database Schema', ha='center', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('foodzone_database_diagram_balanced.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    diagram = SimpleDatabaseDiagram()
    diagram.draw_diagram() 