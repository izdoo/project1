# Project Task Stage -> Done % (Gantt)

## 1) Giới thiệu

`project_stage_done_percent` là module mở rộng cho Project + Bryntum Gantt, cho phép cấu hình phần trăm hoàn thành (`Done %`) theo từng giai đoạn (stage) của task.

Mục tiêu:
- Chuẩn hóa cách cập nhật `Done %` khi task chuyển trạng thái.
- Đồng bộ nhất quán giữa backend Odoo và Gantt.
- Giảm thao tác cập nhật thủ công.

## 2) Chức năng chính

- Thêm trường cấu hình trên stage task: **Done % when task is completed (this stage)**.
- Giá trị cho phép: `0..100`.
- Khi task ở trạng thái **Hoàn tất** (`state = 1_done`), hệ thống tự đồng bộ `percent_done` theo stage hiện tại.
- Khi người dùng sửa tay `percent_done` trong cùng thao tác, hệ thống ưu tiên giá trị người dùng nhập.

## 3) Luồng hoạt động

1. Quản trị dự án cấu hình từng stage:
   - Ví dụ:
     - `Plan` = 0
     - `Workshop` = 30
     - `Review` = 80
     - `Release/Done` = 100
2. Khi task chuyển sang trạng thái Hoàn tất:
   - `Done %` tự cập nhật theo cấu hình stage.
3. Gantt và form task hiển thị cùng một giá trị `Done %`.

## 4) Hướng dẫn sử dụng

### Bước 1: Cấu hình stage

- Vào **Project -> Configuration -> Task Stages**.
- Mở từng stage cần dùng.
- Điền trường **Done % when task is completed (this stage)**.

### Bước 2: Vận hành task

- Cập nhật tiến độ trong quá trình làm việc như bình thường.
- Khi task hoàn tất (state Done), kiểm tra cột `Done %` đã tự đồng bộ.

### Bước 3: Kiểm tra trên Gantt

- Mở **Gantt View Pro**.
- Đảm bảo `Done %` hiển thị đúng theo stage/logic đã cấu hình.

## 5) Lưu ý vận hành

- Module chỉ tự đồng bộ khi task ở trạng thái **Done**.
- Nếu doanh nghiệp dùng quy tắc tiến độ đặc thù (theo timesheet, weighted progress), cần thống nhất chính sách trước khi áp dụng hàng loạt.
- Nếu không muốn tự đồng bộ ở stage nào, để trống hoặc đặt giá trị phù hợp chính sách PMO.

## 6) Phụ thuộc

- `project`
- `bryntum_gantt`

## 7) Khuyến nghị triển khai

- Thiết lập chuẩn stage/progress theo PMO trước khi training người dùng.
- Chạy thử trên 1 project pilot, sau đó áp dụng toàn bộ.
