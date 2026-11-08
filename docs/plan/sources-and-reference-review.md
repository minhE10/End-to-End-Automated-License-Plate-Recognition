# Nguồn và cách vận dụng repo tham khảo

Đọc ngày 08/11/2026, bằng `git show` và `git ls-tree`, không checkout/sửa repo mẫu.
Repo local: `F:/HUST/20261/WebMining/Solving-the-Semantic-Attribute-Gap-in-E-Commerce-Product-Search`.

| Ref | Commit đã đọc | Nội dung áp dụng |
| --- | --- | --- |
| main | ffc228b0f3a6bde7ccc3bb6994fb45ac3aa6059d | README rất ngắn, dùng root làm điểm vào tài liệu |
| origin/plan | 1fd661e68e84f5a2cef0310e565b44304740fc10 | docs/plan/00–06, tuần 1–4, JSON, CSV, config, template, build_plan.py |
| origin/feature/data_processing | e7b41a9e640711d1bd662b4fe60f750517dd8755 | src/, data/, evaluation/, manifests/, handoff/, reports/, README, smoke guide |

Không tìm thấy AGENTS.md trong cây ba ref hoặc các thư mục cha workspace đã kiểm.
Đọc thêm handoff W1_A_to_B, runtime manifest và config của nhánh data_processing.
Nhánh triển khai có artifact/số đo riêng; chúng không chứng minh tiến độ ALPR.
Giữ gate có số đo/bằng chứng, manifest bất biến, runtime/evaluator tách biệt, smoke offline và trách nhiệm người nhận.
Đổi toàn bộ schema sang ảnh/bbox/crop/chuỗi/CTC; không dùng lại ontology/retrieval metric của dự án cũ.

## Nguồn kỹ thuật chính thức

- [CCPD README](https://github.com/detectRecog/CCPD): phiên bản 2019, Green bổ sung 2020, filename annotation,
  mapping và protocol một biển mỗi ảnh. Ngày đọc 08/11/2026; chưa pin commit upstream hoặc tải archive.
- [CCPD split](https://github.com/detectRecog/CCPD/tree/master/split): đối chiếu official protocol;
  MVP dùng custom split đã đặt tên riêng, không so trực tiếp bảng kết quả chính thức.
- [CCPD loader nguồn](https://github.com/detectRecog/CCPD/blob/master/rpnet/load_data.py): đối chiếu bbox/index,
  chỉ tham khảo chuẩn bị dữ liệu; không đưa parser filename vào inference.
- [Bài báo CCPD](https://openaccess.thecvf.com/content_ECCV_2018/html/Zhenbo_Xu_Towards_End-to-End_License_ECCV_2018_paper.html):
  Xu et al., ECCV 2018, nguồn gốc dataset và baseline; không lấy kết quả bài báo làm cam kết nhóm.
- [YOLOv8](https://docs.ultralytics.com/models/yolov8/) và
  [Ultralytics v8.3.0](https://github.com/ultralytics/ultralytics/releases/tag/v8.3.0):
  chọn YOLOv8n thay vì dò nhiều kiến trúc, nhỏ và có adapter detection sẵn; phiên bản baseline được đề xuất cố định.
- [CRNN](https://arxiv.org/abs/1507.05717): Shi, Bai, Yao, CNN + recurrent sequence modeling + transcription.
- [PyTorch CTCLoss source v2.5.1](https://github.com/pytorch/pytorch/blob/v2.5.1/torch/nn/modules/loss.py):
  API log-probabilities `(T,N,C)`, input/target lengths và blank. Công thức shape/time cụ thể là thiết kế của nhóm.

A phải ghi commit CCPD, URL tải thật, ngày tải, SHA-256, phiên bản archive và license trong source manifest.
Chưa pin upstream không được trình bày là đã có provenance của dữ liệu.
Phiên bản thư viện training là đề xuất để pilot, không phải dependency lock đã kiểm.
