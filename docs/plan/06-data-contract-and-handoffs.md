# Hợp đồng dữ liệu và bàn giao A → B → C → D

Phiên bản **alpr-contract-v1**. [data-contract.json](data-contract.json) là JSON Schema Draft2020-12,
có `$defs` cho từng record. Đây là đặc tả phải triển khai, không phải xác nhận dataset đã tồn tại.
Tất cả field trong mỗi record đều required; null chỉ khi schema cho phép; không dùng "None" hoặc 0 thay null.
`additionalProperties=false`: đổi field phải đổi contract version hoặc decision migration.
JSON không NaN/Infinity, UTF-8 LF; text NFC; đơn vị tọa độ pixel trừ label YOLO normalized.

## Ownership và nhận bàn giao

| Điểm nối | Đầu ra phải có | Kiểm nhận trong 2h | Trách nhiệm khi thiếu |
| --- | --- | --- | --- |
| A → B | Source/data/split/charset manifests; annotations; YOLO labels; GT train/dev crops; metric fixtures; smoke20 | Hash, PK/FK, no-overlap, bbox overlay và một batch | G1 chưa đạt; lên lịch sửa chính thức, không mặc định A quay lại miễn phí |
| B → C | detect() callable; checkpoint/hash; env lock; dev detections + predicted crops; G1 bundle giữ nguyên | Reload offline, undo letterbox, crop IDs và coverage | G2 chưa đạt nếu thiếu artifact; C không tự viết lại detector |
| C → D | recognize()/predict() callable; CRNN checkpoint; frozen configs/evaluator; ablation artifacts; sample20 | Pixel-only inference, hashes, failure states và lệnh full-split | G3 chưa đạt; D không bắt đầu ghép core |
| D → người chấm | Demo, raw test predictions, số đo, báo cáo, release manifest | Checkout sạch, offline load, release inventory | G4 chỉ PASS khi đủ bằng chứng và ngưỡng đã freeze |

Người giao viết biên bản trước hết tuần mình; người nhận xác nhận trong quỹ tuần kế.
Nếu phát hiện đầu vào hỏng sau khi người giao kết thúc tuần: dùng reserve/decision đổi lịch hoặc giảm extension;
không đặt nghĩa vụ hỗ trợ ẩn. Không chuyển trạng thái gate thiếu dữ liệu thành đạt.

## Record và field chuẩn

Bảng dưới sinh từ cùng định nghĩa schema để giữ tên/kiểu/null đồng nhất.
`Annotation`, `Sample`, `OCRCrop.plate_text_nfc` và source locator là dữ liệu training/evaluator;
không truyền cả record này vào RuntimeImage. Trainer được nhận GT train hợp lệ, không cấm training labels.
`DetectorLabel` xuất một dòng `0 cx cy w h` cho mỗi GT plate, chuẩn hóa theo kích thước ảnh gốc,
`cx=(x1+x2)/(2W),cy=(y1+y2)/(2H),w=(x2-x1)/W,h=(y2-y1)/H`, width/height>0.


### Artifact

Đường dẫn tương đối, hash byte chính xác; không tự hash hoặc tạo vòng tham chiếu.

| Field | Kiểu / null |
| --- | --- |
| `path` | string |
| `sha256` | string |
| `size_bytes` | integer |
| `role` | enum runtime,train_label,dev_gold,test_gold,evidence,checkpoint,manifest |

### Annotation

Chỉ trainer/evaluator sử dụng. Gốc tọa độ trái trên; bbox half-open; corners trong ảnh gốc.

| Field | Kiểu / null |
| --- | --- |
| `bbox_xyxy` | array[number] |
| `corners_rb_lb_lt_rt` | array[array[number]] |
| `raw_bbox_xyxy` | array[integer] |
| `plate_indices` | array[integer] |
| `plate_text_nfc` | string |
| `source_locator` | string |

### Sample

Record chuẩn cho training/evaluator. RuntimeImage không nhận annotation hoặc source locator.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `sample_id` | string |
| `image_id` | string |
| `runtime_image_path` | string |
| `image_sha256` | string |
| `pixel_sha256` | string |
| `width_px` | integer |
| `height_px` | integer |
| `subset` | string |
| `split` | enum train,dev,test |
| `dedup_group_id` | string |
| `annotation` | Annotation |

