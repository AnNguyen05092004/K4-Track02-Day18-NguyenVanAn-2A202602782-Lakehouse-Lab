# Day 18 — Lakehouse Lab (Track 2)

Lab cho **AICB-P2T2 · Ngày 18 · Data Lakehouse Architecture**.
Mục tiêu: build Bronze → Silver → Gold pipeline với Delta Lake trên local
object storage (MinIO), không cần tài khoản cloud.

## Học sau khi hoàn thành

| Notebook | Skill | Slide section |
|---|---|---|
| `01_delta_basics.py` | Write/read Delta table, schema enforcement, transaction log | §2 Delta Lake |
| `02_optimize_zorder.py` | Small-file problem; OPTIMIZE + ZORDER benchmark | §5 Storage Optimization |
| `03_time_travel.py` | versionAsOf, timestampAsOf, RESTORE, MERGE, DESCRIBE HISTORY | §3 Time Travel |
| `04_medallion.py` | LLM-observability Bronze→Silver→Gold pipeline | §6 Lakehouse cho AI/ML |

## Setup (5 phút)

**Yêu cầu:** Docker Desktop ≥ 4.x (~4 GB RAM cho Spark container).

```bash
git clone https://github.com/VinUni-AI20k/Day18-Track2-Lakehouse-Lab.git
cd Day18-Track2-Lakehouse-Lab
docker compose -f docker/docker-compose.yml up -d
```

Sau khi `up`:
- **Jupyter Lab** → http://localhost:8888 (token: `lakehouse`)
- **MinIO Console** → http://localhost:9001 (`minioadmin` / `minioadmin`)
- **Spark UI** → http://localhost:4040 (sau khi notebook chạy 1 cell)

Trong Jupyter, mở `notebooks/` rồi convert `.py` → notebook qua right-click hoặc:
```bash
jupytext --to notebook notebooks/*.py
```
(Jupytext đã pre-installed trong image.)

Generate sample data:
```bash
docker compose -f docker/docker-compose.yml exec spark python /workspace/scripts/generate_data.py
```

## Deliverable (nộp 4 notebook đã chạy + ảnh chụp)

Mapping 1-to-1 với slide deliverable (slide §0 / line 113):

1. **NB1** — Delta table tạo từ DataFrame, `_delta_log/00..0.json` xuất hiện trong MinIO.
2. **NB2** — Bảng so sánh query time TRƯỚC OPTIMIZE+ZORDER vs SAU. Mục tiêu ≥ 3× speedup.
3. **NB3** — Output `DESCRIBE HISTORY` show ≥ 5 versions; RESTORE chạy trong < 30 s; MERGE upsert 100K rows.
4. **NB4** — Bronze + Silver + Gold tables tồn tại trong MinIO; Gold table query ra metrics đúng.

## Rubric

Xem [`rubric.md`](rubric.md). Tổng điểm 100, weighted vào Track-2 Daily Lab (30%).

## Troubleshooting

- **`AnalysisException: Delta not found`** → image dùng `delta-spark==3.2.0` matched với Spark 3.5; nếu bạn override Spark version, update `requirements.txt`.
- **MinIO connection refused** → đợi 10 s sau `compose up`; check `docker compose logs minio`.
- **Out of memory** → giảm Spark driver memory trong `docker/spark.conf` (default 2 GB).

## License & Attribution
Phỏng theo Track 2 Day 18 slide. © VinUniversity AICB program.
