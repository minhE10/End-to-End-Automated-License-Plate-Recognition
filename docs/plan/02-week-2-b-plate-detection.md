# Tuần 2 — B: YOLO phát hiện biển số

## Benchmark nghiệm thu đặt trước task

| ID | Benchmark | Chiều / ngưỡng tối thiểu | Loại |
| --- | --- | --- | --- |
| G2.1 | Detector artifact nạp lại | >= 1 ratio | integrity |
| G2.2 | Detection precision@0.50 | >= 0.8 ratio | quality |
| G2.3 | Detection recall@0.50 | >= 0.85 ratio | quality |
| G2.4 | Detection mAP50 | >= 0.8 ratio | quality |
| G2.5 | Detection mAP50-95 | >= 0.5 ratio | quality |
| G2.6 | Bàn giao predicted crops | >= 1 ratio | integrity |

Định nghĩa/mẫu số/ngưỡng phấn đấu/cơ sở/lệnh của từng ID: [benchmark chuẩn](05-weekly-goals-and-benchmarks.md). Tất cả **CHƯA ĐO**.

## Mục tiêu và phạm vi

B sở hữu baseline YOLOv8n, adapter detect(), evaluator detection, predicted dev crops và artifact detector nạp lại được.

## Đầu vào và điều kiện nhận

Nhận G1: data/split/hash, parser/crop/charset, smoke20 và metric fixtures. Trong 2h kiểm manifest, count, một batch label overlay; hash/split lỗi thì từ chối đầu vào.

## Ngân sách và task gợi ý

34 giờ thực hiện +6 dự phòng; không tính GPU chạy nền và tải mạng thành giờ công chờ máy.

| Task | Gợi ý | Giờ |
| --- | --- | --- |
| B01 | Kiểm nhận A trong hai giờ đầu | 2 |
| B02 | Môi trường GPU, smoke và YOLO adapter | 4 |
| B03 | Pilot và chọn budget huấn luyện trên dev | 6 |
| B04 | Điều phối baseline train, checkpoint và resume | 5 |
| B05 | Detection evaluation, P/R/AP và failure cases | 7 |
| B06 | Export predicted dev crops và test adapter | 4 |
| B07 | Khóa artifact, báo cáo và bàn giao C | 6 |

### Lịch ngày tham khảo

- Ngày 1 (8h): nhận 2h + môi trường/adapter 4h + pilot 2h.
- Ngày 2 (8h): pilot 4h + điều phối train 4h; GPU wall time tách giờ công.
- Ngày 3 (8h): train/checkpoint 1h + evaluation 7h.
- Ngày 4 (8h): predicted crops/adapter 4h + đóng gói/báo cáo 4h.
- Ngày 5 (8h): bàn giao 2h + dự phòng 6h.

## Cách triển khai đề xuất

Chọn YOLOv8n detection một lớp plate, Ultralytics 8.3.0, image size 640, pretrained COCO chỉ làm khởi tạo.
 Checkpoint nguồn phải có URL/hash và license; chưa có checkpoint nào trong skeleton.
 Disable augmentation có thể đảo chuỗi (horizontal/vertical flip) ở baseline; không đọc nhãn dev/test lúc train.
 Pilot 1k train/200 dev, 3 epochs để đo memory/throughput rồi đề xuất <=30 epochs trên subset đã chọn,
 early stop patience5, seed42. Không chạy sweep; chọn best theo dev mAP50-95, tie chọn epoch sớm.
 Budget tối đa 12 GPU giờ dự kiến; nếu pilot dự báo vượt thì giảm train subset/batch hoặc epochs và ghi log trước test.
 Adapter trả bbox đã undo letterbox về ảnh gốc. Test clamp bounds, score/NMS, empty case, mismatch checkpoint.
 Export predicted dev crops bằng cùng runtime top1 policy; giữ bbox/score/hash/coverage/parent ID;
 evaluator dùng GT cho chấm match, inference không được thấy GT. Không export test crops để C tune.
 Giữ raw detection predictions để AP dùng nhiều bbox và threshold thấp riêng với top1 pipeline.

## Đầu ra và bằng chứng

- Detector checkpoint + model manifest + dependency/platform lockfile đã smoke.
- detect() adapter, YOLO data config theo root tương đối, dev predictions và P/R/AP raw evidence.
- Predicted dev crops cùng policy và ID map; không nhầm GT crop.
- Báo cáo B, pilot timing, W2_B_to_C và lệnh reload offline.

## Tái lập dự kiến

`python -m alpr.cli verify-gate --gate G2 --config configs/frozen.yaml` **CHƯA TRIỂN KHAI**.
Chủ sở hữu phải thay bằng lệnh đã chạy thật trong biên bản, kèm stdout/stderr, env lock, commit, seed, hashes và per-sample CSV.

## Rủi ro, fallback và chưa đạt

VRAM ít: batch16→8→4, image640 giữ baseline trừ khi decision đổi trước test. CPU chỉ smoke; không cam kết huấn luyện đủ trên CPU. Không đạt detection quality sau dev pilot phải ghi fail/đổi lịch, không chuyển detector hỏng cho C.

## Checklist bàn giao

- [ ] G2 và hashes đúng data-v1; adapter detect() callable và offline reload.
- [ ] C chạy một batch trong 2h, output coords gốc và crop đúng schema.
- [ ] Known failures/confidence/NMS/preprocessing và runtime policy được freeze hoặc có decision rõ.
Dùng [template bàn giao](templates/handoff-template.md). Người giao chuẩn bị trong tuần mình, người nhận kiểm 2h đầu tuần kế; không suy ra nghĩa vụ hỗ trợ ngoài tuần.
