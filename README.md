# End-to-End Automated License Plate Recognition

**Two-Stage Detection & Sequence OCR — kế hoạch `alpr-plan-v1`, ngày 08/11/2026.**

Pipeline MVP: ảnh pixel → **YOLOv8n** phát hiện biển số → crop/preprocess →
**CRNN (CNN + BiLSTM + CTC Loss)** → greedy CTC decoding → chuỗi biển số và trạng thái.
“End-to-end” là luồng suy luận hai giai đoạn hoàn chỉnh; hai mạng được huấn luyện riêng.
Hai metric chính là **CER micro** và **End-to-End Accuracy trên toàn bộ ảnh**.

## Trạng thái thực tế

Đã tạo bộ kế hoạch tiếng Việt, schema, config/template, Protocol Python và công cụ kiểm tra/xuất PDF.
Chưa triển khai parser, detector, CRNN, evaluator, CLI inference hoặc demo.
Chưa tải CCPD/checkpoint, chưa huấn luyện, chưa có kết quả mô hình; tất cả số đo là **CHƯA ĐO / null**.
Thư mục triển khai có README chỉ mô tả đầu ra dự kiến; chưa phải module ALPR chạy được.

## Đọc và giao việc

1. [Mục lục kế hoạch](docs/plan/README.md) và [tổng quan](docs/plan/00-project-overview.md).
2. [Gate G1–G4](docs/plan/05-weekly-goals-and-benchmarks.md): benchmark là cam kết nghiệm thu;
   lịch/task chỉ là gợi ý. Không nghiệm thu bằng việc tick backlog.
3. [Hợp đồng và bàn giao](docs/plan/06-data-contract-and-handoffs.md),
   [JSON Schema](docs/plan/data-contract.json), [kiến trúc CRNN/CTC](docs/plan/08-architecture-and-interfaces.md).
4. [Dataset và chống rò rỉ](docs/plan/07-dataset-and-evaluation-protocol.md),
   [tài nguyên/rủi ro](docs/plan/09-resources-and-risks.md), [lệnh và trạng thái](docs/plan/10-reproduction-and-status.md).

[PDF kế hoạch tổng hợp — 38 trang](reports/plan/ALPR-Implementation-Plan.pdf) đã được xuất;
[biên bản kiểm tra](docs/plan/validation-report.md) ghi rõ phạm vi đã xác minh.

| Tuần | Chủ sở hữu | Bàn giao chính | Giờ công |
| --- | --- | --- | --- |
| 1 | A | Parser, split, crop, charset, QA, evaluator metric dùng chung | 34 + 6 dự phòng |
| 2 | B | YOLO baseline, detect(), predicted dev crops, detector manifest | 34 + 6 dự phòng |
| 3 | C | CRNN + greedy CTC, recognize(), predict(), pipeline gọi được và freeze | 34 + 6 dự phòng |
| 4 | D | Demo ảnh đơn/batch, test cuối, phân tích lỗi, báo cáo, release | 34 + 6 dự phòng |

Chưa ấn định ngày bắt đầu. Hai giờ kiểm nhận đầu tuần nằm trong ngân sách của người nhận.
D nhận pipeline đã ghép từ C. Không mặc định người trước hỗ trợ ngoài tuần của mình.

## Công cụ chạy ngay

Chạy tại root repo, Python >=3.11 cho công cụ tài liệu (đã kiểm với Python 3.14).
Môi trường huấn luyện dự kiến dùng Python 3.11 riêng; chưa xác minh dependency training.

```powershell
python -m pip install -r requirements-docs.txt
python scripts/validate_plan.py
python docs/plan/build_plan.py --check
python docs/plan/build_plan.py
```

Lệnh cuối tạo PDF thật khi có ReportLab và font Unicode; xem [hướng dẫn tái lập](docs/plan/10-reproduction-and-status.md).
Các lệnh `python -m alpr.cli ...` trong kế hoạch **chỉ là giao diện dự kiến, chưa chạy được**.

## Cấu trúc

```text
docs/plan/       kế hoạch, gate, hợp đồng, config và template
src/alpr/       Protocol + vùng data/detection/recognition/pipeline/evaluation dự kiến
configs/        chỉ dẫn cấu hình runtime; mẫu chuẩn ở docs/plan/config/
scripts/        validator bộ kế hoạch đã triển khai
tests/          đặc tả ca kiểm thử cần triển khai
data/           raw, processed, splits, crops; chưa có dữ liệu
evaluation/     nhãn/evaluator tách khỏi runtime
manifests/      manifest thật sẽ được tạo sau; hiện chỉ README
handoff/        biên bản bàn giao thật theo tuần
reports/        QA, báo cáo và PDF kế hoạch
demo/           ứng dụng ảnh đơn/batch dự kiến
artifacts/      checkpoint dự kiến, bị Git bỏ qua
```

Nguồn chính thức: [CCPD](https://github.com/detectRecog/CCPD),
[YOLOv8](https://docs.ultralytics.com/models/yolov8/),
[CRNN](https://arxiv.org/abs/1507.05717).
MVP chọn CCPD2019 Base với custom split theo nhóm biển số; không tự nhận tương đương benchmark chính thức.
Không commit dataset/checkpoint. [Nhật ký quyết định](docs/plan/decision-log.md) ghi các giả định trước khi xem test.
