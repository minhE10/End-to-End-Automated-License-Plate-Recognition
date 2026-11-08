# Gate G1–G4 và định nghĩa phép đo

**Tất cả số đo hiện CHƯA ĐO / null.** Gate chỉ đạt khi có artifact, denominator, log và lệnh chạy lại.
`integrity` là bắt buộc; `quality` là ngưỡng đề xuất cần pilot dev, sau freeze trở thành cam kết;
`reporting` yêu cầu đo thật và công bố đầy đủ, chưa áp đặt ngưỡng tốc độ khi phần cứng chưa biết.
Gate có ngưỡng chất lượng chưa đạt phải báo CHƯA ĐẠT dù backlog đã xong.

Nguồn ngưỡng là ngân sách 4 x40 giờ, 5k–20k ảnh train và một GPU 8 GB giả định; không sao chép kết quả bài báo.
Mọi ngưỡng quality có độ chắc chắn thấp cho tới pilot. B đề xuất detection sau pilot tuần 2;
C đề xuất OCR/E2E sau pilot tuần 3, D kiểm manifest freeze trước test.
Chỉ chấp nhận thay đổi khi có decision log, dev evidence, lý do tài nguyên và chữ ký người nhận trước mở test.
Không hiệu chỉnh trên test. Integrity không được nới.

## Protocol chung

CER micro = Σ Levenshtein(pred,gt) / Σ số codepoint GT sau NFC cho cả hai.
Không strip dấu, không xóa ký tự lạ, không sửa theo format biển hoặc lexicon GT. CER có thể >1.
Exact plate accuracy đòi chuỗi NFC bằng hoàn toàn. Mẫu số rỗng => null + lỗi đánh giá, không thành 0 hoặc 1.
Nếu prediction thiếu/duplicate ID: evaluator từ chối báo thành công, lưu lỗi inventory;
runner tạo một result cho mỗi input, ghi error khi thất bại. Để tính toàn split, missing prediction được tính empty/fail và báo coverage lỗi.

Detection precision/recall dùng tất cả bbox sau NMS IoU=0.50 và confidence>=0.25 mặc định (chỉ chỉnh bằng dev).
Matching theo score giảm dần, mỗi GT tối đa một match, IoU>=0.50. FP=prediction không match; FN=GT không match.
Nếu TP+FP=0, precision=0 kèm no_predictions=true; recall=0 khi có GT. Ngt=0 => null.
AP dùng score>=0.001, cùng NMS, tối đa 100 detections/ảnh, PR envelope 101 recall points,
AP50 và mean AP ở 10 IoU 0.50:0.05:0.95, một lớp plate. Ghi evaluator/version chính xác.
Các diagnostic P/R dùng nhiều bbox, còn pipeline chỉ chọn một bbox; đây là hai protocol khác nhau được ghi rõ.

Pipeline chọn top1 confidence cao nhất sau NMS và threshold runtime; hòa score thì sort `(x1,y1,x2,y2)` tăng dần.
Không dùng IoU với GT, OCR text hoặc filename để chọn bbox. Không có top1 => no_detection.
OCR GT crop dùng bbox GT chữ nhật, không warp corners. Predicted crop diagnostic chỉ dùng top1
có IoU>=0.50 và crop hợp lệ; evaluator mới dùng GT để xác định tập điều kiện.
Coverage=Nmatched/Nsplit; báo thêm Nselected, Ncrop_valid, Nunmatched. Nếu không matched, conditional metric=null và gate quality fail.
GT CER/exact giữ OCR lỗi/rỗng trong mẫu số; predicted CER/exact cũng giữ lỗi OCR của mọi crop trong tập matched.

**End-to-End Accuracy = số ảnh có chuỗi top1 nhận đúng hoàn toàn / mọi ảnh trong split**.
Metric chính không đòi IoU; nếu top1 ở vị trí sai mà text tình cờ đúng vẫn đúng theo metric text này.
Joint@0.50 đòi thêm IoU>=0.50, tên riêng. Miss/crop_error/ocr_empty/runtime_error luôn sai E2E.
Pipeline CER dùng pred rỗng cho các lỗi đó. Không bỏ ảnh khó hoặc ảnh chạy lỗi khỏi báo cáo.
Ảnh hỏng nguồn phải quarantine trước freeze split, có số lượng/lý do; ảnh lỗi phát sinh sau freeze không tự xóa khỏi denominator.

