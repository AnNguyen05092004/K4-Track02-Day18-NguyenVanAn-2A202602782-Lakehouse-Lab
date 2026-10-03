# K4-Track02-Day18 — Checkpoints

Đi theo 8 notebook lightweight trong `notebooks/`. Với NB1–NB4 có thể dùng bản
Spark tương ứng; NB5–NB8 dùng lightweight. Mỗi checkpoint cần output thực tế,
bằng chứng và phần giải thích theo [RUBRIC.md](RUBRIC.md).

Chạy các lệnh từ **thư mục gốc repo**. Tài liệu nằm trong `docs/`, còn mã thực thi
và dữ liệu vẫn dùng đường dẫn từ gốc repo như trong các ví dụ.

## Checkpoint 0 — Chuẩn bị môi trường

- **Làm:** theo [README.md](../README.md), cài dependencies và chạy `make smoke`.
  Trên PowerShell dùng `.\.venv\Scripts\python.exe scripts/verify_lite.py`.
- **Sản phẩm:** môi trường Python và output smoke test thành công.
- **Cần hiểu:** Delta/Iceberg là định dạng bảng; DuckDB/Polars là công cụ đọc và xử lý.
  Đường lightweight không cần mạng khi thực thi sau khi cài dependencies.
- **Tự kiểm tra:** các bước smoke đều PASS; xác định được nơi lưu `_lakehouse/`.

## Checkpoint 1 — Delta basics

- **Làm:** chạy `01_delta_basics`; tạo bảng, thử ghi sai kiểu, rồi thêm `tier` bằng schema merge.
- **Sản phẩm:** bảng Delta, nội dung một commit JSON trong `_delta_log/`, output lỗi ghi sai kiểu
  và schema sau evolution.
- **Cần hiểu:** log ghi nhận transaction; enforcement chặn schema không hợp lệ;
  evolution phải được cho phép rõ ràng.
- **Tự kiểm tra:** có ít nhất 2 commit JSON; ghi `age='thirty'` bị chặn; có cột `tier`
  và 2 nhóm tier khi query. Kiểm tra output lỗi thực tế, không chỉ dòng PASS cuối notebook.

## Checkpoint 2 — Compaction và Z-order

- **Làm:** chạy `02_optimize_zorder`; ghi nhận số file và truy vấn trước/sau tối ưu.
- **Sản phẩm:** ít nhất 100 file ban đầu, số file sau tối ưu, speedup, pruning ratio
  và min/max `user_id` của các file sau Z-order.
- **Cần hiểu:** compaction giảm số file; Z-order gom dữ liệu để stats hỗ trợ file skipping.
  Nếu gộp hết vào một file thì không còn nhiều file để prune.
- **Tự kiểm tra:** số file giảm; speedup ≥ 3× **hoặc** pruning ratio ≥ 10×.
  Giải thích vì sao thời gian chạy có thể biến động theo máy.

## Checkpoint 3 — Time travel và MERGE

- **Làm:** chạy `03_time_travel`; tạo lịch sử, MERGE 100K dòng và RESTORE về trạng thái trước dữ liệu lỗi.
- **Sản phẩm:** output MERGE, query version cũ, history sau RESTORE và số dòng `score < 0`.
- **Cần hiểu:** MERGE có thể update/insert; RESTORE tạo transaction mới, không xóa lịch sử cũ.
- **Tự kiểm tra:** history có ≥ 5 version, gồm MERGE và RESTORE; không còn dòng `score < 0`
  trong version hiện tại.

## Checkpoint 4 — Bronze → Silver → Gold

- **Làm:** chạy `04_medallion`; sinh Bronze nếu thiếu, parse/dedup Silver và tổng hợp Gold.
- **Sản phẩm:** ba bảng trên storage; số dòng Bronze/Silver; bảng Gold theo ngày và model.
- **Cần hiểu:** Bronze giữ dữ liệu thô; Silver chuẩn hóa và khử trùng;
  Gold phục vụ câu hỏi về latency, lỗi và chi phí. Chi phí dùng giá minh họa của lab.
- **Tự kiểm tra:** Silver < Bronze; Gold phủ ≥ 7 ngày × 3 model; p50 ≤ p95;
  `cost_usd` có giá trị dương và `error_rate` nằm trong [0, 1]. Kiểm tra output Gold
  vì notebook chưa assert toàn bộ các yêu cầu này.

## Checkpoint 5 — Iceberg và catalog

- **Làm:** chạy `05_iceberg_catalog`; tạo bảng qua catalog, partition bằng `day(ts)`,
  lọc trên `ts`, đổi tên field và thay partition spec.
- **Sản phẩm:** pruning ratio, metadata tree và tỷ lệ metadata:data;
  field ID trước/sau rename và các spec ID đang dùng.
- **Cần hiểu:** hidden partitioning suy ra partition từ cột nguồn; field ID giữ định danh
  khi rename; partition evolution cho phép nhiều layout cùng tồn tại.
