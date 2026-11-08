# Mục lục kế hoạch ALPR

Phiên bản `alpr-plan-v1` / `alpr-contract-v1` / `alpr-custom-base-group-v1`.
**Đây là kế hoạch, chưa phải dữ liệu hay mô hình đã nghiệm thu.**

| Tài liệu | Người đọc | Mục đích |
| --- | --- | --- |
| [00 Tổng quan](00-project-overview.md) | Cả nhóm | MVP, nguồn tham khảo, ownership, đường găng |
| [01 Tuần 1 A](01-week-1-a-data-readiness.md) | A, B | Dữ liệu, split, crop, QA và metric |
| [02 Tuần 2 B](02-week-2-b-plate-detection.md) | B, C | Detector baseline, dev và bàn giao |
| [03 Tuần 3 C](03-week-3-c-sequence-recognition.md) | C, D | CRNN + CTC và pipeline tích hợp |
| [04 Tuần 4 D](04-week-4-d-demo-and-evaluation.md) | D | Demo, test, báo cáo, release |
| [05 Gate và metric](05-weekly-goals-and-benchmarks.md) | Cả nhóm | Định nghĩa, mẫu số, ngưỡng, bằng chứng |
| [06 Hợp đồng](06-data-contract-and-handoffs.md) | Cả nhóm | Field, invariant và A → B → C → D |
| [07 Dataset/protocol](07-dataset-and-evaluation-protocol.md) | A, D | Parser và chống rò rỉ |
| [08 Kiến trúc/API](08-architecture-and-interfaces.md) | B, C | Shape, CTC, checkpoint, lỗi runtime |
| [09 Tài nguyên/rủi ro](09-resources-and-risks.md) | Cả nhóm | Pilot, fallback, thời gian GPU/tải |
| [10 Tái lập/trạng thái](10-reproduction-and-status.md) | Cả nhóm | Lệnh hiện có và lệnh dự kiến |
| [Decision log](decision-log.md) | Cả nhóm | Freeze, đổi protocol trước test |
| [Nguồn tham khảo](sources-and-reference-review.md) | Cả nhóm | Provenance repo mẫu và nguồn chính thức |

Dữ liệu máy đọc: [weekly-benchmarks.json](weekly-benchmarks.json), [data-contract.json](data-contract.json).
[PDF tổng hợp 38 trang](../../reports/plan/ALPR-Implementation-Plan.pdf) gồm các tài liệu kế hoạch;
[biên bản kiểm tra](validation-report.md) ghi lại các lệnh đã chạy.
[Mẫu số đo](benchmark-results-template.csv) dùng null và CHƯA ĐO;
[backlog](recommended-backlog.csv) và [config mẫu](config/recommended-implementation.example.yaml) là gợi ý.
[Template bàn giao](templates/handoff-template.md), [source manifest](templates/source-manifest.example.json),
[run manifest](templates/run-manifest.example.json), [model manifest](templates/model-manifest.example.json),
[release manifest](templates/release-manifest.example.json), [mẫu thực nghiệm](templates/experiment-results-template.csv).
[Data manifest](templates/data-manifest.example.json) và [charset thiết kế](templates/charset.example.json) bổ sung cho hợp đồng.

Tổng 160 giờ công: 136 thực hiện + 24 dự phòng. Không có lịch bắt đầu cụ thể.
Gate toàn vẹn bắt buộc; ngưỡng chất lượng ban đầu là đề xuất có độ tin cậy thấp, phải pilot dev và freeze trước test.
Không được biến một ngưỡng đã trượt thành đạt bằng cách sửa bảng kết quả hoặc đổi mẫu số.
