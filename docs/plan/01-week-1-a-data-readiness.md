# Tuần 1 — A: dữ liệu sẵn sàng

## Benchmark nghiệm thu đặt trước task

| ID | Benchmark | Chiều / ngưỡng tối thiểu | Loại |
| --- | --- | --- | --- |
| G1.1 | Quy mô khả thi | >= 1 ratio | integrity |
| G1.2 | Toàn vẹn schema/provenance | >= 1 ratio | integrity |
| G1.3 | Giao split bị cấm | <= 0 count | integrity |
| G1.4 | Parser audit | >= 1 ratio | integrity |
| G1.5 | Metric/charset/preprocessing fixtures | >= 1 ratio | integrity |

Định nghĩa/mẫu số/ngưỡng phấn đấu/cơ sở/lệnh của từng ID: [benchmark chuẩn](05-weekly-goals-and-benchmarks.md). Tất cả **CHƯA ĐO**.

## Mục tiêu và phạm vi

A sở hữu dataset/parser/split/crop/charset/QA và metric dùng chung. B không phải viết lại parser hoặc đoán mapping.

## Đầu vào và điều kiện nhận

Đầu vào: tài liệu nguồn CCPD, quyền lấy archive, disk budget, contract v1. Hai giờ đầu kiểm nguồn và quy mô pilot; chưa nhận model từ ai.

## Ngân sách và task gợi ý

34 giờ thực hiện +6 dự phòng; không tính GPU chạy nền và tải mạng thành giờ công chờ máy.

| Task | Gợi ý | Giờ |
| --- | --- | --- |
| A01 | Nguồn, dung lượng, protocol và quyền truy cập | 2 |
| A02 | Parser filename, mapping, quarantine và fixture | 6 |
| A03 | Dedup, group split và anti-leak inventory | 7 |
| A04 | Crop/preprocess, charset và CTC shape contract | 6 |
| A05 | Metric chung, QA100 và acceptance suite | 7 |
| A06 | Manifest, sample offline, báo cáo và bàn giao | 6 |

### Lịch ngày tham khảo

- Ngày 1 (8h): nguồn 2h + parser 6h; xác minh 7 field và lỗi annotation.
- Ngày 2 (8h): dedup/group split 7h + crop 1h; freeze nhóm trước tạo crop.
- Ngày 3 (8h): crop/charset 5h + metrics/QA 3h.
- Ngày 4 (8h): metrics/QA 4h + manifests/sample 4h.
- Ngày 5 (8h): bàn giao 2h + dự phòng 6h.

## Cách triển khai đề xuất

Parser: bbox LT/RB, corners RB/LB/LT/RT, mapping positional province/letter/ads, sentinel O bị quarantine.
 Giữ raw coordinates; canonical bbox half-open theo quy tắc x2/y2 không cộng 1, audit hình ảnh trước freeze.
 Dedup byte + decoded RGB + pHash candidate và union-find với text plate; toàn bộ connected component chỉ một split.
 Split seed42 trước crop/augmentation; runtime ảnh tên opaque không chứa nhãn; test gold tách khỏi consumer.
 Charset + hash/version, crop grayscale aspect-resize/pad, metric Levenshtein/IoU/exact và fixtures được A viết thật.
 QA100 train/dev và fixture lỗi phải có annotation đối chiếu độc lập, không tự dùng parser làm gold.
 Tạo smoke 20 ảnh train/dev và loader/offline checker có manifest; B chạy được mà không tải raw.
 Phân loại train labels hợp lệ với test gold: trainer được nhận GT train, evaluator giữ GT dev/test.

## Đầu ra và bằng chứng

- source/data/split/charset manifests + sample/crop JSONL và YOLO label export.
- 20 ảnh smoke train/dev + nhãn, checksum; không có dữ liệu thật ở repo khởi đầu này.
- Source/QA/quarantine/leakage reports; tests parser/metric/preprocess có lệnh tái lập.
- Báo cáo A và W1_A_to_B; hướng dẫn lấy dữ liệu và thay root paths.

## Tái lập dự kiến

`python -m alpr.cli verify-gate --gate G1 --config configs/frozen.yaml` **CHƯA TRIỂN KHAI**.
Chủ sở hữu phải thay bằng lệnh đã chạy thật trong biên bản, kèm stdout/stderr, env lock, commit, seed, hashes và per-sample CSV.

## Rủi ro, fallback và chưa đạt

Archive chậm hoặc disk ít: chỉ tải subset qua nguồn có thể xác minh; nếu không có tải từng subset thì dùng kho ngoài và chuyển phần Base cần thiết. Không hứa archive hỗ trợ streaming chưa kiểm. Dưới 5k/500/500 hoặc overlap >0 => G1 chưa đạt.

## Checklist bàn giao

- [ ] Hash/nguồn/version, count split tối thiểu, audit100 và quarantine log đầy đủ.
- [ ] B nhận sample và validate trong 2h; test gold không nằm runtime.
- [ ] Contract/charset/preprocess/fixtures đủ cho B và C; không còn mapping chưa rõ.
Dùng [template bàn giao](templates/handoff-template.md). Người giao chuẩn bị trong tuần mình, người nhận kiểm 2h đầu tuần kế; không suy ra nghĩa vụ hỗ trợ ngoài tuần.
