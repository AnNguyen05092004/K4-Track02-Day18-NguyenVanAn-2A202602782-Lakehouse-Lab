# Day 18 — Lakehouse Lab (Track 2)

Lab cho **AICB-P2T2 · Ngày 18 · Data Lakehouse Architecture**.
Build Bronze → Silver → Gold pipeline với Delta Lake.

**Hai paths để chọn:**

| Path | Stack | Setup | RAM | Khi nào dùng |
|---|---|---|---|---|
| **Lightweight (default)** | `deltalake` + DuckDB + Polars | `make setup` (~10 s) | ~500 MB | Hầu hết học viên — laptop yếu, mạng chậm, muốn focus vào concept |
| **Spark (Docker)** | PySpark + delta-spark + MinIO | `make spark-up` (~3 min) | ~4 GB | Học viên muốn trải nghiệm Spark API y hệt production Databricks |

> Cả hai paths viết ra **cùng một Delta Lake on-disk format** — bạn có thể đổi
> giữa hai paths bất cứ lúc nào, các tables vẫn đọc được.

---

## Quick Start — Lightweight (recommended)

```bash
git clone https://github.com/VinUni-AI20k/Day18-Track2-Lakehouse-Lab.git
cd Day18-Track2-Lakehouse-Lab
make setup    # ~10 s with pip, ~2 s with uv
make smoke    # ~5 s — verifies the stack works
make lab      # opens http://localhost:8888
```

Yêu cầu: **Python ≥ 3.10**. Không cần Docker, không cần Java, không cần MinIO.

Khi `make smoke` báo `All checks passed`, mở
**http://localhost:8888/lab/tree/01_delta_basics.ipynb** và bắt đầu.

Generate sample data cho NB4:
```bash
make data    # 200K rows → _lakehouse/bronze/llm_calls_raw/
```

### Tất cả lệnh `make`

```
make setup     Lightweight: tạo venv + install (80 MB)
make smoke     Lightweight: 5-second smoke test
make lab       Lightweight: open Jupyter Lab
make data      Lightweight: generate Bronze sample
make clean     Lightweight: wipe venv + _lakehouse/

make spark-up      Spark/Docker: start full stack
make spark-smoke   Spark/Docker: smoke test
make spark-data    Spark/Docker: generate 1M-row sample
make spark-down    Spark/Docker: stop (data persists)
make spark-clean   Spark/Docker: full reset
```

---

## Quick Start — Spark/Docker (optional)

```bash
make spark-up && make spark-smoke
```

Yêu cầu: Docker Desktop ≥ 4.x, RAM ≥ 8 GB free.
Endpoints + troubleshooting cho path này: xem [`notebooks-spark/README.md`](notebooks-spark/) (notebooks dùng PySpark API).

---

## Cấu trúc & tiến trình (cả hai paths)

| Notebook | Skill | Slide section |
|---|---|---|
| `01_delta_basics` | Write/read Delta, schema enforcement, transaction log | §2 Delta Lake |
| `02_optimize_zorder` | Small-file problem; OPTIMIZE + Z-order benchmark | §5 Storage Optimization |
| `03_time_travel` | versionAsOf, RESTORE, MERGE, history() | §3 Time Travel |
| `04_medallion` | LLM-observability Bronze→Silver→Gold pipeline | §6 Lakehouse cho AI/ML |

**Source format:** Notebooks live as Jupytext `.py` files (small, easy to review).
`make setup` and `make lab` auto-convert to `.ipynb`. Edit `.ipynb` in Jupyter
and Jupytext keeps both in sync.

**Spark API equivalent:** Each lightweight notebook has a comment showing the
PySpark equivalent at the top, so you can mentally map between the two paths.

---

## Deliverable (4 notebook đã chạy + ảnh chụp)

Mapping 1-to-1 với slide deliverable:

1. **NB1** — Delta table tạo, `_delta_log/00..0.json` xuất hiện trên disk.
2. **NB2** — Speedup ≥ 3× sau OPTIMIZE+Z-ORDER (in ra trong notebook).
3. **NB3** — `history()` show ≥ 5 versions; RESTORE < 30 s; MERGE 100K rows.
4. **NB4** — Bronze + Silver + Gold tables tồn tại; Gold metrics đúng.

Chấm điểm: xem [`rubric.md`](rubric.md). Tổng 100 pts → Track-2 Daily Lab (30%).

---

## Cấu trúc repo

```
.
├── Makefile              # both paths
├── README.md             # bạn đang đọc
├── requirements.txt      # lightweight (deltalake + duckdb + polars)
├── requirements-spark.txt# Spark path
├── rubric.md             # grading
├── notebooks/            # ← lightweight path (default)
│   ├── 01_delta_basics.py
│   ├── 02_optimize_zorder.py
│   ├── 03_time_travel.py
│   └── 04_medallion.py
├── notebooks-spark/      # Spark/Docker path (same lessons, PySpark API)
├── scripts/
│   ├── lakehouse.py            # path helper (lightweight)
│   ├── generate_data_lite.py   # lightweight Bronze generator
│   ├── verify_lite.py          # lightweight smoke test
│   ├── spark_session.py        # Spark factory
│   ├── generate_data.py        # Spark Bronze generator
│   └── verify.py               # Spark smoke test
└── docker/
    └── docker-compose.yml      # Spark/MinIO/Jupyter stack
```

---

## Troubleshooting (lightweight)

| Triệu chứng | Fix |
|---|---|
| `make setup` báo `python3: command not found` | Install Python 3.10+ (https://www.python.org/downloads/) |
| `make lab` báo "port 8888 in use" | Đổi: `$(JUPYTER) lab --port 8889` trong Makefile |
| NB2 speedup < 3× | Bình thường nếu RAM < 4 GB — DuckDB cache làm before/after gần nhau. Reset bằng `make clean && make setup`. |
| NB4 lỗi "Path does not exist" | Quên `make data` |

---

## Submission

Fork repo → push 4 notebook đã chạy + `submission/REFLECTION.md` (≤ 200 words: anti-pattern nào trong slide §5 team bạn dễ vướng nhất, vì sao?). PR back vào upstream với title `[NXX] Lab18 — <Họ Tên>`.

---

© VinUniversity AICB program. Phỏng theo Track 2 Day 18 slide.
