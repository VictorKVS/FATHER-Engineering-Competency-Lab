from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

import psycopg

N = 10_000
DIM = 384
TOP_K = 10
QUERY_COUNT = 30
REPETITIONS = 3
SEED = 20261114
EF_VALUES = [100, 150, 200, 300, 400]
RECALL_THRESHOLD = 0.95


def percentile(values: list[float], p: float) -> float:
    xs = sorted(values)
    if not xs:
        return 0.0
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def latency_summary(values: list[float]) -> dict[str, float]:
    return {
        "mean_ms": round(statistics.fmean(values), 4),
        "p50_ms": round(percentile(values, 0.50), 4),
        "p95_ms": round(percentile(values, 0.95), 4),
        "p99_ms": round(percentile(values, 0.99), 4),
        "max_ms": round(max(values), 4),
    }


def vector_for(i: int) -> list[float]:
    theta = (2.0 * math.pi * ((i * 7919 + 104729) % N)) / N
    return [math.cos(theta), math.sin(theta)] + [0.0] * (DIM - 2)


def vector_text(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.9f}" for x in v) + "]"


def query_ids() -> list[int]:
    return [((i * 313) + 17) % N + 1 for i in range(QUERY_COUNT)]


def exact_topk(query_id: int) -> list[int]:
    qx, qy = vector_for(query_id)[:2]
    scored: list[tuple[float, int]] = []
    for i in range(1, N + 1):
        vx, vy = vector_for(i)[:2]
        scored.append((qx * vx + qy * vy, i))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [i for _, i in scored[:TOP_K]]


def recall_at_k(expected: list[int], actual: list[int]) -> float:
    return len(set(expected) & set(actual[:TOP_K])) / TOP_K


def sha256_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def image_digest() -> str | None:
    p = subprocess.run(
        ["docker", "inspect", "-f", "{{.Image}}", "father-bench-pgvector"],
        capture_output=True,
        text=True,
        check=False,
    )
    return p.stdout.strip() if p.returncode == 0 else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    started = time.time()
    expected = {qid: exact_topk(qid) for qid in query_ids()}

    with psycopg.connect(
        host="127.0.0.1",
        port=55433,
        dbname="father_bench",
        user="father",
        password="father_bench",
        autocommit=True,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("DROP TABLE IF EXISTS bench_vec_tuning")
            cur.execute(
                "CREATE TABLE bench_vec_tuning("
                "id integer PRIMARY KEY, v vector(384) NOT NULL)"
            )

        with conn.cursor() as cur:
            with cur.copy("COPY bench_vec_tuning (id, v) FROM STDIN") as copy:
                for i in range(1, N + 1):
                    copy.write_row((i, vector_text(vector_for(i))))

        with conn.cursor() as cur:
            cur.execute(
                "CREATE INDEX bench_vec_tuning_hnsw "
                "ON bench_vec_tuning USING hnsw (v vector_cosine_ops)"
            )
            cur.execute("ANALYZE bench_vec_tuning")

        results = []
        selected = None
        qids = query_ids()

        for ef in EF_VALUES:
            with conn.cursor() as cur:
                cur.execute("SET hnsw.ef_search = %s", (ef,))

                # warm-up
                for qid in qids:
                    cur.execute(
                        "SELECT id FROM bench_vec_tuning "
                        "ORDER BY v <=> %s::vector LIMIT %s",
                        (vector_text(vector_for(qid)), TOP_K),
                    )
                    cur.fetchall()

                latencies = []
                recalls = []
                for _ in range(REPETITIONS):
                    for qid in qids:
                        t0 = time.perf_counter_ns()
                        cur.execute(
                            "SELECT id FROM bench_vec_tuning "
                            "ORDER BY v <=> %s::vector LIMIT %s",
                            (vector_text(vector_for(qid)), TOP_K),
                        )
                        actual = [row[0] for row in cur.fetchall()]
                        latencies.append((time.perf_counter_ns() - t0) / 1_000_000)
                        recalls.append(recall_at_k(expected[qid], actual))

            mean_recall = statistics.fmean(recalls)
            item = {
                "ef_search": ef,
                "recall_at_k_mean": round(mean_recall, 6),
                "recall_at_k_min": round(min(recalls), 6),
                "latency": latency_summary(latencies),
                "passes_recall_threshold": mean_recall >= RECALL_THRESHOLD,
            }
            results.append(item)

            if selected is None and item["passes_recall_threshold"]:
                selected = item

    envelope = {
        "qualification": "BRAIN_STORAGE_BENCH_P1_VEC_PGVECTOR_TUNING",
        "contract_version": "1.0",
        "seed": SEED,
        "records": N,
        "dimensions": DIM,
        "top_k": TOP_K,
        "recall_threshold": RECALL_THRESHOLD,
        "tested_ef_search": EF_VALUES,
        "results": results,
        "selected_minimum_passing_configuration": selected,
        "image_digest": image_digest(),
        "started_epoch": started,
        "completed_epoch": time.time(),
        "passed": selected is not None,
    }
    envelope["evidence_hash"] = sha256_json(envelope)
    Path(args.out).write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    print(json.dumps(envelope, indent=2))
    return 0 if envelope["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
