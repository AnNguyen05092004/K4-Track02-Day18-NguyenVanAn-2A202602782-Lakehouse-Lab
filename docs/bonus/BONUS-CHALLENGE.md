# K4-Track02-Day18 — Bonus Tự Thiết Kế Lakehouse

> 🇬🇧 English version: [`BONUS-CHALLENGE-EN.md`](BONUS-CHALLENGE-EN.md)

**Loại:** Architecture brief mở — tách khỏi phần bắt buộc, hoàn toàn tự nguyện và **làm cá nhân**.
**Đối tượng:** Bạn vào vai *architect on-call*, không phải code-writer.
**Effort target:** 4–8 giờ tập trung. Không phải side-hustle — một buổi chiều suy nghĩ kỹ.

Bonus dành cho học viên muốn luyện quyết định kiến trúc và bảo vệ một thiết kế
trong design review. Bài được cộng **tối đa 10 điểm**, chấm riêng theo [RUBRIC.md](../RUBRIC.md);
điểm lab cuối cùng tối đa 100. Không làm bonus không mất điểm phần bắt buộc.

---

## Đề bài

Bạn vừa được giao một bài toán data-storage khó. Chọn một (hoặc tự định
nghĩa — quy tắc giống nhau). Viết **quyết định kiến trúc mà bạn sẽ bảo
vệ trong design review**. Code optional; **document is the deliverable**.

Cái chúng tôi muốn thấy là *judgment*: bạn có loại bỏ được những lựa chọn sai
hiển nhiên với lý do đúng không? *"Tôi xem xét Iceberg nhưng chọn Delta vì
**X**"* — đó là dạng câu trả lời chúng tôi muốn, không phải *"Delta tốt."*

---

## Topics gợi ý (chọn 1 — hoặc tự đặt)

Các topic là tình huống thiết kế giả định lấy cảm hứng từ bài toán công nghiệp;
số liệu là đầu vào của đề, không phải thống kê của một hệ thống đã xác minh.
Không topic nào có một lời giải duy nhất. Với ràng buộc pháp lý, tra cứu văn bản
đang áp dụng, ghi nguồn và phạm vi giả định trong bài; tên một luật không chứng minh thiết kế đã tuân thủ.

### A. LLM observability ở quy mô 1B requests/ngày
Một foundation-model API team log mọi request/response. **1B req/ngày,
~5 KB/req → 5 TB/ngày raw**. Họ cần: (1) dashboard cost & latency theo tenant,
refresh mỗi 5 phút; (2) prompt/response đầy đủ giữ 7 ngày để incident review,
sau đó chỉ giữ aggregates 1 năm; (3) PII redact trước khi bất kỳ ai đọc;
(4) tổng chi phí storage ≤ **\$5 K/tháng**.
*Concepts cần áp dụng:* medallion layout, retention/lifecycle, FinOps tiering,
PII tokenization tại Bronze, streaming ingestion, Z-order/clustering cho hot
path *"filter by tenant."*

### B. Trillion-token training corpus với provenance
Như RedPajama — **30 TB raw web crawl → 3 TB sau MinHash-LSH dedup → 1 TB
curated training set**. Mỗi shard có license tag (CC-BY, MIT, proprietary,
unknown). Khi có báo cáo contamination, bạn phải (a) chứng minh checkpoint nào
đã train trên shard nào, (b) revert shard đó trong vòng 30 phút, (c) re-train
downstream với corpus đã sửa. Hai region: scrape ở US, train ở EU.
*Concepts cần áp dụng:* Bronze→Silver→Gold curation, time travel + branching
(Nessie), catalog choice, multi-region replication semantics, training-data
provenance.

