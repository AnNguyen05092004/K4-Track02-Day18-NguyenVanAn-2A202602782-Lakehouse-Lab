# ---
# jupyter:
#   jupytext:
#     formats: py:percent
# ---

# %% [markdown]
# # NB2 — Small-File Problem & OPTIMIZE + ZORDER
#
# **Mục tiêu:** prove the 3–10× speedup claim from slide §5.
# Maps to deliverable bullet 2.

# %%
import sys, time, random
sys.path.append("/workspace/scripts")
from spark_session import get_spark
from delta.tables import DeltaTable

spark = get_spark("nb2_optimize_zorder")
path = "s3a://lakehouse/events_smallfiles"

# %% [markdown]
# ## 1. Manufacture the small-file problem
#
# Append 200 tiny batches → 200 small files. Realistic streaming-ingestion shape.

# %%
spark.sql("DROP TABLE IF EXISTS events")  # local
import shutil
# clean S3 path manually if rerun (re-running just appends)
for batch in range(200):
    rows = [(i, random.choice(["click","view","scroll","purchase"]), random.randint(1, 10000))
            for i in range(batch*500, (batch+1)*500)]
    df = spark.createDataFrame(rows, ["event_id", "kind", "user_id"])
    df.write.format("delta").mode("append").save(path)

# %% [markdown]
# ## 2. Benchmark BEFORE optimize

# %%
def bench(label):
    t0 = time.time()
    n = (spark.read.format("delta").load(path)
            .where("user_id = 4242 AND kind = 'purchase'").count())
    dt = time.time() - t0
    print(f"{label:25s}  count={n}  time={dt:.2f}s")
    return dt

before = bench("BEFORE OPTIMIZE+ZORDER")

# %% [markdown]
# ## 3. OPTIMIZE + ZORDER

# %%
dt_table = DeltaTable.forPath(spark, path)
spark.sql(f"OPTIMIZE delta.`{path}` ZORDER BY (user_id)")

# %% [markdown]
# ## 4. Benchmark AFTER

# %%
after = bench("AFTER OPTIMIZE+ZORDER")
print(f"\nSpeedup: {before/after:.1f}×  (target ≥ 3×)")

# %% [markdown]
# ## 5. Inspect file count change

# %%
spark.sql(f"DESCRIBE DETAIL delta.`{path}`").select(
    "numFiles", "sizeInBytes"
).show()

# %% [markdown]
# ## ✅ Deliverable check
# - [ ] Speedup ≥ 3×
# - [ ] `numFiles` dropped substantially after OPTIMIZE
# - [ ] Screenshot the printed comparison

# %%
spark.stop()
