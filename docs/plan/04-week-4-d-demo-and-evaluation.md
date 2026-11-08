# Tuần 4 — D: demo, test và phát hành

## Benchmark nghiệm thu đặt trước task

| ID | Benchmark | Chiều / ngưỡng tối thiểu | Loại |
| --- | --- | --- | --- |
| G4.1 | Demo ảnh đơn/batch và lỗi | >= 1 ratio | integrity |
| G4.2 | Test End-to-End Accuracy | >= 0.4 ratio | quality |
| G4.3 | Test pipeline CER | <= 0.35 edit/char | quality |
| G4.4 | Joint detection-recognition@0.50 | bắt buộc báo số đo | reporting |
| G4.5 | Báo đầy đủ detection/OCR/coverage/strata | >= 1 ratio | integrity |
| G4.6 | Latency và tài nguyên | bắt buộc báo số đo | reporting |
| G4.7 | Ablation/error analysis/release | >= 1 ratio | integrity |

Định nghĩa/mẫu số/ngưỡng phấn đấu/cơ sở/lệnh của từng ID: [benchmark chuẩn](05-weekly-goals-and-benchmarks.md). Tất cả **CHƯA ĐO**.

## Mục tiêu và phạm vi

D làm demo ảnh đơn/batch, final test, latency, phân tích lỗi và gói nộp; không viết mới detector/CRNN/pipeline.

## Đầu vào và điều kiện nhận

Nhận G3: predict() callable, checkpoint thật, manifest freeze, sample20, evaluator và ablation artifacts. Trong 2h reload offline và kiểm hash; test labels chỉ mở sau bước này.

## Ngân sách và task gợi ý

34 giờ thực hiện +6 dự phòng; không tính GPU chạy nền và tải mạng thành giờ công chờ máy.

| Task | Gợi ý | Giờ |
| --- | --- | --- |
| D01 | Kiểm nhận pipeline đã ghép và frozen manifest | 2 |
| D02 | Demo ảnh đơn và batch, xử lý lỗi | 6 |
| D03 | Test cuối từ frozen artifacts và per-image metrics | 6 |
| D04 | Latency, resource và clean-machine reproduction | 5 |
| D05 | Strata, ablation và audit lỗi | 5 |
| D06 | Báo cáo, slide và kịch bản demo | 6 |
| D07 | Release manifest, README và gói nộp | 4 |

### Lịch ngày tham khảo

- Ngày 1 (8h): nhận 2h + demo 6h.
- Ngày 2 (8h): test cuối 6h + latency/reproduce 2h.
- Ngày 3 (8h): latency/reproduce 3h + strata/ablation/error audit 5h.
- Ngày 4 (8h): báo cáo/slide/demo 6h + release 2h.
- Ngày 5 (8h): release 2h + dự phòng 6h.

## Cách triển khai đề xuất

Demo nhận upload pixel, tên file chỉ để hiển thị tùy chọn sau inference; không dùng CCPD parser.
 Ghi bbox/text/score/status riêng, ảnh lỗi hiển thị lỗi rõ; batch giữ 1 result cho mọi input.
 Sáu fixture demo: ảnh đơn hợp lệ; batch có ảnh lỗi; no_detection; decode error; ocr_empty; manifest mismatch.
 D giữ test gold ngoài runtime, chấm toàn frozen test đúng ID, không lọc ảnh fail và không tune bằng test.
 Báo detection P/R/AP, OCR GT/predicted/coverage, E2E/CER/joint, strata và failure counts.
 Ablation cùng tập/config đã freeze; GT corners nếu có chỉ là oracle bảng riêng.
 Đo latency đúng warmup/batch/synchronization, hardware, I/O/model/pipeline riêng.
 Audit <=50 lỗi có taxonomy và hình minh họa; không công bố dữ liệu cá nhân ngoài phạm vi đồ án.
 Nếu phát hiện bug evaluator/pipeline sau test: log lần exposure, sửa correctness, rerun mọi run bị ảnh hưởng;
 không dùng lần sửa để chọn augmentation/decoder mới. Kết quả test trở thành exposed, nêu rõ trong báo cáo.
 Báo cáo có phương pháp, tài nguyên, split custom, hạn chế domain/identity và số đo thật; slide và video backup chỉ khi có demo thật.

## Đầu ra và bằng chứng

- Demo offline, frozen checkpoints/manifests và asset runtime opaque đã kiểm hash.
- Per-image predictions/metrics, test exposure log, strata/error audit, latency CSV.
- Báo cáo/slide/README có trạng thái và hướng tái lập, release manifest và gói nộp.
- Biên bản G4 với pass/fail thật; không giấu ngưỡng trượt hoặc thiếu ablation.

## Tái lập dự kiến

`python -m alpr.cli verify-gate --gate G4 --config configs/frozen.yaml` **CHƯA TRIỂN KHAI**.
Chủ sở hữu phải thay bằng lệnh đã chạy thật trong biên bản, kèm stdout/stderr, env lock, commit, seed, hashes và per-sample CSV.

## Rủi ro, fallback và chưa đạt

Thiếu checkpoint hoặc predict() fail smoke: từ chối G3, lập blocker/lịch mới. Demo tối giản CLI/image report thay UI nhiều tính năng. Không mở rộng video/API để bù thiếu metric. Quality trượt vẫn công bố số thật và gate fail.

## Checklist bàn giao

- [ ] Test freeze/hash/denominator đúng, không tune sau test.
- [ ] 6/6 demo fixture và reload offline, không tự tải model khi chạy.
- [ ] Manifest release không vòng hash; không commit dataset/checkpoint lớn; kết quả chưa đo giữ null.
Dùng [template bàn giao](templates/handoff-template.md). Người giao chuẩn bị trong tuần mình, người nhận kiểm 2h đầu tuần kế; không suy ra nghĩa vụ hỗ trợ ngoài tuần.
