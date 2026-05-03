# ---
# jupyter:
#   jupytext:
#     formats: py:percent
# ---

# %% [markdown]
# # NB2 — Small-File Problem & OPTIMIZE + Z-order (lightweight)
#
# Maps to slide §5 + deliverable bullet 2.
#
# > Spark equivalent: `OPTIMIZE delta.\`path\` ZORDER BY (user_id)`
# > delta-rs:        `dt.optimize.compact()` + `dt.optimize.z_order(["user_id"])`

# %%
import sys, time, random, os
sys.path.insert(0, "/workspace/scripts" if os.path.exists("/workspace") else "../scripts")
import polars as pl
import duckdb
from deltalake import DeltaTable, write_deltalake
from lakehouse import path, reset

table_path = path("scratch", "events_smallfiles")
reset(table_path)  # idempotent

# %% [markdown]
# ## 1. Manufacture the small-file problem
#
# 200 tiny appends → 200 small files. Realistic streaming-ingestion shape.

# %%
random.seed(42)
for batch in range(200):
    rows = pl.DataFrame({
        "event_id":  list(range(batch * 500, (batch + 1) * 500)),
        "kind":      [random.choice(["click", "view", "scroll", "purchase"]) for _ in range(500)],
        "user_id":   [random.randint(1, 10000) for _ in range(500)],
    })
    mode = "overwrite" if batch == 0 else "append"
    write_deltalake(table_path, rows.to_arrow(), mode=mode)

dt = DeltaTable(table_path)
files_before = len(dt.files())
print(f"Files before OPTIMIZE: {files_before}")

# %% [markdown]
# ## 2. Benchmark BEFORE optimize (DuckDB point-query)

# %%
def bench(label):
    # Force fresh metadata read
    duckdb.sql(f"SELECT count(*) FROM delta_scan('{table_path}')").fetchone()
    t0 = time.time()
    n = duckdb.sql(
        f"SELECT count(*) FROM delta_scan('{table_path}') "
        f"WHERE user_id = 4242 AND kind = 'purchase'"
    ).fetchone()[0]
    dt_s = time.time() - t0
    print(f"{label:25s}  count={n}  time={dt_s*1000:.1f} ms")
    return dt_s

before = bench("BEFORE OPTIMIZE")

# %% [markdown]
# ## 3. OPTIMIZE (compact small files) + Z-ORDER (co-locate by user_id)

# %%
dt = DeltaTable(table_path)
dt.optimize.compact()
dt.optimize.z_order(["user_id"])

dt = DeltaTable(table_path)  # refresh
files_after = len(dt.files())
print(f"Files after OPTIMIZE+ZORDER: {files_after}  (was {files_before})")

# %% [markdown]
# ## 4. Benchmark AFTER

# %%
after = bench("AFTER OPTIMIZE+ZORDER")
print(f"\nSpeedup: {before/max(after, 1e-6):.1f}×  (target ≥ 3×)")
print(f"File reduction: {files_before} → {files_after}  ({files_before/files_after:.0f}× fewer)")

# %% [markdown]
# ## ✅ Deliverable check
# - [ ] Speedup ≥ 3× (Z-order skips most files via min/max stats)
# - [ ] File count dropped substantially after compact()
# - [ ] Screenshot the printed numbers
