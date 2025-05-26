# Hướng dẫn fix lỗi font tiếng Việt trong file CSV

## Cách 1: Mở file CSV trong Excel đúng cách

1. Mở Excel trước (không trực tiếp mở file CSV)
2. Chọn tab Data (Dữ liệu) > From Text/CSV (Từ văn bản/CSV)
3. Tìm và chọn file FoodZone_Sprint_Backlog.csv
4. Trong cửa sổ import, chọn:
   - File Origin: 65001 (UTF-8)
   - Delimiter: Comma (Dấu phẩy)
5. Nhấn Load (Tải)
6. Lưu lại dưới dạng file Excel (.xlsx)

## Cách 2: Sử dụng Google Sheets

1. Mở Google Sheets
2. File > Import > Upload
3. Chọn file FoodZone_Sprint_Backlog.csv
4. Chọn "Import"
5. Xuất ra định dạng Excel (.xlsx) nếu cần

## Cách 3: Sử dụng Notepad++ để chuyển đổi encoding

1. Mở file CSV bằng Notepad++
2. Chọn Encoding > Convert to UTF-8-BOM
3. Lưu lại file
4. Mở lại trong Excel

## Cách 4: Sử dụng file Excel đã tạo sẵn

Trong thư mục này đã có file Excel với dữ liệu đúng:
- FoodZone_Sprint_Backlog.xlsx - File Excel đã được tạo sẵn với nội dung giống CSV nhưng không bị lỗi font 