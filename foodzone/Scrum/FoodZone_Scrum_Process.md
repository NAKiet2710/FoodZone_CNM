# Quy Trình Làm Việc Scrum - Dự Án FoodZone

## Giới Thiệu

Tài liệu này mô tả quy trình làm việc Scrum được áp dụng cho dự án FoodZone - ứng dụng đặt đồ ăn và giao hàng trực tuyến.

## Vai Trò

1. **Product Owner**: Người chịu trách nhiệm xác định và ưu tiên các tính năng của sản phẩm
2. **Scrum Master**: Người đảm bảo quy trình Scrum được tuân thủ và loại bỏ các trở ngại
3. **Development Team**: Nhóm phát triển gồm các lập trình viên, designer, tester

## Các Sự Kiện Scrum

### 1. Sprint Planning
- Thời gian: Đầu mỗi Sprint (2 tuần/Sprint)
- Mục đích: Lên kế hoạch và chọn các task từ Product Backlog
- Thành phần tham gia: Toàn bộ Scrum team

### 2. Daily Scrum
- Thời gian: Mỗi ngày, không quá 15 phút
- Mục đích: Cập nhật tiến độ, chia sẻ vấn đề
- Thành phần tham gia: Development Team, Scrum Master

### 3. Sprint Review
- Thời gian: Cuối mỗi Sprint
- Mục đích: Demo kết quả đạt được
- Thành phần tham gia: Toàn bộ Scrum team, các bên liên quan

### 4. Sprint Retrospective
- Thời gian: Sau Sprint Review
- Mục đích: Đánh giá quy trình, cải thiện cho Sprint tiếp theo
- Thành phần tham gia: Toàn bộ Scrum team

## Product Backlog

Dựa trên mã nguồn FoodZone, Product Backlog được chia thành các epic sau:

### Epic 1: Hệ Thống Người Dùng
- Đăng ký tài khoản (Khách hàng, Shipper, Nhà hàng)
- Đăng nhập/Đăng xuất
- Quản lý thông tin cá nhân
- Phân quyền người dùng

### Epic 2: Quản Lý Món Ăn
- Thêm/sửa/xóa danh mục món ăn
- Thêm/sửa/xóa món ăn
- Quản lý hình ảnh món ăn
- Tìm kiếm món ăn

### Epic 3: Giỏ Hàng & Đặt Hàng
- Thêm món vào giỏ hàng
- Cập nhật số lượng
- Thanh toán đơn hàng
- Lưu lịch sử đơn hàng

### Epic 4: Giao Hàng & Theo Dõi
- Quản lý địa chỉ giao hàng
- Phân công shipper
- Cập nhật trạng thái đơn hàng
- Theo dõi đơn hàng theo thời gian thực

### Epic 5: Thanh Toán
- Tích hợp PayPal
- Thanh toán khi nhận hàng (COD)
- Lưu lịch sử thanh toán

### Epic 6: Chatbot & Hỗ Trợ
- Tích hợp Google AI
- Trả lời câu hỏi tự động
- Hỗ trợ khách hàng

## Sprint Planning

### Sprint 1 (2 tuần)
**Mục tiêu**: Thiết lập cơ sở dữ liệu và hệ thống người dùng

#### Tasks:
1. Thiết kế ERD và cơ sở dữ liệu
   - Người thực hiện: Backend Developer
   - Story Points: 13
   - Mô tả: Thiết kế mô hình quan hệ các bảng trong CSDL

2. Tạo models Django
   - Người thực hiện: Backend Developer
   - Story Points: 8
   - Mô tả: Implement các models trong models.py

3. Tạo hệ thống đăng ký/đăng nhập
   - Người thực hiện: Backend Developer
   - Story Points: 8
   - Mô tả: Implement views và forms cho chức năng đăng ký/đăng nhập

4. Thiết kế giao diện người dùng cơ bản
   - Người thực hiện: Frontend Developer
   - Story Points: 8
   - Mô tả: Tạo templates cho trang chủ, đăng ký, đăng nhập

### Sprint 2 (2 tuần)
**Mục tiêu**: Phát triển chức năng quản lý món ăn và danh mục

#### Tasks:
1. Xây dựng chức năng thêm/sửa/xóa danh mục
   - Người thực hiện: Backend Developer
   - Story Points: 5
   - Mô tả: Implement views và forms cho Category

2. Xây dựng chức năng thêm/sửa/xóa món ăn
   - Người thực hiện: Backend Developer
   - Story Points: 8
   - Mô tả: Implement views và forms cho Dish

