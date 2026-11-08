# Biên bản kiểm tra bộ kế hoạch

Ngày kiểm tra: **08/11/2026**, múi giờ người dùng Asia/Jakarta.
Phạm vi: repository khởi đầu và kế hoạch. **Mọi benchmark mô hình vẫn CHƯA ĐO/null.**

## Những gì đã tạo

- README, bộ tài liệu tuần 1–4 và các đặc tả tổng quan/gate/dữ liệu/CTC/API/tài nguyên/tái lập/test.
- 25 benchmark G1–G4 có formula/denominator/threshold/rationale/owner/evidence/command dự kiến;
  tất cả observed, observed_n là null.
- JSON Schema Draft2020-12, 6 template có thể kiểm schema; config YAML và 3 CSV hợp lệ.
- Protocol/dataclass Python, thư mục triển khai có ghi CHƯA TRIỂN KHAI, .gitignore và dependency tài liệu.
- Validator thực thi và PDF builder thực thi; [PDF tổng hợp](../../reports/plan/ALPR-Implementation-Plan.pdf)
  có 38 trang, văn bản tiếng Việt và ký tự CJK. PDF chứa kế hoạch, không là báo cáo kết quả model.
- Tại thời điểm hoàn tất bước lập kế hoạch ban đầu: Git local nhánh main, chưa tạo commit, remote hoặc push.

## Lệnh đã chạy thành công

```powershell
python -X utf8 scripts/validate_plan.py
python -X utf8 docs/plan/build_plan.py --check
python -X utf8 docs/plan/build_plan.py
git init -b main
```

Validator kiểm JSON strict (không key trùng/NaN), schema và template, YAML không key trùng,
CSV đúng số cột, link nội bộ, Python syntax; đối chiếu benchmark Markdown/JSON/CSV,
config/charset hash/CTC/version, ownership A–B–C–D và quỹ 34+6h mỗi tuần.
Validator tự kiểm từ chối incomplete READY manifest và charset blank index sai.
Kiểm tra âm bổ sung bằng Python import validator đã xác minh từ chối:
JSON key trùng, YAML key trùng, CSV threshold khác JSON và observed=0 trong template chưa đo.

Đã đọc PDF bằng pypdf: đủ 38 trang, mỗi trang có text, các gate/CTC/NFC/manifest xuất hiện,
ký tự province CJK trích xuất được, không có Unicode replacement character.
Đây là kiểm cấu trúc/văn bản PDF; chưa có kiểm bằng hình ảnh từng trang.

Repo tham khảo được đọc bằng git show/ls-tree, kiểm lại git status sạch và HEAD giữ nguyên
`ffc228b0f3a6bde7ccc3bb6994fb45ac3aa6059d`. Không checkout, chỉnh file hoặc sao chép data cũ.
Không tìm thấy AGENTS.md trong ba ref đã xét hoặc các thư mục cha workspace đã kiểm.

## Chưa thực hiện

- Không tải CCPD/checkpoint, không cài môi trường training, không huấn luyện hoặc đánh giá mô hình.
- Parser, dataset acceptance suite, detect/recognize/predict/evaluator/demo chỉ có thiết kế;
  chưa có implementation hay test ALPR pass thật.
- Các lệnh `python -m alpr.cli ...` chưa triển khai; `configs/frozen.yaml` và model manifests READY chưa tồn tại.
- Dependency training, GPU/VRAM/RAM, epoch time và ngưỡng quality chưa xác minh bằng pilot.
- Windows CIM khảo sát CPU/RAM/GPU trả Access denied; không tìm thấy nvidia-smi.
  Ghi giả định phần cứng và fallback trong tài liệu tài nguyên, không coi đó là số đo.

Biên bản này phân biệt rõ kiểm kế hoạch đã chạy với benchmark/data/model còn CHƯA ĐO.
