# Kiến trúc, CTC và giao diện module

## Detector và crop

Baseline **YOLOv8n detection**, package **ultralytics==8.3.0**, một lớp `plate`, image640,
batch16 tham khảo, seed42. Đây là lựa chọn baseline nhỏ để hạn chế chi phí thử nhiều model;
không khẳng định là phiên bản mới nhất. Chưa kiểm tương thích trên máy/GPU này.
[Nguồn YOLOv8](https://docs.ultralytics.com/models/yolov8/),
[release v8.3.0](https://github.com/ultralytics/ultralytics/releases/tag/v8.3.0).
Torch2.5.1/torchvision0.20.1 với Python3.11 là đề xuất; B phải smoke và khóa lock/CUDA trước train.

Input uint8 RGB HxWx3; thư viện nhận BGR thì adapter đổi đúng một lần. Detector làm letterbox640,
trả bbox original pixels float, clip, class0, score. detect() trả candidates sau NMS với score>=0.001; orchestrator áp runtime conf0.25 để phân biệt low_confidence/no_detection. Runtime NMS IoU0.50, conf0.25 baseline;
AP confidence0.001 là evaluator diagnostic riêng. NMS stable sort theo score và bbox để deterministic.
Top1 chọn score cao nhất sau NMS/threshold, tie bbox lexicographic; không dùng GT/recognizer để chọn.
Crop rectangle dự đoán, padding bbox=0 baseline; box margin5% là extension khác chỉ chọn trên dev.
Rectification không nằm baseline; nếu có cần predicted corners model riêng, còn GT corners chỉ oracle.

## Recognizer bắt buộc CNN + BiLSTM + CTC

[CRNN gốc](https://arxiv.org/abs/1507.05717) cung cấp hướng kiến trúc; dưới đây là thiết kế nhỏ của nhóm,
không tuyên bố tái hiện chính xác kiến trúc/thành tích bài báo.

| Bước | Tensor / cấu hình |
| --- | --- |
| Ảnh crop RGB | uint8 HxWx3, không text/bbox GT trong runtime input |
| Grayscale | round(0.299R+0.587G+0.114B), clamp uint8 |
| Resize/pad | H=32; wr=min(160,max(4,round(Wcrop*32/Hcrop))); resize bilinear 32xwr, pad phải bằng pixel127 lên160 |
| Normalize | float32 /127.5 -1; shape N x1 x32 x160 |
| CNN block1 | Conv3x3 pad1 1→64 +ReLU; MaxPool2x2 stride2 → N x64 x16 x80 |
| CNN block2 | Conv3x3 pad1 64→128 +ReLU; MaxPool2x2 stride2 → N x128 x8 x40 |
| CNN block3 | Conv3x3 pad1 128→256 +ReLU; MaxPool(2,1) → N x256 x4 x40 |
| CNN block4 | Conv3x3 pad1 256→256 +ReLU; MaxPool(2,1) → N x256 x2 x40 |
| Collapse height | Conv(2,1), no padding, 256→256 +ReLU → N x256 x1 x40 |
| Sequence | squeeze height, permute → N xT40 x256 |
| BiLSTM | 2 layers, hidden128 mỗi chiều, batch_first=True, output N x40 x256 |
| Head | Linear256→C68, log_softmax cuối → N x40 x68; transpose T40 xN x68 cho loss |

Ảnh quá rộng bị resize về 32x160 có distortion; report wr clipped rate, không warp bằng GT corners.
Toàn bộ T=40 timestep được tính, kể cả padding phải; `input_lengths=[40]*N`, cùng quy tắc lúc train và decode.
Không dùng ceil(wr/4) với CNN này mà chưa đổi contract, vì receptive field/padding cần kiểm riêng.
Targets là concatenated 1D int64 không blank, `target_lengths=[7]*N` MVP, mở rộng length8 version riêng.
L là độ dài target, R là số cặp ký tự bằng nhau kề nhau; cần **T>=L+R** để CTC có alignment.
T40 đủ với 7/8 ký tự kể cả repeat; vẫn test shape và bound, reject invalid sample trước loss.
`CTCLoss(blank=0,reduction='mean',zero_infinity=False)` baseline, tính log_softmax fp32,
target/input lengths đúng batch; padding target nếu dùng phải có length mask rõ. Không bật zero_infinity để giấu lỗi lengths.
Loss finite và backward nonzero trên batch synthetic/train là kiểm bắt buộc, không là benchmark recognition.

Greedy CTC: argmax từng t → collapse consecutive token lặp → xóa blank0.
Ví dụ `[A,A,blank,A,B,B] → AAB`; nếu xóa blank trước collapse sẽ sai repeated character.
Sentinel O của annotation bị loại khỏi training theo quarantine; CTC blank là token kỹ thuật riêng index0.
Decode không dùng luật biển/beam/GT dictionary để sửa output baseline.
Confidence OCR = trung bình max softmax trên timestep nonblank của greedy path,
null nếu không có nonblank; score không calibrated, chỉ diagnostic, không ngầm loại mẫu khỏi đánh giá.

## Giao diện cụ thể (chưa có implementation)

[interfaces.py](../../src/alpr/interfaces.py) chứa Protocol/dataclass, không sinh prediction.

```python
detect(image: RuntimeImage) -> Sequence[DetectionPrediction]
recognize(crops: Sequence[RuntimeCrop]) -> Sequence[OCRPrediction]
predict(image: RuntimeImage) -> PipelineResult
evaluate(predictions, ground_truth, *, split_manifest, mode) -> MetricReport
```

`RuntimeImage(sample_id, pixels)` và `RuntimeCrop(crop_id,sample_id,pixels)` chỉ chứa opaque IDs/pixels.
Detector return [] khi không có candidates; orchestrator phân biệt no_detection và low_confidence.
recognize giữ thứ tự input, trả một record/crop gồm empty/error status. predict trả đúng một result/ảnh,
gắn selected detection/OCR hoặc null, text empty cho failure. Batch wrapper bắt lỗi từng ảnh và giữ toàn bộ ID.
`MetricReport` dự kiến: mode, split_hash, Nimages, Ngt_chars, coverage, failure_counts,
metric objects gồm numerator/denominator/value/unit, model/config/charset hashes, per_image_artifact.
N=0 => value null + diagnostic; duplicate/unknown IDs là lỗi evaluator, không quietly inner-join.

Mode evaluator: detection; ocr_gt_bbox; ocr_pred_matched; pipeline_all. GT chỉ đi vào evaluator/trainer,
không nhận qua predict. Evaluator nối predictions/GT bằng sample_id, không row order và không parse path runtime.
Training dataset có thể dùng annotations được chuẩn bị hợp lệ; nguyên tắc pixel-only áp dụng inference.

## Checkpoint và khả năng nạp lại

Detector `.pt` cùng model manifest/Ultralytics version; B xác minh cách load phù hợp version đã pin.
CRNN `.pt`: dictionary gồm `format_version`, `architecture_id=crnn-small-v1`, `state_dict`,
`input_shape=[1,32,160]`, `time_steps=40`, `num_classes=68`, `blank_index=0`,
`charset_sha256`, `preprocess_version`, `decoder_version=greedy-ctc-v1`, training config hash, epoch và seed.
Optimizer/scheduler resume artifact riêng; final inference chỉ cần state_dict và metadata.
Checkpoint external metadata phải khớp manifest; không unpickle checkpoint không biết nguồn.
Load mismatch head/charset/blank/shape/preprocess/version/hash => từ chối rõ ràng trước inference,
không tự tải checkpoint thay thế hoặc âm thầm khởi tạo mạng random.
