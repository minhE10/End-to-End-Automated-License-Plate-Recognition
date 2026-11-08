# Tuần 3 — C: CRNN và pipeline hoàn chỉnh

## Benchmark nghiệm thu đặt trước task

| ID | Benchmark | Chiều / ngưỡng tối thiểu | Loại |
| --- | --- | --- | --- |
| G3.1 | CRNN đúng kiến trúc/CTC | >= 1 ratio | integrity |
| G3.2 | OCR GT crop CER | <= 0.2 edit/char | quality |
| G3.3 | OCR GT crop exact | >= 0.55 ratio | quality |
| G3.4 | OCR predicted crop CER | <= 0.25 edit/char | quality |
| G3.5 | OCR predicted crop exact | >= 0.45 ratio | quality |
| G3.6 | Pipeline End-to-End Accuracy | >= 0.4 ratio | quality |
| G3.7 | Pixel-only/freeze/coverage | >= 1 ratio | integrity |

Định nghĩa/mẫu số/ngưỡng phấn đấu/cơ sở/lệnh của từng ID: [benchmark chuẩn](05-weekly-goals-and-benchmarks.md). Tất cả **CHƯA ĐO**.

## Mục tiêu và phạm vi

C sở hữu CNN + BiLSTM + CTC Loss, greedy CTC, recognize(), predict(), evaluator tích hợp và freeze. D phải nhận pipeline thật có thể gọi.

## Đầu vào và điều kiện nhận

Nhận G2 + G1 artifacts: detector callable/checkpoint, predicted dev crops, GT train/dev crops, charset và CTC fixtures. Trong 2h verify toàn bộ hash và shape; thiếu adapter hoặc charset thì chưa nhận.

## Ngân sách và task gợi ý

34 giờ thực hiện +6 dự phòng; không tính GPU chạy nền và tải mạng thành giờ công chờ máy.

| Task | Gợi ý | Giờ |
| --- | --- | --- |
| C01 | Kiểm nhận detector, charset và data hash | 2 |
| C02 | CNN, BiLSTM, CTC trainer và greedy decoder | 8 |
| C03 | Ghép predict() và trạng thái lỗi từ đầu tuần | 4 |
| C04 | Pilot/huấn luyện và OCR dev GT/predicted | 7 |
| C05 | Hai cấu hình preprocessing và lỗi detector/OCR | 5 |
| C06 | Freeze checkpoint/config, evaluator và anti-leak | 4 |
| C07 | Smoke offline, báo cáo và bàn giao pipeline D | 4 |

### Lịch ngày tham khảo

- Ngày 1 (8h): nhận 2h + CRNN 4h + pipeline 2h.
- Ngày 2 (8h): CRNN 4h + pipeline 2h + pilot train 2h.
- Ngày 3 (8h): train/dev 5h + ablation 3h.
- Ngày 4 (8h): ablation 2h + freeze/evaluator 4h + handoff 2h.
- Ngày 5 (8h): handoff 2h + dự phòng 6h.

## Cách triển khai đề xuất

Dùng thiết kế CRNN cụ thể tại 08: grayscale 32x160, CNN width stride4, T40, BiLSTM2 tầng hidden128,
 projection C=68 (67 token thật + blank0), log_softmax, CTCLoss. Không pretrained OCR thay đề bài.
 Train GT bbox crops train, dev GT crops chọn best CER; teacher labels train hợp lệ.
 Greedy decode argmax→collapse repeats→remove blank; không sửa chuỗi theo GT/filename.
 Test repeated labels, target lengths và T>=L+adjacent-repeats; zero_infinity không che invalid CTC samples.
 Pilot 1k train/200 dev, 2 epochs, sau đó <=40 epochs, patience5; tối đa 16 GPU giờ dự kiến.
 Tối đa hai cấu hình preprocess: baseline grayscale và CLAHE (clip2,tile8x8), chọn trên dev rồi khóa;
 không train thêm biến thể nếu budget đã vượt, báo thiếu ablation trung thực.
 Đánh giá GT crop, predicted conditional và original-image pipeline, cùng denominators.
 Gắn failure status; test đổi tên cùng pixel và opaque ID không làm thay prediction ngoài trường ID.
 Freeze checkpoint/config/charset/split và cả ablation artifacts trước khi D mở test.
 Pipeline không có parser filename hoặc nhận GT; nhận pixel qua RuntimeImage.
 Gói bàn giao phải có predict() thật, sample20, evaluator, dependency lock và smoke log clean checkout.

## Đầu ra và bằng chứng

- Recognizer state_dict/checkpoint, optimizer resume riêng nếu cần, decoder version, model manifest.
- recognize() + predict() callable, tests interface/CTC/anti-leak, evaluator toàn split.
- Dev raw results, ablation manifests/configs, frozen run/release candidate manifest.
- W3_C_to_D, báo cáo C, demo smoke sample không nhãn trong tên runtime.

## Tái lập dự kiến

`python -m alpr.cli verify-gate --gate G3 --config configs/frozen.yaml` **CHƯA TRIỂN KHAI**.
Chủ sở hữu phải thay bằng lệnh đã chạy thật trong biên bản, kèm stdout/stderr, env lock, commit, seed, hashes và per-sample CSV.

## Rủi ro, fallback và chưa đạt

CTC không hội tụ: kiểm lengths/blank/charset/input, overfit 32 train samples để debug rồi bỏ run debug khỏi kết quả. Giảm subset/epochs hoặc bỏ extension; không thay CRNN. Chưa có checkpoint/predict() callable => G3 chưa đạt và D không bắt đầu ghép core.

## Checklist bàn giao

- [ ] D gọi predict() bằng pixel trong 2h với đúng checkpoint/hash.
- [ ] Metric full split/miss và CTC repeated-label fixtures pass.
- [ ] Freeze trước test, threshold decision có dev evidence, GT không lọt inference.
Dùng [template bàn giao](templates/handoff-template.md). Người giao chuẩn bị trong tuần mình, người nhận kiểm 2h đầu tuần kế; không suy ra nghĩa vụ hỗ trợ ngoài tuần.