3. Thiết kế giao diện hiển thị danh mục và món ăn
   - Người thực hiện: Frontend Developer
   - Story Points: 8
   - Mô tả: Tạo templates hiển thị danh sách món ăn và chi tiết

4. Xây dựng tính năng tìm kiếm
   - Người thực hiện: Full-stack Developer
   - Story Points: 5
   - Mô tả: Implement chức năng tìm kiếm món ăn

### Sprint 3 (2 tuần)
**Mục tiêu**: Phát triển chức năng giỏ hàng và đặt hàng

#### Tasks:
1. Xây dựng model Cart và CartItem
   - Người thực hiện: Backend Developer
   - Story Points: 5
   - Mô tả: Implement models cho giỏ hàng

2. Phát triển chức năng thêm/xóa/cập nhật giỏ hàng
   - Người thực hiện: Backend Developer
   - Story Points: 8
   - Mô tả: Implement views cho việc quản lý giỏ hàng

3. Thiết kế giao diện giỏ hàng
   - Người thực hiện: Frontend Developer
   - Story Points: 5
   - Mô tả: Tạo template hiển thị giỏ hàng

4. Xây dựng luồng đặt hàng
   - Người thực hiện: Backend Developer
   - Story Points: 13
   - Mô tả: Implement quy trình đặt hàng từ giỏ hàng

### Sprint 4 (2 tuần)
**Mục tiêu**: Phát triển chức năng thanh toán và giao hàng

#### Tasks:
1. Tích hợp PayPal
   - Người thực hiện: Backend Developer
   - Story Points: 13
   - Mô tả: Tích hợp PayPal Standard IPN

2. Xây dựng luồng thanh toán khi nhận hàng (COD)
   - Người thực hiện: Backend Developer
   - Story Points: 8
   - Mô tả: Implement quy trình thanh toán COD

3. Phát triển chức năng quản lý địa chỉ giao hàng
   - Người thực hiện: Backend Developer
   - Story Points: 5
   - Mô tả: Implement views để quản lý địa chỉ giao hàng

4. Thiết kế giao diện thanh toán
   - Người thực hiện: Frontend Developer
   - Story Points: 8
   - Mô tả: Tạo templates cho trang thanh toán

### Sprint 5 (2 tuần)
**Mục tiêu**: Phát triển chức năng theo dõi đơn hàng và shipper

#### Tasks:
1. Xây dựng chức năng phân công shipper
   - Người thực hiện: Backend Developer
   - Story Points: 8
   - Mô tả: Implement logic phân công shipper

2. Phát triển chức năng cập nhật trạng thái đơn hàng
   - Người thực hiện: Backend Developer
   - Story Points: 8
   - Mô tả: Implement views cập nhật trạng thái giao hàng

3. Thiết kế giao diện theo dõi đơn hàng
   - Người thực hiện: Frontend Developer
   - Story Points: 8
   - Mô tả: Tạo template hiển thị thông tin theo dõi

4. Xây dựng dashboard cho shipper
   - Người thực hiện: Full-stack Developer
   - Story Points: 13
   - Mô tả: Tạo dashboard để shipper quản lý đơn hàng

### Sprint 6 (2 tuần)
**Mục tiêu**: Phát triển chatbot và hoàn thiện sản phẩm

#### Tasks:
1. Tích hợp Google AI
   - Người thực hiện: Backend Developer
   - Story Points: 13
   - Mô tả: Tích hợp Google AI cho chatbot

2. Xây dựng giao diện chatbot
   - Người thực hiện: Frontend Developer
   - Story Points: 8
   - Mô tả: Thiết kế UI cho chatbot

3. Testing và sửa lỗi
   - Người thực hiện: Tester
   - Story Points: 13
   - Mô tả: Kiểm thử toàn bộ hệ thống

4. Triển khai lên môi trường production
   - Người thực hiện: DevOps
   - Story Points: 8
   - Mô tả: Cấu hình và triển khai hệ thống

## Definition of Done

Một task được coi là hoàn thành khi:

1. Code đã được implement theo yêu cầu
2. Code đã được review bởi ít nhất 1 thành viên khác
3. Đã pass tất cả các unit tests
4. Đã được test trên môi trường dev
5. Documentation đã được cập nhật

## Công Cụ Sử Dụng

1. **Jira**: Quản lý Scrum board và task
2. **GitHub**: Quản lý mã nguồn và version control
3. **Discord/Slack**: Giao tiếp giữa các thành viên
4. **Google Drive**: Lưu trữ tài liệu dự án 