### SplitManifest

Hash danh sách ID bằng JSON chuẩn hóa và sort ổn định; chốt trước tạo crop.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `protocol_version` | const alpr-custom-base-group-v1 |
| `data_version` | string |
| `seed` | const 42 |
| `sampling_version` | string |
| `dedup_version` | string |
| `source_manifest_sha256` | string |
| `members` | object |
| `counts` | object |
| `membership_sha256` | string |
| `quarantine_count` | integer |

### DetectorLabel

YOLO dùng tâm/kích thước chuẩn hóa theo ảnh gốc; nhãn số chỉ ở training/evaluation.

| Field | Kiểu / null |
| --- | --- |
| `sample_id` | string |
| `image_id` | string |
| `split` | enum train,dev,test |
| `class_id` | const 0 |
| `bbox_cxcywh_norm` | array[number] |
| `image_sha256` | string |

### OCRCrop

Crop lưu cho train/evaluation; runtime crop bỏ nhãn. Crop GT có detector hash=null. Kế thừa split ảnh cha.

| Field | Kiểu / null |
| --- | --- |
| `crop_id` | string |
| `sample_id` | string |
| `image_id` | string |
| `split` | enum train,dev,test |
| `crop_kind` | enum gt_bbox,pred_bbox,oracle_gt_corners,pred_corners |
| `path` | string |
| `sha256` | string |
| `bbox_xyxy` | array[number] |
| `parent_image_sha256` | string |
| `preprocess_version` | string |
| `detector_checkpoint_sha256` | string &#124; null |
| `plate_text_nfc` | string &#124; null |

### Charset

tokens[0]=<CTC_BLANK>; không có sentinel O; hash tokens theo JSON array UTF-8 compact +LF.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `charset_version` | string |
| `normalization` | const NFC |
| `blank_index` | const 0 |
| `tokens` | array[string] |
| `tokens_sha256` | string |
| `allowed_lengths` | array[enum 7,8] |

### DetectionPrediction

Tọa độ pixel ảnh gốc sau undo letterbox; score detector chưa hiệu chuẩn xác suất.

| Field | Kiểu / null |
| --- | --- |
| `sample_id` | string |
| `detection_id` | string |
| `class_id` | const 0 |
| `bbox_xyxy` | array[number] |
| `score` | number |
| `detector_checkpoint_sha256` | string |

### OCRPrediction

Confidence chỉ chẩn đoán, chưa hiệu chuẩn và không thay exact/CER. Output rỗng có confidence=null.

| Field | Kiểu / null |
| --- | --- |
| `sample_id` | string |
| `crop_id` | string |
| `text_nfc` | string |
| `confidence` | number &#124; null |
| `confidence_kind` | const mean_greedy_nonblank_maxprob |
| `decoder_version` | string |
| `recognizer_checkpoint_sha256` | string |
| `charset_sha256` | string |
| `status` | enum ok,ocr_empty,ocr_error |

### PipelineResult

Một record cho mỗi ảnh; mọi failure có text rỗng. Không có field GT. low_confidence nghĩa mọi bbox dưới ngưỡng.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `sample_id` | string |
| `status` | enum ok,low_confidence,no_detection,crop_error,ocr_empty,ocr_error,invalid_input,runtime_error |
| `selected_detection` | DetectionPrediction &#124; null |
| `ocr` | OCRPrediction &#124; null |
| `text_nfc` | string |
| `error_code` | string &#124; null |
| `latency_ms` | number &#124; null |
| `run_id` | string |

### SourceManifest

Template cho phép null; READY đòi revision/nguồn archive và inventory thật.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `manifest_version` | const alpr-manifest-v1 |
| `status` | enum TEMPLATE_NOT_A_RELEASE,READY |
| `created_at` | string &#124; null |
| `dataset_version` | const CCPD2019 |
| `upstream_url` | string |
| `upstream_commit` | string &#124; null |
| `archive_url` | string &#124; null |
| `archive_sha256` | string &#124; null |
| `license_reference` | string |
| `files` | array[Artifact] |