Strata: toàn Base và các bin blur/brightness/tilt/plate-area được định nghĩa bằng train trước freeze;
report N, CER, E2E của từng bin, micro toàn split; nhóm rỗng có N=0 và metric=null.
Nếu chạy subset DB/Blur/FN/Rotate/Tilt/Challenge/Green, báo riêng tên protocol và N từng subset,
không gộp vào headline Base hoặc giả sử đã đo. Báo Wilson95% cho E2E, bootstrap seed42 1000 lần cho CER nếu còn thời gian.

Latency: đo model detect và OCR riêng trên tensor resident (đồng bộ CUDA trước/sau), pipeline từ pixel CPU
qua preprocess/transfer/detect/crop/OCR/decode/serialization; báo thêm file I/O riêng.
Không tính load checkpoint vào latency steady-state, báo cold start riêng.
20 warm-up +200 lượt đo, batch=1, GPU synchronize, no output cache, một checkpoint/config cố định.
p95 là nearest-rank sort[ceil(.95*N)-1], p50 tương tự; báo throughput batch riêng nếu đo.
Record GPU/CPU/driver/CUDA, RAM, peak allocated/reserved VRAM, torch/package versions, precision và model hash.

## Bảng gate


### G1

| ID | Benchmark | Chiều / ngưỡng tối thiểu | Loại |
| --- | --- | --- | --- |
| G1.1 | Quy mô khả thi | >= 1 ratio | integrity |
| G1.2 | Toàn vẹn schema/provenance | >= 1 ratio | integrity |
| G1.3 | Giao split bị cấm | <= 0 count | integrity |
| G1.4 | Parser audit | >= 1 ratio | integrity |
| G1.5 | Metric/charset/preprocessing fixtures | >= 1 ratio | integrity |

### G2

| ID | Benchmark | Chiều / ngưỡng tối thiểu | Loại |
| --- | --- | --- | --- |
| G2.1 | Detector artifact nạp lại | >= 1 ratio | integrity |
| G2.2 | Detection precision@0.50 | >= 0.8 ratio | quality |
| G2.3 | Detection recall@0.50 | >= 0.85 ratio | quality |
| G2.4 | Detection mAP50 | >= 0.8 ratio | quality |
| G2.5 | Detection mAP50-95 | >= 0.5 ratio | quality |
| G2.6 | Bàn giao predicted crops | >= 1 ratio | integrity |

### G3

| ID | Benchmark | Chiều / ngưỡng tối thiểu | Loại |
| --- | --- | --- | --- |
| G3.1 | CRNN đúng kiến trúc/CTC | >= 1 ratio | integrity |
| G3.2 | OCR GT crop CER | <= 0.2 edit/char | quality |
| G3.3 | OCR GT crop exact | >= 0.55 ratio | quality |
| G3.4 | OCR predicted crop CER | <= 0.25 edit/char | quality |
| G3.5 | OCR predicted crop exact | >= 0.45 ratio | quality |
| G3.6 | Pipeline End-to-End Accuracy | >= 0.4 ratio | quality |
| G3.7 | Pixel-only/freeze/coverage | >= 1 ratio | integrity |

### G4

| ID | Benchmark | Chiều / ngưỡng tối thiểu | Loại |
| --- | --- | --- | --- |
| G4.1 | Demo ảnh đơn/batch và lỗi | >= 1 ratio | integrity |
| G4.2 | Test End-to-End Accuracy | >= 0.4 ratio | quality |
| G4.3 | Test pipeline CER | <= 0.35 edit/char | quality |
| G4.4 | Joint detection-recognition@0.50 | bắt buộc báo số đo | reporting |
| G4.5 | Báo đầy đủ detection/OCR/coverage/strata | >= 1 ratio | integrity |
| G4.6 | Latency và tài nguyên | bắt buộc báo số đo | reporting |
| G4.7 | Ablation/error analysis/release | >= 1 ratio | integrity |

## Từng benchmark: công thức, mẫu số, bằng chứng

### G1.1 — Quy mô khả thi