- **Tự kiểm tra:** pruning ≥ 5×; `latency_millis` giữ field ID 4;
  ≥ 2 spec ID và toàn bộ dữ liệu vẫn đọc được.

## Checkpoint 6 — Maintenance

- **Làm:** chạy `06_maintenance`; đo compaction, clustering, vacuum/expiry,
  orphan removal và checkpoint.
- **Sản phẩm:** số trước/sau từng job; bằng chứng xóa 3 Delta orphan;
  Iceberg còn 3 snapshots và manifest lists không còn được tham chiếu đã được dọn;
  checkpoint Parquet cùng `_last_checkpoint`.
- **Cần hiểu:** file không còn được tham chiếu và file đã bị xóa vật lý là hai trạng thái khác nhau;
  maintenance phải tính đến retention và các reader/writer đang chạy.
- **Tự kiểm tra:** compaction giảm ≥ 10× file; clustering skip ≥ 50%; vacuum thu hồi bytes;
  dữ liệu hiện tại còn nguyên. Chỉ dùng retention 0 với dữ liệu scratch của lab.

## Checkpoint 7 — Multimodal và vectors

- **Làm:** chạy `07_vectors_multimodal`; so inline blob/pointer, float32/int8,
  SQL semantic search và xóa dữ liệu khi external index chưa đồng bộ.
- **Sản phẩm:** amplification, tỷ lệ dung lượng, recall@10, topic fidelity,
  kết quả tìm kiếm và CDF delete events.
- **Cần hiểu:** column pruning và random access có chi phí khác nhau;
  embeddings là dữ liệu có vòng đời; external index phải nhận cả sự kiện delete.
- **Tự kiểm tra:** amplification ≥ 5×; int8 nhỏ ≥ 3×; recall@10 ≥ 0.80;
  topic fidelity ≥ 0.95; dữ liệu đã xóa có 0 hits trong bảng nhưng > 0 hits ở index cũ.

## Checkpoint 8 — Agents và provenance

- **Làm:** chạy `08_agents_provenance`; tạo trajectory medallion, pin version,
  thử lớp MCP mô phỏng, phân loại nguồn dữ liệu và xóa subject.
- **Sản phẩm:** Silver có 2 partition `agent_version`, Gold cho 2 policy;
  training run pin version; output cache/confirmation/task;
  4 bucket provenance và partition `UNCLASSIFIED`.
- **Cần hiểu:** version pin giúp tái lập dữ liệu training; provenance phải được ghi từ ingest;
  delete ở version hiện tại chưa xóa bản cũ. MCP ở đây là lớp mô phỏng offline,
  không phải server hay cơ chế xác thực production. Cache được đo ở `list_tables`,
  không phải `tools/list`; cờ `confirmed` do bên gọi truyền nên không ngăn agent tự xác nhận.
  Replay hiện chỉ kiểm tra số bước, chưa so sánh toàn bộ nội dung.
  Các bucket là quy tắc phân loại minh họa, không phải bốn nhóm bắt buộc của luật.
  Mapping hiện tại gán CC-BY-4.0 vào `public_domain` dù đây là giấy phép có điều kiện
  ghi công; `user-owned` + consent cũng chưa chứng minh đã kiểm tra opt-out khi scraping.
  Không dùng mapping này để kết luận quyền sử dụng dữ liệu thật.
- **Tự kiểm tra:** replay có số bước khớp version đã pin; 5 lượt list chỉ đọc catalog 1 lần;
  destructive call chưa xác nhận trả `input_required`; task hoàn tất;
  trainable set loại `UNCLASSIFIED`; subject không còn ở version hiện tại.

## Checkpoint 9 — Hoàn thiện bài nộp

- **Làm:** chạy `make test`, `make run-all`; thực thi notebook trong Jupyter để giữ output;
  chuẩn bị ảnh và reflection theo [SUBMISSION.md](SUBMISSION.md).
- **Sản phẩm:** 8 `.ipynb` có output trong `submission/notebooks/`, screenshots,
  reflection và thông tin người nộp.
- **Cần hiểu:** `run_all.py` chạy scripts để kiểm tra, không lưu output vào `.ipynb`.
- **Tự kiểm tra:** xem `git status` và repo đã push; các file bài nộp phải hiện trên GitHub,
  không chỉ tồn tại trên máy. Đối chiếu từng tiêu chí [RUBRIC.md](RUBRIC.md).

## Nguồn đối chiếu cho NB8

- [MCP revision 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28/): protocol thực tế; lớp trong notebook chỉ mô phỏng một số ý tưởng.
- [EU AI Act, Article 10 — bản hợp nhất 27/07/2026](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727): data governance cho hệ thống thuộc phạm vi áp dụng; không quy định bốn bucket của lab.
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): giấy phép có yêu cầu ghi công, khác với public domain.
