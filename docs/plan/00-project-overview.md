# Tổng quan dự án và trách nhiệm

## Kết quả cần giao

Ảnh xe chứa một biển số → YOLOv8n → bbox → crop chữ nhật → grayscale/resize/padding →
CNN → BiLSTM → logits → greedy CTC → biển số UTF-8 và trạng thái.
Huấn luyện detector và recognizer riêng. Không thay CRNN bằng dịch vụ OCR.
MVP demo ảnh đơn/batch. Video, tracking, camera, API production, beam search và rectification nằm ngoài đường găng.

G1 có dữ liệu đủ tin cậy; G2 có detector nạp lại được; G3 có pipeline gọi được;
G4 có demo và test cuối tái lập. [Gate chi tiết](05-weekly-goals-and-benchmarks.md) là chuẩn nghiệm thu.
Tất cả mô hình và chất lượng hiện CHƯA ĐO.

## Phân công nối tiếp

| Người | Tuần | Sở hữu đầu ra | Người nhận |
| --- | --- | --- | --- |
| A | 1 | Nguồn, parser, split, crops, charset, metric edit distance/IoU/exact, bộ test fixtures | B; C/D dùng tiếp |
| B | 2 | YOLO baseline, adapter detect(), export predicted dev crops, scorer detection, môi trường GPU đã khóa | C |
| C | 3 | CNN + BiLSTM + CTC, recognize(), predict(), evaluator tích hợp, frozen release candidate | D |
| D | 4 | UI/CLI demo, evaluator test cuối, latency, phân tích lỗi, báo cáo, gói phát hành | Người chấm |

A làm trước metric chung và input preprocessing có fixture để giảm tải tuần C; B giao adapter và predicted dev crops
để C không viết lại detector. C ghép luồng suy luận ngay ngày 1–2 bằng adapter thật và CRNN chưa huấn luyện chỉ để
kiểm shape; không công bố output này như kết quả. D nhận pipeline đã chạy với checkpoint thật sau G3.
D không được giao nhiệm vụ viết CRNN hoặc ghép các module cốt lõi.

Mỗi tuần 34 giờ thực hiện + 6 dự phòng. Hai giờ đầu B/C/D kiểm nhận trong quỹ 34 giờ.
Nếu đầu vào không hợp lệ: lập biên bản từ chối, ưu tiên dự phòng/giảm phần mở rộng, điều chỉnh lịch công khai.
Không mặc định gọi người trước quay lại miễn phí; gate thiếu artifact phải giữ trạng thái CHƯA ĐẠT.

## Dữ liệu và phép đo

MVP CCPD2019 `ccpd_base`, biển 7 ký tự. Custom split theo nhóm chuỗi biển số và cụm ảnh trùng,
seed 42, mục tiêu 20.000/2.000/2.000 train/dev/test; tối thiểu 5.000/500/500.
Pilot riêng 1.000 train + 200 dev lấy từ train/dev đã khóa; không tạo test pilot.
Nếu thiếu nhóm để đạt quy mô tối thiểu phải báo blocker, không cho phép overlap.
Các subset khó và CCPD-Green 8 ký tự chỉ mở rộng khi đủ thời gian/GPU.
Chi tiết trong [protocol](07-dataset-and-evaluation-protocol.md).

Ba chế độ đánh giá độc lập: OCR trên GT bbox crop (không warp), OCR trên predicted crop có điều kiện,
pipeline toàn ảnh. Không gộp oracle GT corners vào end-to-end thực tế.
Dev dùng chọn confidence/NMS/preprocessing/epoch; test chỉ do D mở sau freeze.

## Cách làm việc

Task, lịch ngày, framework và CLI đề xuất được thay bằng decision log nếu vẫn đáp ứng đề và hợp đồng.
YOLO + CNN/BiLSTM/CTC và định nghĩa CER/E2E bắt buộc giữ.
Mọi release giữ hash nguồn/split/config/charset/checkpoint, log và lệnh tái lập.
Backlog hoàn tất không thay cho số đo, mẫu số hay bằng chứng.
Repo mẫu chỉ cung cấp tổ chức tài liệu và cơ chế bàn giao; không sao chép dữ liệu/metric tìm kiếm.
