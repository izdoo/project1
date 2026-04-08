# Project Period Report (Weekly / Monthly)

## 1) Giới thiệu

`project_period_report` là module báo cáo định kỳ theo dự án (tuần/tháng), hỗ trợ:
- Ghi nhận kết quả thực hiện.
- Lập kế hoạch kỳ tiếp theo.
- Theo dõi tiến độ, issue, risk.
- Xuất PDF để gửi nội bộ/khách hàng.

Module phù hợp cho đội PM, BA, Dev Lead, và quản lý dự án cần báo cáo chuẩn hóa theo chu kỳ.

## 2) Chức năng chính

- Quản lý báo cáo theo:
  - Dự án
  - Kỳ báo cáo (`Week` / `Month`)
  - Khoảng ngày (`date_from` -> `date_to`)
- Tab **Kết quả tuần này**:
  - KPI: `% completion`, `Bug count`, `Task count`, `Man-day`
  - 3 section:
    - `Task hoàn thành`
    - `Task đang thực hiện`
    - `Task bị chen thêm`
- Nút **Load completed tasks**:
  - Tải nhanh task đã đóng trong kỳ vào section `Task hoàn thành`.
- Tab **Next period plan** + nút **Load next period plan**:
  - Tự lấy task đang dở từ kỳ trước (carry-over).
  - Tự lấy task đến hạn trong tuần kế tiếp.
- Tab bổ sung:
  - `Progress by area`
  - `Issues`
  - `Risks`
  - `Others`
- Nút **Print PDF**:
  - Xuất báo cáo PDF theo template chuẩn.

## 3) Hướng dẫn sử dụng

### Bước 1: Tạo báo cáo kỳ

- Vào **Project -> Reports -> Period Reports**.
- Tạo mới:
  - Chọn `Project`
  - Chọn `Period type`
  - Chọn `Date from` / `Date to`

### Bước 2: Điền kết quả kỳ hiện tại

- Mở tab **Kết quả tuần này**:
  - Điền KPI tổng quan.
  - Bấm **Load completed tasks** để nạp task hoàn thành.
  - Bổ sung/chỉnh sửa các dòng ở 3 section theo thực tế.

### Bước 3: Lập kế hoạch kỳ tới

- Mở tab **Next period plan**.
- Bấm **Load next period plan** để nạp:
  - Task carry-over từ kỳ trước.
  - Task có hạn trong tuần kế tiếp.
- Chỉnh sửa nội dung kế hoạch cuối cùng theo ưu tiên triển khai.

### Bước 4: Cập nhật rủi ro/vấn đề

- Tab `Progress by area`, `Issues`, `Risks`, `Others`:
  - PM/Lead nhập nội dung đánh giá, nguyên nhân, tác động, hành động xử lý.

### Bước 5: Xuất báo cáo

- Bấm **Print PDF** để xuất file gửi stakeholder.

## 4) Quy ước dữ liệu khuyến nghị

- `% completion`: tỷ lệ hoàn thành kỳ hiện tại ở cấp dự án/phase.
- `Bug count`: số bug phát sinh hoặc tồn trong kỳ (theo quy ước team).
- `Task count`: tổng task đã xử lý trong kỳ.
- `Man-day`: tổng nỗ lực nhân sự quy đổi ngày công.

## 5) Lưu ý vận hành

- `Load completed tasks` dựa trên task đóng (`stage fold = true`) và `write_date` trong khoảng kỳ.
- `Load next period plan` thay thế danh sách kế hoạch auto hiện tại bằng dữ liệu mới tạo.
- Nên thống nhất định nghĩa KPI với PMO trước khi báo cáo chính thức.

## 6) Phụ thuộc

- `project`
- `web`

## 7) Khuyến nghị triển khai

- Dùng mẫu báo cáo thống nhất theo phòng PM.
- Chốt checklist review trước khi bấm `Print PDF`.
- Lưu báo cáo theo tuần/tháng để phục vụ retrospective và audit tiến độ.
