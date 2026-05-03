"""Generate synthetic LLM-observability records into Bronze (lightweight path).

Default 200K rows — small enough that all 4 notebooks finish in under a minute
on a laptop. Override with `python generate_data_lite.py 1000000`.
"""
from __future__ import annotations

import json
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import polars as pl
from deltalake import write_deltalake

from lakehouse import path, reset


def main(n_rows: int = 200_000) -> None:
    start = datetime(2026, 4, 1, tzinfo=timezone.utc)
    models = ["claude-sonnet-4-6"] * 6 + ["claude-haiku-4-5"] * 3 + ["claude-opus-4-7"]
    statuses = ["ok"] * 95 + ["rate_limited"] * 3 + ["error"] * 2

    rows = []
    for i in range(n_rows):
        ts = start + timedelta(seconds=i // 10)
        m = random.choice(models)
        pt = random.randint(50, 4000)
        ct = random.randint(20, 2000)
        latency = int(ct * random.uniform(8, 25) + random.gauss(200, 50))
        rows.append(
            {
                "request_id": str(uuid.uuid4()),
                "ts": ts,
                "raw_json": json.dumps(
                    {
                        "model": m,
                        "user_id": f"u_{random.randint(1, 5000)}",
                        "usage": {"input": pt, "output": ct},
                        "latency_ms": latency,
                        "status": random.choice(statuses),
                    }
                ),
            }
        )

    df = pl.DataFrame(rows)
    out = path("bronze", "llm_calls_raw")
    reset(out)
    write_deltalake(out, df.to_arrow(), mode="overwrite")
    print(f"Wrote {n_rows:,} rows → {out}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    main(n)
