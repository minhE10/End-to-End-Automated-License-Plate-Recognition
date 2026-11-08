# Tái lập và phân biệt trạng thái

## Lệnh hiện có

Chạy từ root repository:

```powershell
python -m pip install -r requirements-docs.txt
python scripts/validate_plan.py
python docs/plan/build_plan.py --check
python docs/plan/build_plan.py
```

Install command là hướng dẫn khi máy thiếu dependency; môi trường lập kế hoạch đã có sẵn nên không cài lại.
Validator kiểm link Markdown local, JSON strict, JSON Schema và manifest/charset templates,
YAML, CSV, benchmark table/JSON/template, versions/ownership/budget và null chưa đo.
Validator **không kiểm ảnh thật, chống rò dataset thật hoặc chất lượng mô hình**.
Build --check kiểm dependency/font/docs; build tạo `reports/plan/ALPR-Implementation-Plan.pdf` thật,
gồm README plan và 00–11, decision log, nguồn; in số trang/hash/kích thước sau khi tạo.
Arial cho tiếng Việt, STSong-Light cho ký tự CJK; nếu máy thiếu font/dependency thì script fail rõ và giữ Markdown đầy đủ,
không ghi PDF rỗng. Có thể dùng `--output` để chọn đường dẫn.

## Giao diện lệnh tương lai — CHƯA TRIỂN KHAI

Không copy chạy các lệnh dưới ở skeleton này. Tên CLI là đề xuất, chủ sở hữu có thể đổi
nhưng phải cập nhật command registry/biên bản và giữ input/output tương đương.

```powershell
python -m alpr.cli prepare-data --config configs/frozen.yaml
python -m alpr.cli train-detector --config configs/frozen.yaml
python -m alpr.cli evaluate --mode detection --split dev --config configs/frozen.yaml
python -m alpr.cli export-crops --kind predicted --split dev --config configs/frozen.yaml
python -m alpr.cli train-recognizer --config configs/frozen.yaml
python -m alpr.cli evaluate --mode ocr_gt_bbox --split dev --config configs/frozen.yaml
python -m alpr.cli evaluate --mode ocr_pred_matched --split dev --config configs/frozen.yaml
python -m alpr.cli evaluate --mode pipeline_all --split test --config configs/frozen.yaml
python -m alpr.cli predict --image data/processed/images/opaque-id.jpg --config configs/frozen.yaml
python -m alpr.cli latency --split dev --config configs/frozen.yaml
python -m alpr.cli verify-gate --gate G3 --config configs/frozen.yaml
```

Future train commands chỉ dùng train/dev; test evaluate chỉ sau C freeze và D kiểm nhận.
Future config `configs/frozen.yaml` và runtime data/model path chưa tồn tại vì chưa có run thật.
Copy config example sau pilot, điền hash đã đo; không dùng null template làm release thực thi.
Mỗi verify-gate phải có dispatch cho mọi benchmark ID trong JSON hoặc cung cấp lệnh thay thế đã chạy thật.
`PYTHONPATH=src` hoặc editable install dùng cho triển khai sau; hiện chưa có alpr.cli.

## Bảng trạng thái ban đầu

| Thành phần | Hiện trạng | Evidence |
| --- | --- | --- |
| Kế hoạch/schema/config/templates | ĐÃ TẠO | Các file trong docs/plan |
| Protocol Python | ĐÃ TẠO, chỉ interface | src/alpr/interfaces.py |
| Validator/PDF builder | ĐÃ TRIỂN KHAI | scripts/validate_plan.py; docs/plan/build_plan.py |
| Parser/split/crop/charset dataset release | CHƯA TRIỂN KHAI | Không có artifact thật |
| YOLO detector/CRNN/training | CHƯA TRIỂN KHAI | Checkpoint null |
| Pipeline/evaluator/demo | CHƯA TRIỂN KHAI | Không có prediction hay report mô hình |
| CER/E2E/P-R/mAP/latency | CHƯA ĐO | Template null |

Lịch sử lệnh thực sự đã chạy và kết quả kiểm tài liệu nằm ở [biên bản kiểm tra](validation-report.md).
PDF là bản kế hoạch, không chứng minh huấn luyện hay gate model đã đạt.
