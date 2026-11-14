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

N = 100_000
DIM = 384
TOP_K = 10
QUERY_COUNT = 30
REPETITIONS = 3
SEED = 20261114
RECALL_THRESHOLD = 0.95
EF_SEARCH = 1000
A = 7919
B = 104729

BUILD_MATRIX = [
    {"m": 16, "ef_construction": 64},
    {"m": 16, "ef_construction": 128},
    {"m": 16, "ef_construction": 256},
    {"m": 32, "ef_construction": 128},
    {"m": 32, "ef_construction": 256},
    {"m": 32, "ef_construction": 512},
    {"m": 48, "ef_construction": 256},
    {"m": 48, "ef_construction": 512},
    {"m": 64, "ef_construction": 512},
]


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
    theta = (2.0 * math.pi * ((i * A + B) % N)) / N
    return [math.cos(theta), math.sin(theta)] + [0.0] * (DIM - 2)


def vector_text(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.9f}" for x in v) + "]"


def query_ids() -> list[int]:
    return [((i * 313) + 17) % N + 1 for i in range(QUERY_COUNT)]


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


def docker_stats() -> dict[str, Any]:
    p = subprocess.run(
        ["docker", "stats", "father-bench-pgvector", "--no-stream", "--format", "{{json .}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0 or not p.stdout.strip():
        return {"error": p.stderr.strip()}
    try:
        return json.loads(p.stdout.strip())
    except json.JSONDecodeError:
        return {"raw": p.stdout.strip()}


def evaluate(cur, expected: dict[int, list[int]]) -> dict[str, Any]:
    latencies: list[float] = []
    recalls: list[float] = []
    ids = query_ids()

    for qid in ids:
        cur.execute(
            "SELECT id FROM bench_vec_m_build "
            "ORDER BY v <=> %s::vector LIMIT %s",
            (vector_text(vector_for(qid)), TOP_K),
        )
        cur.fetchall()

    for _ in range(REPETITIONS):
        for qid in ids:
            t0 = time.perf_counter_ns()
            cur.execute(
                "SELECT id FROM bench_vec_m_build "
                "ORDER BY v <=> %s::vector LIMIT %s",
                (vector_text(vector_for(qid)), TOP_K),
            )
            actual = [row[0] for row in cur.fetchall()]
            latencies.append((time.perf_counter_ns() - t0) / 1_000_000)
            recalls.append(recall_at_k(expected[qid], actual))

    mean_recall = statistics.fmean(recalls)
    return {
        "recall_at_k_mean": round(mean_recall, 6),
        "recall_at_k_min": round(min(recalls), 6),
        "latency": latency_summary(latencies),
        "passes_recall_threshold": mean_recall >= RECALL_THRESHOLD,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    started = time.time()
    try:
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
                cur.execute("DROP TABLE IF EXISTS bench_vec_m_build")
                cur.execute(
                    "CREATE TABLE bench_vec_m_build("
                    "id integer PRIMARY KEY, v vector(384) NOT NULL)"
                )

            ingest_started = time.perf_counter()
            with conn.cursor() as cur:
                with cur.copy("COPY bench_vec_m_build (id, v) FROM STDIN") as copy:
                    for i in range(1, N + 1):
                        copy.write_row((i, vector_text(vector_for(i))))
            ingest_seconds = time.perf_counter() - ingest_started

            # Exact persisted ground truth before any ANN index exists.
            exact_expected: dict[int, list[int]] = {}
            exact_latencies: list[float] = []
            with conn.cursor() as cur:
                for qid in query_ids():
                    t0 = time.perf_counter_ns()
                    cur.execute(
                        "SELECT id FROM bench_vec_m_build "
                        "ORDER BY v <=> %s::vector LIMIT %s",
                        (vector_text(vector_for(qid)), TOP_K),
                    )
                    exact_expected[qid] = [row[0] for row in cur.fetchall()]
                    exact_latencies.append(
                        (time.perf_counter_ns() - t0) / 1_000_000
                    )

            results = []
            selected = None

            for config in BUILD_MATRIX:
                m = config["m"]
                efc = config["ef_construction"]

                with conn.cursor() as cur:
                    cur.execute("DROP INDEX IF EXISTS bench_vec_m_build_hnsw")
                    build_started = time.perf_counter()
                    cur.execute(
                        "CREATE INDEX bench_vec_m_build_hnsw "
                        "ON bench_vec_m_build USING hnsw (v vector_cosine_ops) "
                        f"WITH (m = {m}, ef_construction = {efc})"
                    )
                    build_seconds = time.perf_counter() - build_started
                    cur.execute("ANALYZE bench_vec_m_build")
                    cur.execute(
                        "SELECT set_config('hnsw.ef_search', %s, false)",
                        (str(EF_SEARCH),),
                    )

                    measured = evaluate(cur, exact_expected)

                item = {
                    "m": m,
                    "ef_construction": efc,
                    "ef_search": EF_SEARCH,
                    "index_build_seconds": round(build_seconds, 4),
                    **measured,
                    "resource_snapshot": docker_stats(),
                }
                results.append(item)

                if selected is None and item["passes_recall_threshold"]:
                    selected = item

        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_M_PGVECTOR_BUILD_TUNING",
            "contract_version": "1.0",
            "seed": SEED,
            "records": N,
            "dimensions": DIM,
            "top_k": TOP_K,
            "recall_threshold": RECALL_THRESHOLD,
            "ground_truth": {
                "method": "exact search over persisted pgvector values before ANN index",
                "exact_latency": latency_summary(exact_latencies),
            },
            "ingest_seconds": round(ingest_seconds, 4),
            "ef_search": EF_SEARCH,
            "build_matrix": BUILD_MATRIX,
            "results": results,
            "selected_first_passing_configuration": selected,
            "image_digest": image_digest(),
            "started_epoch": started,
            "completed_epoch": time.time(),
            "passed": selected is not None,
        }
    except Exception as exc:
        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_M_PGVECTOR_BUILD_TUNING",
            "contract_version": "1.0",
            "seed": SEED,
            "records": N,
            "status": "FAIL",
            "reason": repr(exc),
            "started_epoch": started,
            "completed_epoch": time.time(),
            "passed": False,
        }

    envelope["evidence_hash"] = sha256_json(envelope)
    Path(args.out).write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    print(json.dumps(envelope, indent=2))
    return 0 if envelope.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