### DataManifest

Inventory dữ liệu sau QA; không tự hash. READY đòi counts/inventory thật.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `manifest_version` | const alpr-manifest-v1 |
| `status` | enum TEMPLATE_NOT_A_RELEASE,READY |
| `created_at` | string &#124; null |
| `data_version` | string |
| `source_manifest_sha256` | string &#124; null |
| `split_manifest_sha256` | string &#124; null |
| `charset_sha256` | string &#124; null |
| `parser_version` | string |
| `inventory` | array[Artifact] |
| `counts` | object |

### ModelManifest

Recognizer READY phải khóa charset/decoder và input shape qua config.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `manifest_version` | const alpr-manifest-v1 |
| `status` | enum TEMPLATE_NOT_A_RELEASE,READY |
| `created_at` | string &#124; null |
| `model_kind` | enum detector,recognizer |
| `architecture` | string |
| `framework_version` | string &#124; null |
| `checkpoint_sha256` | string &#124; null |
| `data_manifest_sha256` | string &#124; null |
| `split_manifest_sha256` | string &#124; null |
| `config_sha256` | string &#124; null |
| `charset_sha256` | string &#124; null |
| `preprocess_version` | string |
| `decoder_version` | string &#124; null |
| `artifacts` | array[Artifact] |

### RunManifest

READY đòi ID, hash, lệnh, môi trường và bằng chứng; metric chưa đo phải giữ null và ghi rõ.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `manifest_version` | const alpr-manifest-v1 |
| `status` | enum TEMPLATE_NOT_A_RELEASE,READY |
| `created_at` | string &#124; null |
| `stage` | enum data,detector,recognizer,pipeline |
| `run_id` | string &#124; null |
| `git_commit` | string &#124; null |
| `seed` | const 42 |
| `mode` | enum train,dev,test,latency |
| `source_manifest_sha256` | string &#124; null |
| `data_manifest_sha256` | string &#124; null |
| `split_manifest_sha256` | string &#124; null |
| `config_sha256` | string &#124; null |
| `charset_sha256` | string &#124; null |
| `detector_checkpoint_sha256` | string &#124; null |
| `recognizer_checkpoint_sha256` | string &#124; null |
| `hardware` | object |
| `environment_lock_sha256` | string &#124; null |
| `commands` | array[string] |
| `test_exposure` | array[string] |
| `metrics` | object |
| `artifacts` | array[Artifact] |

### ReleaseManifest

Tách runtime allowlist khỏi nhãn train/eval; đồ thị hash không vòng và không tự tham chiếu.

| Field | Kiểu / null |
| --- | --- |
| `contract_version` | const alpr-contract-v1 |
| `manifest_version` | const alpr-manifest-v1 |
| `status` | enum TEMPLATE_NOT_A_RELEASE,READY |
| `created_at` | string &#124; null |
| `release_id` | string &#124; null |
| `git_commit` | string &#124; null |
| `protocol_version` | const alpr-custom-base-group-v1 |
| `frozen_run_manifest_sha256` | string &#124; null |
| `source_manifest_sha256` | string &#124; null |
| `data_manifest_sha256` | string &#124; null |
| `split_manifest_sha256` | string &#124; null |
| `config_sha256` | string &#124; null |
| `charset_sha256` | string &#124; null |
| `detector_checkpoint_sha256` | string &#124; null |
| `recognizer_checkpoint_sha256` | string &#124; null |
| `runtime_inventory` | array[Artifact] |
| `evaluation_inventory` | array[Artifact] |
| `gate_decisions` | object |

## Invariant liên record và điều kiện từ chối