- Chủ sở hữu: **A**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **train/dev/test**.
- Công thức: `min(Ntrain/5000,Ndev/500,Ntest/500)`; mẫu số/số mẫu: Tất cả ảnh hợp lệ sau dedup và group split.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `4`; loại `integrity`.
- Cơ sở: Tối thiểu 5000/500/500; mục tiêu 20000/2000/2000. Đây là ngân sách subset, không là số lượng dataset chính thức. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g1/G1.1-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G1 --benchmark G1.1 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G1.2 — Toàn vẹn schema/provenance

- Chủ sở hữu: **A**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **all**.
- Công thức: `N_valid / N_artifact_records`; mẫu số/số mẫu: Mọi record và artifact bàn giao; ảnh loại có log riêng.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g1/G1.2-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G1 --benchmark G1.2 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G1.3 — Giao split bị cấm

- Chủ sở hữu: **A**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **all**.
- Công thức: `N_cross_split_exact + N_cross_split_cluster + N_cross_split_plate`; mẫu số/số mẫu: So sánh mọi cặp split trên toàn inventory.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `<=`; đơn vị `count`.
- Ngưỡng tối thiểu: `0`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g1/G1.3-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G1 --benchmark G1.3 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G1.4 — Parser audit

- Chủ sở hữu: **A**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **train/dev + synthetic**.
- Công thức: `N_correct / N_audited`; mẫu số/số mẫu: 100 ảnh train/dev: 80 random seed42 +20 khó; >=12 fixture lỗi.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: BBox/text đối chiếu nguồn và ảnh; test không dùng audit. Trường hợp không rõ phải quarantine, không xác nhận đúng bằng parser tự so với chính nó. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g1/G1.4-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G1 --benchmark G1.4 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G1.5 — Metric/charset/preprocessing fixtures

- Chủ sở hữu: **A**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **synthetic + train/dev**.
- Công thức: `N_pass / N_cases`; mẫu số/số mẫu: Ít nhất 20 ca parser/CTC/metrics/shape; thống kê coverage từng nhóm.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g1/G1.5-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G1 --benchmark G1.5 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G2.1 — Detector artifact nạp lại

- Chủ sở hữu: **B**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev smoke**.
- Công thức: `N_pass / N_checks`; mẫu số/số mẫu: >=20 ảnh dev + manifest/hash/config/offline reload checks.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g2/G2.1-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G2 --benchmark G2.1 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G2.2 — Detection precision@0.50

- Chủ sở hữu: **B**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev**.
- Công thức: `TP/(TP+FP)`; mẫu số/số mẫu: Tất cả prediction sau NMS, conf cố định; TP matching 1:1 IoU>=0.50.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `0.8`; phấn đấu: `0.9`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g2/G2.2-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G2 --benchmark G2.2 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G2.3 — Detection recall@0.50

- Chủ sở hữu: **B**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev**.
- Công thức: `TP/(TP+FN)`; mẫu số/số mẫu: Tất cả GT trên dev; Ndev>=500; miss vẫn là FN.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `0.85`; phấn đấu: `0.93`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g2/G2.3-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G2 --benchmark G2.3 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G2.4 — Detection mAP50

- Chủ sở hữu: **B**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev**.
- Công thức: `AP at IoU 0.50`; mẫu số/số mẫu: Một lớp plate; mọi prediction score>=0.001; Ndev>=500.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `0.8`; phấn đấu: `0.9`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g2/G2.4-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G2 --benchmark G2.4 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G2.5 — Detection mAP50-95

- Chủ sở hữu: **B**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev**.
- Công thức: `mean(AP_t), t=0.50:0.05:0.95`; mẫu số/số mẫu: Một lớp, tất cả dev; 10 IoU thresholds; 101-point interpolated PR.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `0.5`; phấn đấu: `0.65`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g2/G2.5-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G2 --benchmark G2.5 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G2.6 — Bàn giao predicted crops

- Chủ sở hữu: **B**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev**.
- Công thức: `N_valid_linked / N_eligible`; mẫu số/số mẫu: Mọi top1 detection đủ conf và crop hợp lệ; báo Neligible/Ndev.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g2/G2.6-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G2 --benchmark G2.6 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G3.1 — CRNN đúng kiến trúc/CTC

- Chủ sở hữu: **C**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **synthetic/train/dev**.
- Công thức: `N_pass / N_cases`; mẫu số/số mẫu: >=8 CTC/shape/checkpoint tests; CNN+BiLSTM+CTCLoss được inspect.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g3/G3.1-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G3 --benchmark G3.1 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G3.2 — OCR GT crop CER

