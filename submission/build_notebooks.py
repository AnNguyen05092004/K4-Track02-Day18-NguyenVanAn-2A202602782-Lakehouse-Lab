"""Build the 8 executed submission notebooks -> submission/notebooks/*.ipynb

Vai trò file: dựng bản NỘP của 8 notebook từ nguồn gốc `notebooks/*.py` (không sửa nguồn).
  1. Đọc từng notebook jupytext `.py` của đề bài.
  2. Chèn thêm (a) cell bằng chứng CHỈ ĐỌC (in nội dung _delta_log, kiểm tra chất lượng Gold...)
     và (b) cell Markdown giải thích số liệu — rubric chấm "con số + cách đọc con số".
     Không cell nào bỏ assert hay hạ ngưỡng của đề.
  3. Thực thi thật bằng kernel Jupyter (nbclient), lưu output vào .ipynb.

Chạy từ gốc repo:   .venv/bin/python submission/build_notebooks.py [01 02 ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

import jupytext
import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"
OUT = ROOT / "submission" / "notebooks"


def md(src: str):
    c = new_markdown_cell(src.strip("\n"))
    c.metadata["injected"] = True
    return c


def code(src: str):
    c = new_code_cell(src.strip("\n"))
    c.metadata["injected"] = True
    return c


# INSERTS[prefix] = [(anchor_substring_in_ORIGINAL_cell, [cells inserted right after it]), ...]
INSERTS: dict[str, list] = {}

# ═══════════════════════════════════════════════════════════════════════════
# NB1
# ═══════════════════════════════════════════════════════════════════════════
INSERTS["01"] = [
    ('print("\\nHistory:")', [
        code('''
# [Bằng chứng - chỉ đọc] Thư mục bảng + nội dung commit đầu tiên của _delta_log
import json, os
log_dir = os.path.join(table_path, "_delta_log")
print("Các file trong bảng:")
for root, _, files in os.walk(table_path):
    for f in sorted(files):
        print("  ", os.path.relpath(os.path.join(root, f), table_path))

print("\\n=== _delta_log/00000000000000000000.json (mỗi dòng là 1 action) ===")
with open(os.path.join(log_dir, "00000000000000000000.json")) as fh:
    for line in fh:
        action = json.loads(line)
        kind = next(iter(action))
        body = action[kind]
        if kind == "metaData":
            fields = json.loads(body["schemaString"])["fields"]
            body = {"id": body["id"], "schema": [(f["name"], f["type"]) for f in fields]}
        print(f"\\n[{kind}]")
        print(json.dumps(body, indent=2)[:700])
'''),
        md('''
### 📝 Giải thích — tạo bảng và `_delta_log/`
- Một lần `write_deltalake` thành công = **một commit** = một file JSON đánh số (`00000000000000000000.json`). Bảng Delta *chính là* chuỗi các action trong log này, không phải thư mục Parquet.
- Commit đầu có 4 loại action: `commitInfo` (ai/làm gì: `WRITE`), `protocol` (phiên bản đọc/ghi), `metaData` (schema `id, name, age, city` — thứ mà schema enforcement dùng để so sánh) và `add` (khai báo file Parquet thuộc bảng, kèm size và thống kê min/max).
- File Parquet nằm cạnh log nhưng **không có action `add` thì không thuộc bảng** — ý này sẽ dùng lại ở NB6 (orphan files).
'''),
    ]),
    ('BLOCKED by schema enforcement', [
        code('''
# [Bằng chứng - chỉ đọc] Lỗi đầy đủ + chứng minh lần ghi bị chặn KHÔNG để lại dấu vết
import os
try:
    write_deltalake(table_path, bad.to_arrow(), mode="append")
    print("!!! UNEXPECTED: ghi sai kiểu thành công")
except Exception as e:
    print("BỊ CHẶN. Loại lỗi:", type(e).__name__)
    print("Nội dung lỗi:", str(e)[:400])

log_dir = os.path.join(table_path, "_delta_log")
n_commits = len([f for f in os.listdir(log_dir) if f.endswith(".json")])
n_rows = DeltaTable(table_path).to_pyarrow_table().num_rows
print(f"\\nSố commit JSON sau lần ghi lỗi: {n_commits}  (vẫn chỉ có commit tạo bảng)")
print(f"Số dòng trong bảng           : {n_rows}  (vẫn là 3)")
assert n_commits == 1 and n_rows == 3, "lần ghi lỗi đã để lại dấu vết"
'''),
        md('''
### 📝 Giải thích — schema enforcement
- Ghi `age = "thirty"` vào cột `age` kiểu `Int64` bị chặn với `Cast error: Cannot cast string 'thirty' to value of Int64 type`.
- **Bằng chứng thật nằm ở cell trên, không phải dòng `[PASS]` cuối notebook** (cờ đó là hardcode): sau lần ghi lỗi, `_delta_log/` vẫn chỉ có 1 commit và bảng vẫn 3 dòng → giao dịch hỏng bị từ chối nguyên khối, không để lại file hay commit dở.
- Với Parquet thuần, file sai kiểu vẫn ghi được và chỉ vỡ khi truy vấn sau đó; Delta chặn ngay lúc ghi.
'''),
    ]),
    ('new.to_arrow(), mode="append", schema_mode="merge")', [
        code('''
# [Bằng chứng - chỉ đọc] Commit thứ 2 đã đổi schema như thế nào
import json, os
log_dir = os.path.join(table_path, "_delta_log")
print("Các file JSON trong _delta_log:", sorted(f for f in os.listdir(log_dir) if f.endswith(".json")))
with open(os.path.join(log_dir, "00000000000000000001.json")) as fh:
    for line in fh:
        action = json.loads(line)
        kind = next(iter(action))
        if kind == "metaData":
            fields = json.loads(action["metaData"]["schemaString"])["fields"]
            print("Schema trong commit 1:", [(f["name"], f["type"]) for f in fields])
        else:
            print("action:", kind)
print("\\nHistory:")
for h in DeltaTable(table_path).history():
    print(f"  v{h['version']}  {h['operation']}")
'''),
        md('''
### 📝 Giải thích — schema evolution (opt-in)
- Có **2 commit** (`...000.json` tạo bảng, `...001.json` append kèm cột `tier`). Lần ghi lỗi không sinh commit nào.
- Cột `tier` chỉ xuất hiện vì ta **nói rõ** `schema_mode="merge"`; không có tham số này, ghi dữ liệu có cột lạ sẽ bị từ chối như trường hợp enforcement.
- Commit 1 chứa `metaData` mới có thêm `tier`. 3 dòng cũ **không bị viết lại**; đọc lên thì `tier = null`. Vì vậy truy vấn DuckDB ở mục 5 cho đúng **2 nhóm**: `premium` (1 dòng) và `NULL` (3 dòng).
'''),
    ]),
    ('NB1 complete', [
        md('''
### ✅ Tổng kết NB1
| Tiêu chí | Bằng chứng ở trên |
|---|---|
| Delta table + JSON commit trong `_delta_log/` | danh sách file + nội dung `00000000000000000000.json` |
| Schema enforcement chặn `age=str` | lỗi `Cast error...`, 1 commit & 3 dòng không đổi |
| `schema_mode="merge"` thêm `tier` | schema commit 1 + DuckDB trả 2 nhóm tier |
'''),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════════
# NB2
# ═══════════════════════════════════════════════════════════════════════════
INSERTS["02"] = [
    ('print(f"Files before OPTIMIZE: {files_before}")', [
        code('''
# [Bằng chứng - chỉ đọc] Trước OPTIMIZE: mỗi file nhỏ cỡ nào, min/max user_id của nó ra sao?
import pyarrow as pa
_rows = pa.table(DeltaTable(table_path).get_add_actions(flatten=True)).to_pylist()
_sizes = [r["size_bytes"] for r in _rows]
files_could_hold_before = sum(1 for r in _rows if r["min.user_id"] <= TARGET_USER <= r["max.user_id"])
print(f"Số file: {len(_rows)}   kích thước mỗi file: {min(_sizes)/1024:.0f}–{max(_sizes)/1024:.0f} KB")
print("Khoảng user_id của 3 file đầu:", [(r["min.user_id"], r["max.user_id"]) for r in _rows[:3]])
print(f"File 'có thể chứa' user_id={TARGET_USER}: {files_could_hold_before}/{len(_rows)}")
'''),
        md('''
### 📝 Giải thích — small-file problem
- 200 lần `append` → **200 file Parquet** (≥ 100 như yêu cầu) và 200 commit. Mỗi file chỉ ~64 KB (xem cell bằng chứng ở trên).
- Mỗi file chứa 5.000 `user_id` ngẫu nhiên trong 1…100.000, nên min/max của mọi file đều xấp xỉ **[~1, ~100.000]**: các khoảng chồng lấn gần như hoàn toàn. Vì thế với `user_id = 4242`, engine không thể loại file nào dựa vào thống kê — cell trên cho thấy gần như **tất cả** file đều "có thể chứa" user này và phải được mở.
'''),
    ]),
    ('File reduction: {files_before}', [
        md('''
### 📝 Giải thích — OPTIMIZE + Z-ORDER và tốc độ
- `compact` gộp file nhỏ; `z_order(["user_id"])` viết lại dữ liệu **sắp xếp theo `user_id`**, mỗi file giữ một dải hẹp. Số file giảm từ **200 xuống 55** (xem output; `target_size=256 KB` được cố ý giữ nhỏ để vẫn còn nhiều file cho Z-order bỏ qua — nếu gộp thành 1 file thì không còn gì để pruning).
- **Speedup** ở trên là thời gian đồng hồ (median của 3 lần chạy) nên **dao động theo máy, cache và tải CPU**; không dùng nó làm bằng chứng duy nhất. Tiêu chí cho phép dùng pruning thay thế, và pruning là con số xác định (xem bên dưới).
'''),
    ]),
    ('Z-order deliverable metrics', [
        md('''
### 📝 Giải thích — files-pruned ratio và dải min/max
- Sau Z-order, dải `user_id` của các file **nối đuôi nhau, gần như không chồng lấn** (ví dụ `[1, 1851]`, `[1851, 3696]`, `[3696, 5534]`…). Mỗi file chỉ rộng ~1.850 giá trị thay vì ~100.000 như trước.
- Với `user_id = 4242` chỉ **1 file** (`[3696, 5534]`, dòng có `← contains target`) có thể chứa; **54/55 file bị bỏ qua** → **files-pruned ratio = 55 / 1 = 55×** (≥ 10×, đạt tiêu chí độc lập với đồng hồ).
- Cơ chế: Delta ghi min/max từng cột vào log; engine so sánh predicate với khoảng này và không mở file nằm ngoài khoảng. Z-order là thao tác làm cho các khoảng đó **hẹp và rời nhau**, nên thống kê trở nên có ích.
'''),
    ]),
    ('NB2 complete', [
        md('''
### ✅ Tổng kết NB2
| Tiêu chí | Kết quả |
|---|---|
| ≥ 100 file trước OPTIMIZE | 200 file |
| `numFiles` giảm rõ rệt | 200 → 55 |
| Speedup ≥ 3× **hoặc** pruning ≥ 10× | pruning 55× (speedup xem output, dao động theo máy) |
'''),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════════
# NB3
# ═══════════════════════════════════════════════════════════════════════════
INSERTS["03"] = [
    ('Total versions: {len(final_history)}', [
        md('''
### 📝 Giải thích — MERGE, time travel và RESTORE
- **MERGE 100K dòng (v2):** `operationMetrics` của v2 cho thấy `num_source_rows = 100000`, trong đó **50.000 dòng cập nhật** (customer_id 50000–99999 đã có từ v0) và **50.000 dòng chèn mới** (100000–149999) → bảng có 150.000 dòng. Đây là upsert nguyên tử trong **một** commit.
- **Time travel:** `DeltaTable(path, version=0)` đọc lại đúng 100.000 dòng ban đầu; `version=1` có schema có thêm cột `tier`. Mỗi version đọc được vì log giữ nguyên các commit cũ.
- **Dữ liệu xấu (v3):** append 50 dòng `score = -1`, `status = null` cho `customer_id 0–49` (trùng khoá với dòng đã có — `append` không dedup như MERGE).
- **RESTORE về v2 (v4):** `RESTORE` **không xoá lịch sử**; nó ghi một commit mới (v4) có trạng thái bằng v2. Kết quả: số dòng `score < 0` = **0**, và `history()` có **5 version** (v0 WRITE, v1 WRITE, v2 MERGE, v3 WRITE, v4 RESTORE) — đạt yêu cầu ≥ 5 và có cả dòng RESTORE.
- Ý nghĩa vận hành: sai dữ liệu được sửa bằng một thao tác kiểm toán được, không phải khôi phục từ backup.
'''),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════════
# NB4
# ═══════════════════════════════════════════════════════════════════════════
INSERTS["04"] = [
    ('assert n_dates >= 7', [
        code('''
# [Bằng chứng - chỉ đọc] 3 bảng trên storage + kiểm tra chất lượng Gold mà notebook gốc chưa assert
from lakehouse import ROOT

for name, p in [("Bronze", BRONZE), ("Silver", SILVER), ("Gold", GOLD)]:
    t = DeltaTable(p)
    rel = Path(p).relative_to(ROOT.parent)
    print(f"{name:7} {str(rel):42} delta v{t.version()}  rows={t.to_pyarrow_table().num_rows:>8,}  parquet files={len(t.file_uris())}")

print("\\nSilver partition theo date:", sorted(x.name for x in Path(SILVER).iterdir() if x.is_dir() and not x.name.startswith("_")))
print("DuckDB session TimeZone  :", con.sql("SELECT current_setting('TimeZone')").fetchone()[0])

quality = {
    "Silver < Bronze (dedup)":        silver_n < bronze_n,
    "Gold = n_dates x 3 model":        gold_df.height == n_dates * 3 and n_models == 3,
    "p50 <= p95 ở mọi dòng":           bool((gold_df["p50_latency_ms"] <= gold_df["p95_latency_ms"]).all()),
    "cost_usd > 0 ở mọi dòng":         bool((gold_df["cost_usd"] > 0).all()),
    "error_rate trong [0, 1]":         bool(gold_df["error_rate"].is_between(0, 1).all()),
}
print()
for k, v in quality.items():
    print(f"  [{'PASS' if v else 'FAIL'}] {k}")
assert all(quality.values()), "chất lượng Gold không đạt"
'''),
        md('''
### 📝 Giải thích — Bronze → Silver → Gold
- **Bronze (thô):** 200.000 dòng, mỗi dòng là chuỗi JSON nguyên bản + `request_id` + `ts`; generator cố ý chèn ~5% `request_id` trùng (retry).
- **Silver (sạch):** parse JSON thành cột có kiểu, bỏ dòng JSON hỏng và **dedup theo `request_id`** (`ROW_NUMBER() ... rn = 1`) → **190.052 dòng** (< 200.000; mất 9.948 dòng trùng). Silver được partition theo `date`.
- **Gold (tổng hợp):** mỗi dòng là một cặp (ngày, model) với p50/p95 latency (`QUANTILE_CONT`), tổng token, `error_rate` và `cost_usd` tính từ **bảng giá minh hoạ** của lab (không phải giá thật). Cell kiểm tra ở trên xác nhận: p50 ≤ p95, cost > 0, error_rate ∈ [0,1] ở mọi dòng — những điều notebook gốc chưa assert.
- **Vì sao Gold có 8 ngày chứ không phải 7?** Dữ liệu trải 7 ngày **UTC**, nhưng `CAST(ts AS DATE)` trong DuckDB chuyển `TIMESTAMPTZ` sang ngày theo **múi giờ của phiên** (máy này là `Asia/Ho_Chi_Minh`, UTC+7 — in ở cell trên). Ranh giới ngày lệch 7 giờ nên ngày đầu và ngày cuối là ngày *một phần*, tổng thành 8 ngày × 3 model = 24 dòng. Trên máy múi giờ UTC sẽ ra 7 ngày. Cả hai đều thoả "≥ 7 ngày × 3 model"; điều này cũng là lời nhắc: nên chuẩn hoá về UTC khi tính ngày trong pipeline.
'''),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════════
# NB5
# ═══════════════════════════════════════════════════════════════════════════
INSERTS["05"] = [
    ('NB5 complete', [
        md('''
### 📝 Giải thích — Iceberg và catalog
- **Tạo bảng qua catalog:** `cat.create_table("lake.llm_events", schema=...)` — ta không chọn đường dẫn; catalog (SQLite ở đây) sở hữu layout và con trỏ tới `metadata.json` hiện tại. Spec phân vùng là `day(ts)` (`ts_day`).
- **Hidden-partition pruning = 10×:** 10 file (mỗi ngày 1 file) → lọc một ngày trên **`ts`** (không phải `ts_day`) chỉ cần đọc **1 file** (`plan_files()`), 500 dòng. Iceberg lưu *transform* `day(ts)` trong metadata và tự suy ra partition từ cột thật. Người dùng kiểu Hive quên `WHERE dt=...` sẽ đọc **cả 10 file**; ở 512 MB/file và 10.000 truy vấn/ngày, lấy $5/TB, mỗi predicate bị quên tốn ~$220/ngày (phép tính minh hoạ trong notebook).
- **Cây metadata 3 tầng:** `metadata.json` → manifest list (10, mỗi snapshot một) → manifest (10) → data file (10). Ở quy mô lab, metadata còn **lớn hơn dữ liệu** (xem tỉ lệ phần trăm ở output, hàng trăm %) vì mỗi file chỉ ~5 KB; ở 512 MB/file tỉ lệ này ≈ 0,1% — file nhỏ làm đau hai lần: nhiều file dữ liệu *và* nhiều metadata.
- **Field ID:** `latency_ms` → `latency_millis` vẫn là **`field_id = 4`**: đổi tên chỉ là thay nhãn trong metadata, **không viết lại file dữ liệu nào**. Thêm `tier` nhận ID mới (6); 5.000 dòng cũ đọc lên `tier = NULL`, không cần backfill.
- **Partition evolution:** thêm `model` vào spec; batch ngày 11 ghi theo spec mới. Các data file thuộc **2 spec_id (1 và 2)** cùng tồn tại (spec 0 là spec rỗng ban đầu, chưa có file nào) và bảng vẫn đọc đủ **5.500 dòng** — không cần rewrite bảng.
'''),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════════
# NB6
# ═══════════════════════════════════════════════════════════════════════════
INSERTS["06"] = [
    ('Clustering is what makes stats USEFUL', [
        md('''
### 📝 Giải thích — Job 1 (compaction) và Job 2 (clustering)
- **Job 1 – Compaction:** 200 file → **11 file (≈ 18× ít hơn, ≥ 10×)**; `filesAdded=11`, `filesRemoved=200`. Dung lượng dữ liệu *tăng tạm thời* (10,1 → 16,1 MB) vì compaction **ghi file mới trước**, file cũ chỉ bị tombstone chứ chưa bị xoá.
- **Job 2 – Clustering (đo bằng thống kê, không bằng đồng hồ):** trước Z-order, truy vấn `user_id = 12345` phải mở **11/11** file (min/max chồng lấn); sau Z-order chỉ **1/10** file → bỏ qua **90%** (≥ 50%).
'''),
    ]),
    ('AFTER vacuum', [
        md('''
### 📝 Giải thích — Job 3 (vacuum / expiry của Delta)
- `retention_hours=0` thu hồi **16,1 MB**. Dòng "`would reclaim 211 files (0 B)`" của dry-run chỉ liệt kê *tên* file tombstone (đường dẫn tương đối nên `du()` ra 0 B) — số liệu đáng tin là dòng `Reclaimed`.
- Đổi lại, **time travel về v0 không còn**. Chỉ dùng retention 0 với dữ liệu scratch của lab; production dùng ≥ 168 giờ (7 ngày) để không phá reader đang chạy.
'''),
    ]),
    ('The age guard is not optional', [
        md('''
### 📝 Giải thích — Job 4 (orphan files) và phát hiện quan trọng
- Ta tạo 3 file Parquet mồ côi (job "crash" trước khi commit, tuổi 30 ngày). Bảng vẫn báo 100.000 dòng — orphan **vô hình** với `history()` và dashboard nhưng vẫn tính tiền lưu trữ.
- **Phát hiện đo được #1:** `VACUUM` của `deltalake` dry-run vẫn chỉ liệt kê file *đã tombstone* (211), **không thấy 3 orphan** vì chúng chưa từng vào log. Phải tự làm phép hiệu tập hợp *(file trên đĩa) − (file log tham chiếu)* + age guard 24 giờ → `find_orphans` tìm đúng **3** file và xoá được; sau đó `find_orphans == []`.
- **Về con số "15 file trên đĩa vs 10 trong log (5 file không thấy)":** `count_files()` đếm mọi `*.parquet` kể cả **file checkpoint nằm trong `_delta_log/`** — delta-rs tự tạo checkpoint mỗi 100 commit (v99, v199). Vậy 5 = **3 orphan thật + 2 checkpoint tự động** (không phải rác); `find_orphans` đã loại `_delta_log` nên chỉ báo đúng 3.
- **Sửa đổi so với đề (có chủ đích, giữ nguyên tiêu chí):** `DeltaTable.file_uris()` trả đường dẫn đã mã hoá phần trăm (`VIN AI` → `VIN%20AI`). Bản gốc không `unquote` nên trên đường dẫn có dấu cách, **mọi file đang dùng đều trông như "không được tham chiếu"** và chỉ nhờ age guard 24 giờ mà không bị xoá nhầm — một lỗi tiềm ẩn nguy hiểm (file đang dùng cũ hơn 24 giờ sẽ bị xoá). Tôi thêm `unquote(...)` trong `find_orphans` (`notebooks/06_maintenance.py`); kết quả vẫn tìm đúng 3 orphan.
'''),
    ]),
    ('create_checkpoint()', [
        md('''
### 📝 Giải thích — Job 5 (checkpoint)
Log có hơn 200 file JSON; một reader "lạnh" phải replay tất cả để biết trạng thái hiện tại. Checkpoint (`*.checkpoint.parquet` + `_last_checkpoint`) gộp trạng thái thành **một** file Parquet, reader chỉ đọc checkpoint + vài JSON sau đó. Output xác nhận `_last_checkpoint present: True`. (delta-rs đã tự tạo checkpoint ở v99/v199; lệnh `create_checkpoint()` tạo thêm một cái ở version hiện tại.)
'''),
    ]),
    ('Reclaimed by chaining expiry', [
        md('''
### 📝 Giải thích — Iceberg: expiry không xoá file vật lý
- `expire_snapshots` giảm **20 → 3 snapshot** (đạt "còn 3 snapshot") nhưng số file `.avro` trên đĩa vẫn **40 → 40**, `metadata.json` tăng 21 → 22 (expiry ghi thêm một metadata mới) → **expiry chỉ làm file "không còn được tham chiếu", chưa xoá gì**.
- **Phát hiện đo được #2:** phải tự tìm manifest list `snap-*.avro` không còn snapshot nào trỏ tới: **17 file** (≈ 37 KB) → xoá → `.avro` còn **23** (3 manifest list + 20 manifest vẫn được snapshot hiện tại tham chiếu), dữ liệu vẫn đủ **2.000 dòng**.
- Đây là hành vi của **API PyIceberg ở phiên bản trong lab**, không phải kết luận cho mọi engine Iceberg (Spark/Java thường nối expiry với dọn file). Bài học: Job 3 và Job 4 là một **cặp**; chạy expiry mà không sweep là lý do "đã expire snapshot mà hoá đơn S3 không giảm".
'''),
    ]),
    ('NB6 complete', [
        md('''
### ✅ Tổng kết NB6
| Job | Kết quả đo |
|---|---|
| 1 Compaction | 200 → 11 file (≈ 18×) |
| 2 Clustering | 1/10 file phải mở → bỏ qua 90% |
| 3 Expiry | Delta vacuum thu hồi 16,1 MB; Iceberg 20 → 3 snapshot |
| 4 Orphans | 3 Delta orphan tìm & xoá; 17 manifest list Iceberg bị bỏ lại đã quét |
| 5 Checkpoint | `*.checkpoint.parquet` + `_last_checkpoint` |
'''),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════════
# NB7
# ═══════════════════════════════════════════════════════════════════════════
INSERTS["07"] = [
    ('NB7 complete', [
        md('''
### 📝 Giải thích — blob, vector và lifecycle bug
- **Blob inline vs pointer:** tổng byte lưu gần như bằng nhau (12,5 MB blob phải nằm đâu đó). Với truy vấn phân tích `SELECT topic, count(*)`, đọc footer Parquet cho thấy cả hai layout chỉ đọc **~1,2 KB**: *column pruning* bảo vệ phân tích nên lời khuyên "đừng để blob trong bảng" không đúng cho trường hợp này.
- **Random access amplification = 200×:** lấy **một** frame 64 KB (`doc_id=137`) từ bảng inline phải đọc cả **row group 12,5 MB** (200 dòng trong 1 row group) → khuếch đại 12,5 MB / 64 KB = **200×** (≥ 5×); với pointer chỉ là 1 `GET` đúng 64 KB. Đơn vị I/O của Parquet là *row group*, không phải dòng — đây là điều Lance tối ưu cho random read (nuôi GPU).
- **int8 quantization:** 2,6 MB → ~452 KB = **~5,8× nhỏ hơn** (≥ 3×; vượt mức 4× lý thuyết vì int8 nén tốt hơn float32 ngẫu nhiên). **recall@10 = 0,904** (≥ 0,80) và **topic fidelity = 1,000** (≥ 0,95): ~10% ID thay đổi nhưng đó là hoán đổi giữa các láng giềng gần tương đương, kết quả vẫn 100% đúng chủ đề → recall theo ID *đánh giá thấp* chất lượng cho RAG.
- **Semantic search là SQL:** `array_cosine_similarity` của DuckDB trả top-5 cùng chủ đề `storage`; kết hợp được với cột governance (`consent_train`, `license`) trong một truy vấn. (Delta không có kiểu vector cố định chiều nên cột đọc lên là `list<float>`; notebook ép về `FLOAT[256]` khi truy vấn.) Brute force chỉ phù hợp phân tích/offline, không phải đường phục vụ online ở triệu vector.
- **Lifecycle bug tái hiện được:** yêu cầu xoá `user_042` (8 doc) → bảng lakehouse còn **0 hit** nhưng index ngoài (bản sao đồng bộ) vẫn trả **8 hit** → vi phạm quyền xoá. Cách đúng: index đăng ký **Change Data Feed** — CDF phát đúng **8 sự kiện `delete`** — hoặc tốt nhất giữ vector ngay trong dòng để vòng đời do bảng đảm bảo.
'''),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════════
# NB8
# ═══════════════════════════════════════════════════════════════════════════
INSERTS["08"] = [
    ('NB8 complete', [
        md('''
### 📝 Giải thích — trajectory, MCP mô phỏng, provenance
- **Medallion cho trajectory:** Bronze 1.578 bước → Silver **partition theo `agent_version`** (`policy-v2`, `policy-v3`) → Gold có **2 dòng** (mỗi policy 150 trajectory; success_rate 0,76 vs 0,753). Partition theo version cho phép retrain/xoá dữ liệu của một policy mà không đụng policy kia.
- **Pin version:** run huấn luyện ghi `table_version = 0` và `n_steps_seen = 1578`. Sau đó dữ liệu mới đổ vào (v1, 1.978 bước) nhưng đọc lại `version=0` vẫn ra **1.578 bước** → khớp. *Giới hạn:* phép kiểm chỉ so **số dòng**, chưa so nội dung.
- **MCP (mô phỏng offline, không phải server thật):** 5 lượt `list_tables` chỉ tốn **1** lần đọc catalog (4 lượt dùng cache TTL); gọi `delete_rows` chưa xác nhận trả `resultType: input_required`, sau `confirmed=True` mới `ok` — *giới hạn:* cờ `confirmed` do bên gọi truyền nên **không phải ranh giới uỷ quyền**, và `delete_rows` là no-op; task `submit_scan` → poll `working, working, completed` (độ trễ được mô phỏng, không có job nền).
- **Provenance (bucket minh hoạ của lab):** phân loại 2.000 doc thành `licensed` 675, `public_domain` 333, `synthetic` 331, `scraped_optout_checked` 327 và **`UNCLASSIFIED` 334 (16,7%)**; cả 5 bucket thành partition. Bộ lọc training của lab loại `UNCLASSIFIED` → **1.666 / 2.000** dòng được dùng. `UNCLASSIFIED` là một *phát hiện kiểm toán*, không được lặng lẽ gán vào bucket mặc định. *Giới hạn:* `cc-by-4.0` được xếp vào `public_domain` dù là giấy phép yêu cầu ghi công, và `user-owned` + consent chưa chứng minh đã kiểm tra opt-out — không dùng mapping này để kết luận quyền sử dụng dữ liệu thật.
- **Xoá theo subject:** `user_007` có 8 dòng (1 synthetic, 1 licensed, 5 UNCLASSIFIED, 1 scraped_optout_checked) → sau `delete` còn **0** ở version hiện tại (v0 → v1). Nhưng **v0 vẫn chứa dữ liệu đã xoá** (time travel) và file vật lý chưa bị dọn → xoá thật cần VACUUM/retention (NB6) và xử lý cả bản sao, index, mô hình đã huấn luyện. Đây là bài kiểm tra phiên bản hiện tại, không phải kết luận pháp lý.
'''),
    ]),
]


def build(prefix: str) -> Path:
    src = next(NB_DIR.glob(f"{prefix}_*.py"))
    nb = jupytext.read(src)
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata.pop("jupytext", None)  # bỏ cấu hình ghép cặp .py: nếu giữ, Jupyter báo "Unable to read paired notebook"

    for anchor, cells in INSERTS.get(prefix, []):
        idx = next((i for i, c in enumerate(nb.cells)
                    if not c.metadata.get("injected") and anchor in c.source), None)
        if idx is None:
            raise SystemExit(f"[{src.name}] anchor not found: {anchor!r}")
        nb.cells[idx + 1:idx + 1] = cells

    client = NotebookClient(nb, timeout=900, kernel_name="python3",
                            resources={"metadata": {"path": str(NB_DIR)}})
    client.execute()

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / (src.stem + ".ipynb")
    nbformat.write(nb, out)
    return out


if __name__ == "__main__":
    wanted = sys.argv[1:] or [f"{i:02d}" for i in range(1, 9)]
    for p in wanted:
        print(f"building NB{p} ...", flush=True)
        print("  ->", build(p).relative_to(ROOT), flush=True)