### C. CDC từ ride-hailing Việt Nam → Lakehouse với yêu cầu bảo vệ dữ liệu cá nhân
Production Oracle DB → Debezium CDC → Lakehouse cho analytics.
**100 triệu chuyến/năm, 30 K writes/giây ở peak.** PII của tài xế + hành
khách (số điện thoại, giấy tờ định danh, GPS) cần được bảo vệ. Đề bài dùng
**Nghị định 13/2023/NĐ-CP** làm điểm xuất phát để nghiên cứu; xác định thêm
văn bản đang áp dụng tại thời điểm thiết kế. SLA cho analyst: dashboard refresh trong 60 giây
kể từ source commit; ad-hoc query p95 < 1 giây. Sự kiện đến muộn xảy ra
thường xuyên (mất mạng ở tỉnh xa).
*Concepts cần áp dụng:* CDC + Delta CDF, SCD Type 2, late-data handling
(`MERGE WHEN MATCHED AND src.ts > tgt.ts`), tokenization tại Bronze landing,
audit table cho mọi lần đọc PII, lineage tooling.

### D. Multimodal RAG trên 10 triệu document pháp lý
Một văn phòng luật Việt Nam muốn RAG trên **10 triệu PDF** (text + ảnh scan
+ bảng). Embeddings sẽ được regenerate **ít nhất 2 lần** khi model upgrade.
Search latency p95 < 200 ms trên 30 tỉ tokens chunks. Versioning quan trọng:
khi một bản án trích dẫn version cụ thể của document, kết quả retrieval phải
*reproducible* sau 5 năm.
*Concepts cần áp dụng:* Delta vs Lance cho embeddings, embedding lifecycle &
versioning, multimodal storage layout, vector index choice (HNSW/IVF), RAG
freshness vs staleness.

### E. Lifecycle hot/warm/cold cho click-stream với FinOps cap cứng
Một consumer-app analytics team sinh ra **10 TB/ngày click events**.
Giả định đề bài yêu cầu retention 365 ngày. Budget storage của CFO là cap cứng
**\$8 K/tháng across all tiers**. Query trong 7 ngày gần nhất phải p95 < 2 s;
trong 90 ngày p95 < 30 s; > 90 ngày *"best effort, < 5 phút."*
*Concepts cần áp dụng:* partitioning strategy, S3 Standard / IA / Glacier
tiering, compaction cadence, OPTIMIZE schedule cost trade-offs, query-time
projection / column pruning.

### F. Catalog migration vendor-neutral, zero-downtime
Bạn được giao 500 Delta tables trong **Databricks Unity Catalog**, được
20 team dùng qua Spark, Trino, DuckDB, và Snowflake. Leadership muốn thoát
vendor lock-in: migrate sang **Apache Polaris** với zero query downtime,
giữ time-travel semantics, không broken dashboard. Bạn có 6 tuần.
*Concepts cần áp dụng:* REST Catalog spec, Iceberg ↔ Delta interop (UniForm,
Apache XTable), table renames vs registration-only, dual-write windows,
governance migration.

### G. Real-time feature store với column-level lineage
Một ngân hàng chạy **200 features × 10 K production models**. Risk team cần
trả lời trong < 5 phút: *"Nếu tôi drop column `customer.address_country`,
model nào bị broken và thiệt hại tiền là bao nhiêu?"* Features được tính bởi
~50 Spark jobs across 5 teams, daily backfills cho 90 ngày gần nhất.
*Concepts cần áp dụng:* OpenLineage + Marquez, data contracts, breaking-change
detection, feature-table layout, Bronze→Silver→Gold cho features, MERGE-based
backfills.

### H. Topic của riêng bạn
Định nghĩa một bài toán từ công việc hoặc lĩnh vực bạn quan tâm. Cùng quy tắc:
realistic scale numbers, real constraints, real trade-offs.

---

## Nộp gì

Một document, **3–6 trang** khi render (markdown OK), tại
`submission/bonus/ARCHITECTURE.md` cộng với code optional tại `submission/bonus/poc/`.

Dùng cấu trúc nào cũng được, nhưng document phải trả lời **đầy đủ các điểm
sau**:

1. **Problem statement** (≤ 200 từ). Numbers, constraints, vì sao khó.
2. **Architecture diagram.** Bronze→Silver→Gold layout, ingestion path,
   query path. ASCII art hoặc diagramming tool nào cũng được. Chỉ **một**
   diagram, thể hiện ít nhất 4 concept Day18 được áp dụng vào lựa chọn cụ thể.
