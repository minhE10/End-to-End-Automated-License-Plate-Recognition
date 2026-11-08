# Tài nguyên, ngân sách và sổ rủi ro

## Quan sát môi trường ngày 08/11/2026

Python3.14.3; os.cpu_count()=8 logical CPU; ổ F còn khoảng **25,55 GiB** tại thời điểm khảo sát.
Windows CIM CPU/RAM/GPU bị Access denied; không tìm thấy nvidia-smi trong PATH.
Chưa xác minh model CPU, RAM, GPU, VRAM hoặc CUDA. Không suy ra máy không có GPU từ việc thiếu nvidia-smi.
PyYAML6.0.3, jsonschema4.26.0, ReportLab5.0.1 và font Arial có sẵn; không có pandoc/xelatex trong PATH.
Python3.14 chỉ dùng kiểm tài liệu; tạo môi trường training Python3.11 sau, chưa cài torch.

## Ba loại thời gian tách biệt

| Loại | Ngân sách/ước lượng ban đầu | Cách xác minh |
| --- | --- | --- |
| Giờ công | 4 người x40h =160h; 136 thực hiện +24 reserve | Backlog tổng 34+6 mỗi người; chờ GPU không tính thành giờ thao tác |
| Tải dữ liệu | Chưa biết, phụ thuộc archive thật/băng thông; ví dụ 10GB ở10MB/s lý tưởng ~17 phút, không là ETA cam kết | A đo size/bandwidth/retry; cấp slot tải riêng ngoài giờ công active |
| GPU detector | Pilot <=0,5h tham khảo; full subset trần12 GPU giờ, nằm trong tuần B | Đo seconds/epoch trên pilot và ngoại suy theo ảnh/epochs, margin x1.5 |
| GPU CRNN | Pilot <=0,5h tham khảo; full subset +1 ablation trần16 GPU giờ, nằm trong tuần C | Đo throughput thực tế/VRAM rồi chốt số epoch; không hứa hội tụ trước pilot |

Giả định tham khảo: một GPU CUDA VRAM>=8GB, RAM>=16GB, disk ngoại vi/remote nếu full archive không vừa.
Các con số GPU là giới hạn chi phí đề xuất, không là benchmark đã chạy hoặc dự báo chính xác.
Download và training chạy nền phải hoàn thành trong cửa sổ tuần tương ứng; nếu dự báo quá tuần thì giảm scope hoặc đổi lịch.
Mỗi người giữ 6h reserve cho lỗi nguồn/tensor/integration; không phân reserve cho video hay production API.

## Pilot và giảm phạm vi

1. A kiểm archive size + extracted subset + crop + checkpoints + workspace overhead trước tải.
   Giữ >=8GiB headroom; với disk hiện tại, chặn tải nếu dự kiến working set vượt ~17GiB.
   Chưa biết kích thước archive thì không mặc định đủ. Không tải CCPD toàn bộ trong bước lập kế hoạch.
2. Thu subset Base qua nguồn chính thức nếu có lựa chọn; nếu archive bắt buộc tải cả, dùng volume ngoài/compute workspace
   được cấp và chuyển subset có provenance. Không tự giả định hỗ trợ HTTP range extraction.
3. Freeze split group trước, pilot 1k/200 từ train/dev. Đo parse time, batch memory và epoch time;
   image decode/crop on-demand thay cache toàn crop khi disk chật. Raw không bao giờ bị xóa trước xác minh bản nguồn an toàn.
4. Nếu target20k không vừa: dùng minimum5k/500/500, batch giảm theo VRAM, early-stop và số epoch giới hạn.
   B/C chỉ tối đa2 cấu hình; không sweep. Thời gian ablation nằm trong cùng budget.
5. CPU-only: parser/evaluator/smoke chạy được; xin slot GPU/đổi lịch là blocker training thật.
   Không cam kết đạt quality trên CPU hoặc thay CRNN bằng OCR bên ngoài. Giữ status CHƯA ĐẠT nếu thiếu compute.
6. Cắt extension theo thứ tự: video/API/tracking → beam/rectification → subset khó/Green.
   Baseline YOLO+CRNN+CTC, full-split metric và anti-leak không được cắt. Ablation bắt buộc thiếu phải ghi fail, không giả hoàn thành.

## Risk register

| ID | Rủi ro / tín hiệu | Chủ sở hữu | Xử lý / điều kiện chặn |
| --- | --- | --- | --- |
| R01 | Disk <working set+8GiB | A | Subset/on-demand hoặc volume ngoài; dừng tải lớn chưa đủ chỗ |
| R02 | Không có GPU/wheel Python | B | Python3.11 env riêng, smoke torch/CUDA; chỉ CPU smoke và báo blocker training |
| R03 | Sai mapping/sentinel/corners | A | QA100+fixtures, quarantine; G1 fail khi còn mơ hồ |
| R04 | Text/near-duplicate overlap | A | Union groups trước split; overlap>0 chặn G1 |
| R05 | Filename leakage | C | Pixel-only API, rename test và module isolation; bất kỳ lệ thuộc nhãn chặn G3 |
| R06 | CNN timestep/CTC collapse sai | C | Shape/repeat/length tests, overfit32 train; không dùng zero_infinity che lỗi |
| R07 | Predicted crop giảm OCR | B/C | Báo GT vs pred/coverage; dev-only preprocessing; giữ E2E đủ mẫu số |
| R08 | Tuần C quá tải | B/C | A viết metrics/fixtures, B giao adapter/pred crops; ghép predict từ đầu C; cắt extensions |
| R09 | Test bị dùng tuning | D | Exposure log + freeze hashes; nếu lộ ghi hạn chế, không gọi held-out chưa xem |
| R10 | Người giao hết tuần, artifact lỗi | Người nhận | Từ chối gate, reserve/đổi lịch rõ; không giả định hỗ trợ ngoài quỹ |
| R11 | Model/license không phân phối được | B/D | Ghi nguồn/license trước tải/đóng gói; cung cấp script lấy artifact thay commit dữ liệu lớn |
| R12 | Ngưỡng pilot thiếu cơ sở | B/C | Hiệu chỉnh từ dev có decision trước test; không đưa paper score thành cam kết |

Risk register hiện là rủi ro dự kiến; chưa có log training hoặc measured throughput.
