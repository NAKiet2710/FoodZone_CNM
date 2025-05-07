import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch

def draw_use_case_diagram():
    """
    Vẽ biểu đồ use case cho ứng dụng web FoodZone với bố cục dễ nhìn hơn
    """
    # Tạo figure và axis
    plt.figure(figsize=(12, 9))
    ax = plt.gca()
    
    # Vẽ đường biên hệ thống
    system_rect = Rectangle((1.5, 0.5), 7, 8, fill=False, linestyle='--', linewidth=1.5, edgecolor='gray')
    ax.add_patch(system_rect)
    ax.text(5, 8.7, 'Hệ Thống FoodZone', fontsize=16, fontweight='bold', ha='center')
    
    # Định nghĩa vị trí các tác nhân (actors) theo hàng ngang
    actor_positions = {
        'Khách Hàng': (0.7, 7),
        'Shipper': (0.7, 4),
        'Chủ Nhà Hàng': (9.3, 7),
        'Quản Trị Viên': (9.3, 4)
    }
    
    # Vẽ các tác nhân
    for actor, pos in actor_positions.items():
        # Vẽ hình người đơn giản
        circle = plt.Circle(pos, 0.15, facecolor='white', edgecolor='black')
        line = plt.Line2D([pos[0], pos[0]], [pos[1]-0.15, pos[1]-0.5], color='black')
        arm1 = plt.Line2D([pos[0]-0.15, pos[0]+0.15], [pos[1]-0.3, pos[1]-0.3], color='black')
        leg1 = plt.Line2D([pos[0], pos[0]-0.1], [pos[1]-0.5, pos[1]-0.7], color='black')
        leg2 = plt.Line2D([pos[0], pos[0]+0.1], [pos[1]-0.5, pos[1]-0.7], color='black')
        
        ax.add_patch(circle)
        ax.add_line(line)
        ax.add_line(arm1)
        ax.add_line(leg1)
        ax.add_line(leg2)
        
        # Thêm tên actor
        ax.text(pos[0], pos[1]-0.9, actor, ha='center', fontsize=10, fontweight='bold')
    
    # Định nghĩa các use case chính theo hàng và cột rõ ràng
    # Cột phía khách hàng
    left_column = {
        'Xem Thực Đơn': (2.5, 8),
        'Đặt Món': (2.5, 7),
        'Theo Dõi Đơn Hàng': (2.5, 6),
        'Tương Tác Chatbot': (2.5, 5),
        'Cập Nhật Trạng Thái': (2.5, 3),
        'Quản Lý Tình Trạng': (2.5, 2)
    }
    
    # Cột giữa
    middle_column = {
        'Đăng Nhập/Đăng Ký': (5, 8.5),
        'Thanh Toán': (5, 7.5),
        'Quản Lý Địa Chỉ': (5, 6.5),
        'Đặt Bàn': (5, 5.5),
        'Đổi Mật Khẩu': (5, 4.5),
        'Cập Nhật Vị Trí': (5, 3.5),
        'Xem Báo Cáo': (5, 2.5),
        'Quản Lý Danh Mục': (5, 1.5)
    }
    
    # Cột phía chủ nhà hàng/admin
    right_column = {
        'Quản Lý Nhà Hàng': (7.5, 8),
        'Quản Lý Món Ăn': (7.5, 7),
        'Quản Lý Đơn Hàng': (7.5, 6),
        'Xem Thống Kê': (7.5, 5),
        'Quản Lý Người Dùng': (7.5, 3),
        'Quản Lý Nội Dung': (7.5, 2)
    }
    
    # Gộp tất cả use cases
    use_cases = {}
    use_cases.update(left_column)
    use_cases.update(middle_column)
    use_cases.update(right_column)
    
    # Vẽ các use case
    for use_case, pos in use_cases.items():
        ellipse = Ellipse(pos, 1.6, 0.6, fill=True, color='lightblue', alpha=0.5)
        ax.add_patch(ellipse)
        ax.text(pos[0], pos[1], use_case, ha='center', va='center', fontsize=9)
    
    # Kết nối actors với use cases
    connections = [
        # Khách hàng
        ('Khách Hàng', 'Xem Thực Đơn'),
        ('Khách Hàng', 'Đặt Món'),
        ('Khách Hàng', 'Theo Dõi Đơn Hàng'),
        ('Khách Hàng', 'Tương Tác Chatbot'),
        ('Khách Hàng', 'Đăng Nhập/Đăng Ký'),
        ('Khách Hàng', 'Thanh Toán'),
        ('Khách Hàng', 'Quản Lý Địa Chỉ'),
        ('Khách Hàng', 'Đặt Bàn'),
        ('Khách Hàng', 'Đổi Mật Khẩu'),
        
        # Shipper
        ('Shipper', 'Đăng Nhập/Đăng Ký'),
        ('Shipper', 'Cập Nhật Trạng Thái'),
        ('Shipper', 'Cập Nhật Vị Trí'),
        ('Shipper', 'Quản Lý Tình Trạng'),
        ('Shipper', 'Đổi Mật Khẩu'),
        
        # Chủ nhà hàng
        ('Chủ Nhà Hàng', 'Đăng Nhập/Đăng Ký'),
        ('Chủ Nhà Hàng', 'Quản Lý Nhà Hàng'),
        ('Chủ Nhà Hàng', 'Quản Lý Món Ăn'),
        ('Chủ Nhà Hàng', 'Quản Lý Đơn Hàng'),
        ('Chủ Nhà Hàng', 'Xem Thống Kê'),
        ('Chủ Nhà Hàng', 'Đổi Mật Khẩu'),
        
        # Quản trị viên
        ('Quản Trị Viên', 'Đăng Nhập/Đăng Ký'),
        ('Quản Trị Viên', 'Quản Lý Người Dùng'),
        ('Quản Trị Viên', 'Quản Lý Danh Mục'),
        ('Quản Trị Viên', 'Xem Báo Cáo'),
        ('Quản Trị Viên', 'Quản Lý Nội Dung')
    ]
    
    # Vẽ kết nối với màu nhạt và độ cong khác nhau dựa trên actor
    for actor, use_case in connections:
        actor_pos = actor_positions[actor]
        use_case_pos = use_cases[use_case]
        
        # Đặt độ cong và màu khác nhau cho từng actor để dễ nhìn hơn
        if actor == 'Khách Hàng':
            color = 'lightcoral'
            rad = 0.1
        elif actor == 'Shipper':
            color = 'lightseagreen'
            rad = 0.15
        elif actor == 'Chủ Nhà Hàng':
            color = 'mediumpurple'
            rad = -0.1
        else:  # Quản Trị Viên
            color = 'goldenrod'
            rad = -0.15
            
        arrow = FancyArrowPatch(actor_pos, use_case_pos, connectionstyle=f"arc3,rad={rad}", 
                              arrowstyle="->", color=color, lw=0.8, alpha=0.6, shrinkA=20, shrinkB=10)
        ax.add_patch(arrow)
    
    # Thêm mối quan hệ include/extend với đường mũi tên rõ ràng
    relationships = [
        ('Đặt Món', 'Xem Thực Đơn', 'bao gồm'),
        ('Đặt Món', 'Thanh Toán', 'bao gồm'),
        ('Đặt Món', 'Quản Lý Địa Chỉ', 'bao gồm'),
        ('Theo Dõi Đơn Hàng', 'Đặt Món', 'mở rộng'),
        ('Đặt Bàn', 'Xem Thực Đơn', 'bao gồm'),
        ('Cập Nhật Trạng Thái', 'Cập Nhật Vị Trí', 'bao gồm')
    ]
    
    for use_case1, use_case2, rel_type in relationships:
        use_case1_pos = use_cases[use_case1]
        use_case2_pos = use_cases[use_case2]
        
        # Kiểu đường khác nhau cho include và extend
        style = 'dashed' if rel_type == 'mở rộng' else 'solid'
        
        # Sử dụng màu xanh đậm hơn và mũi tên rõ ràng
        arrow = FancyArrowPatch(use_case1_pos, use_case2_pos, connectionstyle="arc3,rad=-0.3", 
                              arrowstyle="-|>", linestyle=style, color='royalblue', lw=1.2, shrinkA=10, shrinkB=10)
        ax.add_patch(arrow)
        
        # Thêm nhãn mối quan hệ với nền trắng để dễ đọc
        mid_x = (use_case1_pos[0] + use_case2_pos[0]) / 2
        mid_y = (use_case1_pos[1] + use_case2_pos[1]) / 2
        # Offset để đặt trên mũi tên
        offset_x = (use_case2_pos[1] - use_case1_pos[1]) * 0.1
        offset_y = (use_case1_pos[0] - use_case2_pos[0]) * 0.1
        
        label = ax.text(mid_x + offset_x, mid_y + offset_y, f'<<{rel_type}>>', 
                 fontsize=8, ha='center', va='center', color='blue',
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
    
    # Thêm chú thích
    legend_elements = [
        plt.Line2D([0], [0], color='lightcoral', lw=2, label='Khách Hàng'),
        plt.Line2D([0], [0], color='lightseagreen', lw=2, label='Shipper'),
        plt.Line2D([0], [0], color='mediumpurple', lw=2, label='Chủ Nhà Hàng'),
        plt.Line2D([0], [0], color='goldenrod', lw=2, label='Quản Trị Viên'),
        plt.Line2D([0], [0], color='royalblue', lw=2, linestyle='solid', label='<<bao gồm>>'),
        plt.Line2D([0], [0], color='royalblue', lw=2, linestyle='dashed', label='<<mở rộng>>')
    ]
    ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.05),
              ncol=3, fontsize=9)
    
    # Thiết lập thuộc tính của trục
    plt.xlim(0, 10)
    plt.ylim(0, 9)
    plt.axis('off')
    plt.title('Biểu Đồ Use Case FoodZone', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('Draw/usecase_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()

def draw_order_flow():
    """
    Vẽ biểu đồ luồng cho quy trình đặt món ăn với bố cục thẳng hàng
    """
    # Tạo đồ thị có hướng cho luồng đặt hàng
    G = nx.DiGraph()
    
    # Thêm các node cho từng bước trong quy trình đặt hàng
    nodes = [
        'Xem Thực Đơn',
        'Đăng Nhập',
        'Chọn Món',
        'Kiểm Tra Địa Chỉ',
        'Thanh Toán',
        'Xác Nhận Đơn',
        'Chuẩn Bị Món',
        'Giao Hàng',
        'Nhận Hàng',
        'Đánh Giá'
    ]
    
    # Thêm node với vị trí thẳng hàng hơn
    positions = {
        # Hàng trên - Quy trình khách hàng
        'Xem Thực Đơn': (1, 2),
        'Đăng Nhập': (2, 2),
        'Chọn Món': (3, 2),
        'Kiểm Tra Địa Chỉ': (4, 2),
        'Thanh Toán': (5, 2),
        'Xác Nhận Đơn': (6, 2),
        
        # Hàng dưới - Quy trình nhà hàng và shipper
        'Chuẩn Bị Món': (6, 1),
        'Giao Hàng': (4, 1),
        'Nhận Hàng': (2, 1),
        'Đánh Giá': (1, 1)
    }
    
    for node in nodes:
        G.add_node(node)
    
    # Thêm cạnh cho luồng
    edges = [
        ('Xem Thực Đơn', 'Đăng Nhập'),
        ('Đăng Nhập', 'Chọn Món'),
        ('Chọn Món', 'Kiểm Tra Địa Chỉ'),
        ('Kiểm Tra Địa Chỉ', 'Thanh Toán'),
        ('Thanh Toán', 'Xác Nhận Đơn'),
        ('Xác Nhận Đơn', 'Chuẩn Bị Món'),
        ('Chuẩn Bị Món', 'Giao Hàng'),
        ('Giao Hàng', 'Nhận Hàng'),
        ('Nhận Hàng', 'Đánh Giá')
    ]
    
    for edge in edges:
        G.add_edge(edge[0], edge[1])
    
    plt.figure(figsize=(10, 3.5))
    
    # Định nghĩa màu sắc node theo tác nhân với màu đẹp hơn
    node_colors = {
        'khach_hang': '#b2dfdb',  # xanh lá nhạt
        'he_thong': '#bbdefb',    # xanh dương nhạt
        'nha_hang': '#fff59d',    # vàng nhạt
        'shipper': '#ffccbc'      # cam nhạt
    }
    
    # Gán tác nhân cho mỗi node
    node_actor = {
        'Xem Thực Đơn': 'khach_hang',
        'Đăng Nhập': 'khach_hang',
        'Chọn Món': 'khach_hang',
        'Kiểm Tra Địa Chỉ': 'khach_hang',
        'Thanh Toán': 'khach_hang',
        'Xác Nhận Đơn': 'he_thong',
        'Chuẩn Bị Món': 'nha_hang',
        'Giao Hàng': 'shipper',
        'Nhận Hàng': 'khach_hang',
        'Đánh Giá': 'khach_hang'
    }
    
    # Tạo bản đồ màu
    color_map = [node_colors[node_actor[node]] for node in G.nodes()]
    
    # Vẽ đồ thị với các viền rõ ràng hơn
    nx.draw(G, positions, with_labels=True, node_color=color_map, 
            node_size=1500, arrowsize=15, font_size=9, font_weight='bold',
            width=1.5, edge_color='gray', edgecolors='gray', linewidths=1)
    
    # Tạo chú thích
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor=node_colors['khach_hang'], label='Khách Hàng', edgecolor='gray'),
        plt.Rectangle((0, 0), 1, 1, facecolor=node_colors['he_thong'], label='Hệ Thống', edgecolor='gray'),
        plt.Rectangle((0, 0), 1, 1, facecolor=node_colors['nha_hang'], label='Nhà Hàng', edgecolor='gray'),
        plt.Rectangle((0, 0), 1, 1, facecolor=node_colors['shipper'], label='Shipper', edgecolor='gray')
    ]
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0), 
               ncol=4, fontsize=9)
    
    plt.title('Quy Trình Đặt Món Ăn', fontsize=14, pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('Draw/order_flow.png', dpi=300, bbox_inches='tight')
    plt.show()

def draw_entity_relationships():
    """
    Vẽ đồ thị biểu diễn mối quan hệ giữa các thực thể và vai trò người dùng với bố cục rõ ràng
    """
    # Tạo đồ thị cho các mối quan hệ
    G = nx.Graph()
    
    # Định nghĩa các node (vai trò và thực thể)
    roles = [
        'Khách Hàng',
        'Shipper',
        'Chủ Nhà Hàng',
        'Quản Trị Viên',
        'Đơn Hàng', 
        'Món Ăn',
        'Giao Hàng',
        'Thanh Toán',
        'Nhà Hàng',
        'Địa Chỉ',
        'Danh Mục',
        'Đánh Giá'
    ]
    
    # Thêm node
    for role in roles:
        G.add_node(role)
        
    # Định nghĩa vị trí các node theo hình tròn cho dễ nhìn
    import math
    
    # Định vị vai trò người dùng ở bốn góc
    pos = {
        'Khách Hàng': (-3, 2),
        'Shipper': (-3, -2),
        'Chủ Nhà Hàng': (3, 2),
        'Quản Trị Viên': (3, -2),
    }
    
    # Định vị các thực thể theo hình tròn ở giữa
    entity_nodes = [node for node in roles if node not in pos]
    n_entities = len(entity_nodes)
    radius = 1.8
    
    for i, node in enumerate(entity_nodes):
        angle = 2 * math.pi * i / n_entities
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        pos[node] = (x, y)
    
    # Định nghĩa các mối quan hệ
    relationships = [
        ('Khách Hàng', 'Đơn Hàng', 'Đặt'),
        ('Khách Hàng', 'Thanh Toán', 'Thực hiện'),
        ('Khách Hàng', 'Địa Chỉ', 'Quản lý'),
        ('Khách Hàng', 'Đánh Giá', 'Tạo'),
        ('Shipper', 'Giao Hàng', 'Thực hiện'),
        ('Chủ Nhà Hàng', 'Nhà Hàng', 'Quản lý'),
        ('Chủ Nhà Hàng', 'Món Ăn', 'Tạo'),
        ('Quản Trị Viên', 'Danh Mục', 'Quản lý'),
        ('Quản Trị Viên', 'Nhà Hàng', 'Duyệt'),
        ('Đơn Hàng', 'Món Ăn', 'Chứa'),
        ('Đơn Hàng', 'Giao Hàng', 'Có'),
        ('Đơn Hàng', 'Thanh Toán', 'Yêu cầu'),
        ('Món Ăn', 'Nhà Hàng', 'Thuộc về'),
        ('Món Ăn', 'Danh Mục', 'Phân loại'),
        ('Món Ăn', 'Đánh Giá', 'Nhận'),
        ('Giao Hàng', 'Địa Chỉ', 'Đến')
    ]
    
    # Thêm cạnh
    for source, target, label in relationships:
        G.add_edge(source, target, label=label)
    
    # Tạo figure
    plt.figure(figsize=(9, 7))
    
    # Định nghĩa màu node theo loại với màu đẹp hơn
    node_colors = {
        'role': '#e1bee7',      # tím nhạt cho vai trò người dùng
        'entity': '#90caf9'     # xanh dương nhạt cho thực thể
    }
    
    # Gán loại cho mỗi node
    node_type = {
        'Khách Hàng': 'role',
        'Shipper': 'role',
        'Chủ Nhà Hàng': 'role',
        'Quản Trị Viên': 'role',
        'Đơn Hàng': 'entity',
        'Món Ăn': 'entity',
        'Giao Hàng': 'entity',
        'Thanh Toán': 'entity',
        'Nhà Hàng': 'entity',
        'Địa Chỉ': 'entity',
        'Danh Mục': 'entity',
        'Đánh Giá': 'entity'
    }
    
    # Tạo bản đồ màu và kích thước node
    color_map = [node_colors[node_type[node]] for node in G.nodes()]
    node_size = [1200 if node_type[node] == 'role' else 900 for node in G.nodes()]
    
    # Vẽ mạng với viền rõ ràng
    nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=node_size,
            font_size=9, font_weight='bold', width=1.2, edge_color='gray',
            edgecolors='gray', linewidths=0.8)
    
    # Vẽ nhãn cạnh với nền trắng để dễ đọc
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, 
                                font_color='darkred', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
    
    # Tạo chú thích
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor=node_colors['role'], label='Vai Trò Người Dùng', edgecolor='gray'),
        plt.Rectangle((0, 0), 1, 1, facecolor=node_colors['entity'], label='Thực Thể Hệ Thống', edgecolor='gray')
    ]
    plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.05),
              ncol=2, fontsize=9)
    
    plt.title('Mối Quan Hệ Giữa Thực Thể', fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('Draw/entity_relationships.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("Đang tạo các biểu đồ Use Case cho FoodZone...")
    draw_use_case_diagram()
    draw_order_flow()
    draw_entity_relationships()
    print("Tất cả biểu đồ đã được tạo trong thư mục Draw.")