- sample_id=image_id là opaque ID duy nhất; basename runtime không chứa annotation.
- Bbox: 0<=x1<x2<=W, 0<=y1<y2<=H, float pixel half-open; corners theo RB/LB/LT/RT.
- Mọi sample ID, pixel hash, dedup group và chuỗi plate NFC không giao nhau giữa các split.
- Chia split trước; crop/augmentation kế thừa ảnh cha, FK crop.sample_id phải resolve được.
- RuntimeImage/RuntimeCrop chỉ nhận pixel và ID. Trainer dùng GT train hợp lệ; test gold chỉ evaluator.
- NFC duy nhất. Sentinel O bị quarantine; blank0 không là target; charset/hash khớp output head.
- CTC T40, target7 baseline hoặc8 mở rộng; T>=L+repeat; input_lengths40 kể cả padding.
- Không dùng GT corners trong inference; oracle phải tách khỏi headline E2E.
- Failure pipeline có text rỗng; no_detection/low_confidence có selected_detection=null và ocr=null.
- READY từ chối schema/version/hash/architecture/shape/decoder không tương thích.
- SHA256 theo byte; hash tập ID theo JSON sort UTF-8 compact LF; manifests không vòng.
- TEMPLATE cho phép null nhưng loader phải từ chối; READY inventory không rỗng.

## Đơn vị, hash và lifecycle

Sample.image_id=sample_id UUIDv4 sinh trong chuẩn bị rồi pin manifest; ID không chứa plate/text/bbox.
image_sha256 là byte file nguồn runtime; pixel_sha256 là SHA256 của `uint32 big-endian H,W` nối RGB uint8 row-major,
không gồm tên/metadata. Cùng pixel khác encoding vẫn có cùng pixel hash; same source có thể khác byte hash.
Paths tương đối dưới release root; cấm absolute path, `..`, symlink thoát root; resolver không tự quét raw/evaluation.
Metadata runtime chỉ ID, width/height lấy từ pixels; không source filename, nhãn, corners hoặc split gold.

Dataset hash giữ trong data manifest (inventory artifacts + counts + contract version; không self-hash).
Split hash là hash file manifest cuối cùng; membership hash là JSON object train/dev/test với IDs sort,
UTF-8 compact separators, LF cuối. Config hash theo exact YAML bytes đã freeze;
charset hash là array tokens JSON UTF-8 compact +LF, checkpoint hash là exact file bytes.
Run manifest trỏ các hash này, release manifest hash các manifest con. Không có vòng self-reference.

READY loader phải từ chối template, thiếu file, sai size/hash, sai contract/version, charset/head không khớp,
normalization/blank/shape/time/decoder khác, split/config khác frozen release hoặc inventory chứa role cấm.
Runtime inventory chỉ checkpoint/config/charset/runtime images và metadata pixel cần thiết;
không Annotation, raw source locator, filename CCPD, train labels, dev/test gold hoặc expected output.
Academic package có thể chứa evaluation inventory riêng nhưng predict() không đọc thư mục đó.

Low confidence: detector có bbox nhưng tất cả dưới conf runtime => status low_confidence, text empty;
không có candidate => no_detection. Bbox không hợp lệ/crop rỗng => crop_error, không fallback GT crop.
OCR decode rỗng => ocr_empty; lỗi tensor/decoder => ocr_error; invalid pixels => invalid_input;
lỗi bất ngờ => runtime_error. Các lỗi có error_code, text empty và vẫn tính vào E2E/CER.
`ok` yêu cầu selected_detection, OCR status ok và text nonempty; score OCR thấp chỉ hiển thị diagnostic,
baseline không abstain thêm bằng OCR confidence. Không nối chuỗi từ nhiều bbox.
Nếu GT text không supported trong data preparation thì quarantine trước freeze, không xóa ký tự để làm label hợp lệ.

Xem [CTC/API](08-architecture-and-interfaces.md), [parser/split](07-dataset-and-evaluation-protocol.md)
và [test specification](11-test-specification.md). Validator kế hoạch chỉ kiểm schema/template/cross-document;
acceptance suite data/model thực tế do A/B/C/D triển khai sau, gồm mọi invariant liên record trên.

RunManifest.stage phân biệt data/detector/recognizer/pipeline: checkpoint chưa có ở giai đoạn data được null; detector READY đòi detector hash; recognizer READY đòi recognizer hash; pipeline READY đòi cả hai. created_at là ISO8601 UTC, size_bytes đơn vị byte, latency_ms đơn vị mili giây.