- Chủ sở hữu: **C**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev GT bbox crops**.
- Công thức: `sum(edit_distance)/sum(len(gt))`; mẫu số/số mẫu: Tất cả Ndev>=500, >=3500 ký tự GT; không loại OCR rỗng/lỗi.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `<=`; đơn vị `edit/char`.
- Ngưỡng tối thiểu: `0.2`; phấn đấu: `0.1`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g3/G3.2-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G3 --benchmark G3.2 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G3.3 — OCR GT crop exact

- Chủ sở hữu: **C**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev GT bbox crops**.
- Công thức: `N_exact / Ndev`; mẫu số/số mẫu: Tất cả Ndev; NFC nguyên chuỗi; empty/error sai.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `0.55`; phấn đấu: `0.75`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g3/G3.3-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G3 --benchmark G3.3 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G3.4 — OCR predicted crop CER

- Chủ sở hữu: **C**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev conditional predicted crops**.
- Công thức: `sum(edit_distance)/sum(len(gt_matched))`; mẫu số/số mẫu: Top1 IoU>=0.50 và crop hợp lệ; báo Nmatched,Nchars,coverage; Nmatched=0 => null/fail.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `<=`; đơn vị `edit/char`.
- Ngưỡng tối thiểu: `0.25`; phấn đấu: `0.15`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g3/G3.4-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G3 --benchmark G3.4 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G3.5 — OCR predicted crop exact

- Chủ sở hữu: **C**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev conditional predicted crops**.
- Công thức: `N_exact_matched / Nmatched`; mẫu số/số mẫu: Cùng tập G3.4; coverage=Nmatched/Ndev; không bỏ nhận dạng rỗng/lỗi.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `0.45`; phấn đấu: `0.65`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g3/G3.5-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G3 --benchmark G3.5 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G3.6 — Pipeline End-to-End Accuracy

- Chủ sở hữu: **C**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev original images**.
- Công thức: `N_images_exact / Ndev`; mẫu số/số mẫu: Toàn Ndev>=500; miss/crop error/runtime error = failure; top1 cố định.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `0.4`; phấn đấu: `0.65`; loại `quality`.
- Cơ sở: Mốc khởi đầu xấp xỉ 0.85 recall x 0.45 OCR conditional; không phải kết quả độc lập hay bảo đảm. Hiệu chỉnh bằng pilot dev. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g3/G3.6-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G3 --benchmark G3.6 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G3.7 — Pixel-only/freeze/coverage

- Chủ sở hữu: **C**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev + synthetic**.
- Công thức: `N_pass / N_checks`; mẫu số/số mẫu: 100 ảnh đổi tên cùng pixel; full ID coverage; runtime không parser/GT; config+checkpoint freeze.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g3/G3.7-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G3 --benchmark G3.7 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G4.1 — Demo ảnh đơn/batch và lỗi

- Chủ sở hữu: **D**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **demo riêng**.
- Công thức: `N_pass / 6`; mẫu số/số mẫu: 6 ca: ảnh đơn, batch, không detect, ảnh lỗi, OCR empty, artifact mismatch.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g4/G4.1-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G4 --benchmark G4.1 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G4.2 — Test End-to-End Accuracy

- Chủ sở hữu: **D**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **test original images**.
- Công thức: `N_images_exact / Ntest`; mẫu số/số mẫu: Toàn Ntest>=500; ít nhất 3500 ký tự GT; miss và mọi lỗi vẫn nằm mẫu số.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `0.4`; phấn đấu: `0.65`; loại `quality`.
- Cơ sở: Kế thừa mục tiêu dev G3.6 đã freeze; không giảm ngưỡng sau xem test. Khoảng Wilson 95% được báo kèm. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g4/G4.2-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G4 --benchmark G4.2 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G4.3 — Test pipeline CER

- Chủ sở hữu: **D**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **test original images**.
- Công thức: `sum(edit_distance(pred_or_empty,gt))/sum(len(gt))`; mẫu số/số mẫu: Mọi ảnh test; miss/error pred=""; không lọc ký tự sai hoặc unknown.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `<=`; đơn vị `edit/char`.
- Ngưỡng tối thiểu: `0.35`; phấn đấu: `0.2`; loại `quality`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g4/G4.3-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G4 --benchmark G4.3 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G4.4 — Joint detection-recognition@0.50

