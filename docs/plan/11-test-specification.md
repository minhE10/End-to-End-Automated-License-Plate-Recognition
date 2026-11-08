# Đặc tả kiểm thử ALPR cần triển khai

Hiện **chưa có test/model ALPR thực thi**. `scripts/validate_plan.py` kiểm tài liệu, không chứng nhận các ca dưới đã pass.
Fixtures synthetic hoặc train/dev; không lấy test images làm regression tuning. Khi triển khai, pytest hoặc unittest đều được.

| Nhóm | Chủ sở hữu | Ca có ý nghĩa / expected behavior |
| --- | --- | --- |
| Parser | A | Filename nguồn mẫu → 皖AY339S; bbox154,383,386,473; corners RB,LB,LT,RT đúng thứ tự |
| Parser invalid | A | Sai7 fields, âm/out-of-range indices, sentinel O, unsupported length8, bbox ngược, corrupt image → quarantine có reason |
| Split | A | Duplicate byte/decoded pixel, same plate, near-pair thành chain union → chỉ một split; crop giữ parent split |
| Pixel hash | A | Cùng RGB/dim khác tên/encoding → cùng pixel hash; khác dimensions hoặc pixel → khác hash |
| Charset | A/C | Index0 province không thành CTC blank; head68; tokens/hash/NFC đúng; sentinel không target |
| Metrics | A | GT ABC, pred ADC => edit1, CER1/3; GT AA pred empty => edit2; micro (1+2)/(3+2)=0.6 |
| Detection | A/B | Identity IoU1, disjoint0, boundary half-open, duplicate detection chỉ match GT một lần |
| CTC | A/C | [A,A,blank,A,B,B]→AAB; all blank→empty; T<L+repeat reject; shape T40 và target không blank |
| CRNN loss | C | Batch có repeated target, finite CTCLoss/backward, gradient nonzero; mismatch charset checkpoint reject |
| Pipeline | B/C | Top1 tie policy stable; undo letterbox; conf miss; crop clamp/error; OCR empty/error không crash batch |
| Evaluator | C/D | 3 ảnh gồm 1 correct, 1 miss, 1 wrong → E2E1/3; miss đóng đủ GT deletions trong CER |
| Evaluator coverage | C/D | Missing prediction tính empty/fail và báo lỗi; duplicate/unknown IDs fail; Nmatched0 => conditional null |
| Anti-leak | C | Đổi basename và ID giữ pixel, label giả trong tên → text/bbox/status không đổi; inference không import parser/GT |
| Artifacts | B/C/D | Thiếu/mismatch checkpoint/config/data/split/charset hash, TEMPLATE status, path traversal → reject load |
| Demo | D | 6 fixture G4.1, offline reload; không tự tải model/network hoặc giấu ảnh lỗi |

Ngưỡng tối thiểu fixture tổng G1.5 >=20 và G3.1 >=8 không thay coverage các nhóm bắt buộc.
Đếm fixture thực tế và expected assertion; không tạo nhiều bản cùng một test chỉ để đạt số lượng.