3. **Quyết định chính, kèm alternatives đã loại.** Cho mỗi lựa chọn lớn
   (table format, catalog, partitioning, compression, lifecycle, governance),
   viết: *"Tôi chọn **A**. Tôi loại **B** vì [tradeoff]. Tôi loại **C**
   vì [tradeoff]."* Cần ít nhất 5 quyết định, mỗi quyết định có ít nhất 2 alternatives bị loại.
4. **Failure modes** (≥ 3). Cái gì hỏng lúc 3 giờ sáng? Bạn detect thế nào,
   và rollback ra sao? Ít nhất một failure mode phải tie với concept Day 18
   (time travel, schema evolution, deletion vectors, lineage).
5. **Ước lượng chi phí back-of-envelope.** \$/tháng cho storage + compute.
   Show the math. *"$X/TB-tháng × Y TB"* hơn đứt *"chắc rẻ thôi."*
6. **Bạn sẽ build cái gì trước** (slice MVP một tuần). Không phải toàn bộ —
   slice nhỏ nhất shippable chứng minh kiến trúc work, với tiêu chí nghiệm thu và
   cách kiểm tra mechanism khó nhất.

**PoC optional** (`submission/bonus/poc/`): một notebook ngắn (50–150 dòng)
demo một mechanism *non-trivial* trong design — ví dụ tokenization function
cho topic C, license-tag-aware MERGE cho topic B, embedding-version migration
cho topic D. Không phải implementation đầy đủ; một spike chứng minh phần khó
nhất là feasible.

---

## Thế nào là "tốt"

Bài được đánh giá theo rubric bonus tối đa 10 điểm. Các đặc điểm dưới đây là
self-checklist trước khi nộp; chi tiết điểm tại [RUBRIC.md](../RUBRIC.md):

| Dimension | "Tốt" trông như thế nào |
|---|---|
| **Quyết định kèm alternatives đã loại** | Ít nhất 5 quyết định chính, mỗi cái show ≥ 2 lựa chọn bị loại với tradeoff reasoning cụ thể. *"X nhanh hơn"* generic ≠ tradeoff. |
| **Constraints & numbers thực tế** | Scale, latency, budget figures xuất hiện *xuyên suốt* — không chỉ ở problem statement. Math kiểm tra được. |
| **Liên hệ tới concepts Day 18** | Medallion, ACID, time travel, catalogs, lineage, security, FinOps — ít nhất 4 trong số đó được *áp dụng*, không phải chỉ name-drop. |
| **Failure-mode rigor** | Kịch bản 3-giờ-sáng cụ thể với detection + rollback, không phải *"chúng tôi sẽ monitor."* |
| **Chất lượng PoC (nếu có)** | Nếu nộp: chạy được từ clean checkout; demo phần *khó* chứ không phải phần dễ. |

Thiết kế chỉ nêu tên công nghệ mà thiếu tradeoff và bằng chứng khả thi không
đáp ứng đầy đủ tiêu chí bonus. Code tùy chọn, nhưng phép tính và lập luận phải kiểm tra được.

---

## Bắt đầu thế nào (nếu bí)

1. Chọn topic. Bỏ **20 phút** sketch những gì đã có sẵn trong đầu — diagram,
   formats, partitions, catalog. Đừng research vội.
2. Liệt kê **5 thứ có thể làm vỡ** design lúc 3 giờ sáng. Cho mỗi thứ, viết
   rollback plan trong một câu.
3. *Bây giờ* mới đi xem lại slide §6–§8 (Industrial cases, Production ops)
   và để ý xem bạn đã quên trade-off nào.
4. Revise. Write. Nộp.

Bản sketch đầu tiên luôn sai. Bản thứ hai mới là *the work*.

---

## Submission

Nộp bài cá nhân tại `submission/bonus/ARCHITECTURE.md` trong cùng repo/PR với phần bắt buộc.
Dùng fork cá nhân của repo đề bài, bắt buộc đổi tên thành
`K4-Track02-Day18-HoVaTen-MSSV-Lakehouse-Lab`; bonus nằm trong fork đã dùng cho phần bắt buộc.
Tiêu đề PR: `[K4-Track02-Day18] HoVaTen - MSSV - Lakehouse Lab [+bonus]`.
Nơi nộp, deadline và checklist tại [SUBMISSION.md](../SUBMISSION.md).
