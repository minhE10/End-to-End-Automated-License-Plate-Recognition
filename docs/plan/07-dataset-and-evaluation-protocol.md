# CCPD, parser và protocol chống rò rỉ

## Phiên bản và phạm vi

Nguồn: [CCPD chính thức](https://github.com/detectRecog/CCPD),
[loader](https://github.com/detectRecog/CCPD/blob/master/rpnet/load_data.py),
[split](https://github.com/detectRecog/CCPD/tree/master/split).
MVP dùng archive **CCPD2019**, subset `ccpd_base`, 7 ký tự. Nguồn có bổ sung Green năm 2020, biển 8 ký tự;
Green chỉ mở rộng version dữ liệu/allowed_lengths và báo metric riêng, không trộn ngầm vào Base.
Chưa tải archive; A phải pin upstream commit/archive URL/hash và xác minh inventory trước G1.

Protocol nhóm **alpr-custom-base-group-v1**, seed42, không dùng official split cho headline MVP.
Official README dùng Base cho train/val và các subset khó cho test; protocol detection gốc chọn 1 bbox và IoU>0.7.
Nhóm dùng Base group split và P/R/AP@0.50 cùng mAP50-95; vì khác dữ liệu lẫn metric nên không tuyên bố so ngang benchmark gốc.
Nếu chạy official protocol bổ sung, dùng manifest riêng, metric joint@0.7 với bất đẳng thức đúng nguồn,
không đổi tên kết quả custom thành official.

| Mức | Train | Dev | Test | Dùng để |
| --- | ---: | ---: | ---: | --- |
| Mục tiêu | 20.000 | 2.000 | 2.000 | Chất lượng baseline, nếu đủ dung lượng/GPU |
| Tối thiểu | 5.000 | 500 | 500 | MVP nhỏ, vẫn group-disjoint |
| Pilot từ split đã khóa | 1.000 | 200 | Không có pilot test | Tốc độ/VRAM và dev sanity |

Đây là số mẫu mục tiêu, chưa phải counts đã quan sát. Test được chọn trước huấn luyện, giữ nguyên trong suốt pilot/scaling.
Nếu giảm từ mục tiêu xuống tối thiểu: chỉ lấy train/dev subset theo thứ tự seed cố định; test đã freeze giữ nguyên
nếu đã đủ tải. Nếu buộc đổi test inventory do nguồn lỗi trước exposure thì tạo protocol/split version mới và decision.

## Parser filename chỉ dành cho data/evaluator

Tên nguồn tách đuôi extension rồi split `-` thành đúng 7 field:
area ratio, tilt horizontal/vertical, bbox, 4 corners, plate indices, brightness, blur.
Area/tilt/brightness/blur giữ raw field cho stratification; không dùng chúng làm feature inference.
Không giả định đơn vị số metadata nếu chưa xác minh trong archive/paper; bin khó định nghĩa bằng quantile train
và pin ngưỡng trong manifest, không điều chỉnh theo kết quả test.

1. Bbox field `x1&y1_x2&y2`, corners bốn `x&y` theo **RB → LB → LT → RT**;
   nguồn tọa độ ảnh gốc, x ngang/y dọc, origin góc trái trên. Preserve raw để audit.
2. Canonical bbox float `[x1,y1,x2,y2)` half-open. Vì nguồn dùng hiệu `right-left`, baseline không cộng 1;
   A kiểm overlay 100 ảnh trước freeze, nếu điều chỉnh convention phải version/parser và regenerate mọi crop/label.
3. Clip rounding chỉ khi tạo crop: left/top=floor, right/bottom=ceil, clamp [0,W]/[0,H].
   Annotation ngoài bounds hoặc x1>=x2/y1>=y2 bị quarantine, không lặng lẽ sửa nhãn; prediction out-of-bounds
   được clamp trong runtime với log; nếu còn rỗng => crop_error. Corners invalid/self-intersect bị quarantine.
4. Plate indices: vị trí0 dùng provinces, vị trí1 dùng alphabets, còn lại dùng ads.
   Mapping đầy đủ nằm ở `x-annotation-mapping` trong [JSON contract](data-contract.json).
   Kiểm index không âm/không vượt giới hạn, dài7 MVP. Đối chiếu sample chính thức:
   `0_0_22_27_27_33_16` → `皖AY339S` (fixture nguồn, không phải prediction).
5. Ký tự cuối bảng nguồn là chữ **O sentinel “không ký tự”**, không phải số0.
   Sentinel không phải CTC blank, không target hợp lệ; quarantine với reason=sentinel_annotation.
   Không xóa sentinel rồi gán nhãn ngắn hơn. Index0 province là 皖, không phải blank.
6. UTF-8, normalize NFC duy nhất; không đổi case/strip ký tự để sửa nhãn. Charset `ccpd67-v1` có
   33 token tỉnh/đặc biệt +24 chữ Latin (không I/O) +10 số; CTC thêm blank0 => head68.
   [Charset mẫu](templates/charset.example.json) là thiết kế vocabulary, không lấy từ test.
7. Ảnh decode lỗi, dimensions sai, filename sai field, bbox/corners/index lỗi, length8 trong MVP,
   unsupported token => quarantine JSONL gồm source locator/hash/reason/parser_version; báo counts từng reason.
   Lấy mẫu audit quarantine bằng train/dev hoặc source QA trước freeze; không chọn test dễ hơn qua kết quả model.

## Split, dedup và giới hạn cùng xe

A lập inventory ảnh nguồn một lần, sample_id UUID opaque và source mapping chỉ trong evaluator/preparation.
Chạy trước sampling/split: SHA256 file, hash decoded RGB; pHash64 toàn ảnh và plate crop GT cho candidate near-duplicate,
Hamming<=4 dùng tìm candidate, không tự coi mọi candidate là trùng. Review candidate pairs và ghi bằng chứng;
đồng thời union mọi ảnh có plate_text NFC trùng. Toàn connected component thành dedup_group_id.
Exact duplicate giữ representative theo source locator sort, log alias/lý do loại; near-duplicate giữ cùng nhóm,
không cần xóa hết. Ảnh augmentation chưa được sinh ở bước này.

Để tránh O(N²) toàn dataset, A dùng hash bucket/BK-tree hoặc indexing theo pHash và review candidates trên pool Base
đã chọn rộng hơn quota. Sampling chỉ từ component và pin pool hash; nói rõ kiểm near-duplicate giới hạn trong pool,
không tuyên bố chống rò toàn CCPD. Candidate chưa phân xử thì gộp bảo thủ hoặc quarantine, không tách qua split.
Biển giống nhau nối nhóm kể cả góc/độ sáng khác. Điều này giảm text memorization nhưng không chứng minh cùng xe:
không có vehicle ID đáng tin để phát hiện xe đổi biển/nhãn sai hoặc mọi cảnh gần trùng.

Thứ tự deterministic: sort group ID, RNG seed42 shuffle; phân nhóm vào test, dev, train theo quota ảnh xấp xỉ,
giữ nguyên component, cho phép vượt quota do kích thước nhóm và ghi actual N.
Chọn thêm nhóm từ cùng pool nếu thiếu minimum, không bẻ component; log phân bố province/blur/tilt/brightness.
Leakage report bắt buộc pairwise train-dev/train-test/dev-test: overlap sample, byte hash, pixel hash,
dedup group và text phải 0; unresolved near-duplicate cross-split phải 0.
Chỉ sau đó crop, augment train và export detector labels. Crop/augment kế thừa parent split.
Không shuffle tất cả crop rồi split lại.

## Ranh giới nhãn và test exposure

Trainer được nhận GT train, dev evaluator nhận dev GT để chọn model, early stop và tham số.
A cần parse test nguồn để chuẩn bị split và audit tự động overlap; không dùng test pixels/labels để thiết kế augmentation,
chọn model/decoder hoặc manual QA chọn ảnh đẹp. Tạo test bundle riêng, exposure log ghi A đã thấy metadata lúc chuẩn bị.
B/C không được dùng test labels; D chỉ mở sau frozen checkpoint/config/decoder/split hashes.

Preparation copy/re-encode lossless nếu cần để có basename UUID, ghi hash pixel trước/sau và metadata encoding;
runtime loader nhận pixels RGB + ID, không source filename hoặc raw path chứa annotation.
Test renaming: 100 dev images, giữ pixel y hệt, đổi basename và opaque ID, chạy predict 2 lần;
bbox/score/text/status không đổi (bỏ trường ID); deterministic CUDA nếu có hoặc tolerance score<=1e-6 đã freeze,
text và status phải exact. Thêm test các filename cố ý chứa GT sai để bắt code parse lén.
Runtime dependency graph không import parser, không đọc evaluator gold hoặc raw cache.
Không sử dụng GT corners ở pipeline. Warp GT corners là oracle thí nghiệm riêng nếu còn thời gian.