- Chủ sở hữu: **D**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **test original images**.
- Công thức: `N_top1_IoU_ge_0.50_and_exact / Ntest`; mẫu số/số mẫu: Toàn Ntest; metric bổ sung, khác End-to-End Accuracy.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `report`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `null`; phấn đấu: `null`; loại `reporting`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g4/G4.4-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G4 --benchmark G4.4 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G4.5 — Báo đầy đủ detection/OCR/coverage/strata

- Chủ sở hữu: **D**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **test**.
- Công thức: `N_present / N_required`; mẫu số/số mẫu: 11 metric bắt buộc + bảng theo từng strata quan sát được; nhóm rỗng ghi N=0, metric=null.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: 11 metric: precision, recall, mAP50, mAP50-95, GT CER/exact, predicted CER/exact/coverage, E2E, pipeline CER; joint báo thêm G4.4. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g4/G4.5-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G4 --benchmark G4.5 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G4.6 — Latency và tài nguyên

- Chủ sở hữu: **D**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev fixed latency set**.
- Công thức: `p50,p95 of elapsed_ms`; mẫu số/số mẫu: 20 warm-up +200 measured forwards, batch1; nạp model một lần; 200 ID cố định từ dev; công bố CPU/GPU/VRAM/RAM.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `report`; đơn vị `ms`.
- Ngưỡng tối thiểu: `null`; phấn đấu: `null`; loại `reporting`.
- Cơ sở: Mốc pilot thực dụng trên custom Base; chưa có số đo nội bộ, độ chắc chắn thấp. Cần freeze bằng dev trước test. Độ chắc chắn `low_until_dev_pilot`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g4/G4.6-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G4 --benchmark G4.6 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

### G4.7 — Ablation/error analysis/release

- Chủ sở hữu: **D**; dataset: CCPD2019 ccpd_base / alpr-custom-base-group-v1; split: **dev selection + final test report**.
- Công thức: `N_pass / N_checks`; mẫu số/số mẫu: GT vs predicted crop; baseline vs 1 preprocessing đã chọn trên dev; >=50 lỗi hoặc toàn bộ nếu <50; release reload offline.
- Tổng hợp: micro/full split unless explicitly conditional; chiều: `>=`; đơn vị `ratio`.
- Ngưỡng tối thiểu: `1`; phấn đấu: `null`; loại `integrity`.
- Cơ sở: Điều kiện tính đúng và tái lập, không được nới để che lỗi. Độ chắc chắn `high`.
- Tài nguyên: Python 3.11, 1 GPU CUDA 8 GB đề xuất; chưa xác minh. Subset tối thiểu nếu thiếu tài nguyên.
- Bằng chứng dự kiến: `reports/runs/g4/G4.7-evidence.json` + per-image/per-crop CSV, frozen manifest và stdout/stderr.
- Lệnh dự kiến **CHƯA TRIỂN KHAI**: `python -m alpr.cli verify-gate --gate G4 --benchmark G4.7 --config configs/frozen.yaml`.
- Kết quả hiện tại: **CHƯA ĐO**, observed=null, observed_n=null.

## Nghiệm thu và ablation

Mọi bảng phải có ID run, dataset/split/config/charset/checkpoint hashes, N thực tế, numerator và denominator,
failure counts, raw predictions, runtime/error log. Không dùng 0 thay số đo chưa chạy.
Mẫu CSV dùng token `null`; JSON dùng null thật. Khi có số đo, tạo file run riêng, giữ template nguyên trạng.
Nếu ngưỡng tối thiểu trượt: báo số thật, đánh dấu gate fail, đề xuất scope/schedule có decision; không chọn test đẹp.

Ablation bắt buộc vừa sức: (1) cùng recognizer trên GT crop và predicted crop, báo coverage và pipeline toàn ảnh;
(2) baseline grayscale so với duy nhất một cải tiến contrast/CLAHE, chọn bằng dev với tối đa 2 cấu hình;
(3) taxonomy detector miss/localization/crop/recognition, đếm theo toàn split và audit tối đa 50 lỗi.
C chuẩn bị checkpoint/config cả hai biến thể đã freeze để D chạy báo cáo, không chuyển tuning sang D.
Nếu không kịp biến thể cải tiến, ghi ablation chưa hoàn thành và gate tương ứng chưa đạt; không giả số đo.
