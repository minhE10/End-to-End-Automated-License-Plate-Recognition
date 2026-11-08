# Nhật ký quyết định

Các quyết định dưới là **thiết kế ban đầu**, ngày 08/11/2026; không là kết quả pilot.
Chưa có ngày khởi động cụ thể. A/B/C/D là vai trò dự kiến, chưa có chữ ký nghiệm thu.

| ID | Quyết định | Lý do | Trạng thái / thời điểm xem lại |
| --- | --- | --- | --- |
| DEC01 | CCPD2019 Base, custom group split seed42; target20k/2k/2k, min5k/500/500 | Vừa ngân sách, giảm text memorization | Đề xuất; A pin inventory/hash trước G1 |
| DEC02 | YOLOv8n / ultralytics8.3.0, image640, train riêng | Baseline nhỏ, giảm số nhánh thử | Đề xuất; B smoke dependency/GPU trước train |
| DEC03 | CRNN-small CNN stride4 +BiLSTM2x128 +CTC, input32x160/T40/head68 | Đáp ứng đề, dễ kiểm alignment | Đề xuất; C kiểm shape và finite backward |
| DEC04 | Crop chữ nhật, greedy CTC, không GT warp trong runtime | Deployment chỉ có pixel | Baseline; sửa phải version/config và dev evidence |
| DEC05 | A làm metric/fixture, B giao adapter/crop, C giao predict() thật | Giảm overload C và tránh D ghép core | Ràng buộc bàn giao |
| DEC06 | Quality thresholds provisional, integrity bắt buộc | Chưa có GPU hoặc internal baseline | B/C pilot dev rồi freeze; chưa từng xem test model |
| DEC07 | Preprocessing ablation duy nhất CLAHE so baseline | Vừa budget hai cấu hình | Chọn trên dev; D chỉ đo final frozen variants |
| DEC08 | Giữ test cố định khi giảm train scope | Tránh đổi test theo kết quả | Chỉ sửa test lỗi nguồn trước exposure, có protocol version mới |

## Template quyết định tiếp theo

- ID, ngày, tác giả/chủ sở hữu/người nhận:
- Đổi gì: data/split/config/architecture/threshold/protocol version cũ → mới:
- Bằng chứng dev/pilot, hashes, denominator, resource logs:
- Tác động công sức/GPU/disk và API/bàn giao:
- Test đã được ai xem, xem gì, khi nào; xác nhận trước test exposure nếu là tuning:
- Kết luận và freeze timestamp/hash; ngưỡng nào trở thành cam kết:
- Nếu sửa correctness sau test: error exposure, mọi run cần chạy lại, giới hạn kết luận:

Không được hạ ngưỡng sau khi biết test thấp, đổi tên split để giấu exposure hoặc điền observed=0 khi chưa chạy.
