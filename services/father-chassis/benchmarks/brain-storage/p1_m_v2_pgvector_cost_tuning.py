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
ACTIVE_VECTOR_DIMS = 32
TOP_K = 10
QUERY_COUNT = 30
REPETITIONS = 3
SEED = 20261114
RECALL_THRESHOLD = 0.95
VECTOR_MODULUS = 2147483647
CORPUS_VERSION = "v2-deterministic-32d"

BUILD_MATRIX = [
    {"m": 16, "ef_construction": 64},
    {"m": 16, "ef_construction": 128},
    {"m": 16, "ef_construction": 256},
    {"m": 24, "ef_construction": 128},
    {"m": 24, "ef_construction": 256},
    {"m": 32, "ef_construction": 128},
    {"m": 32, "ef_construction": 256},
]
EF_SEARCH_VALUES = [64, 128, 256, 512, 1000]


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
    values: list[float] = []
    norm_sq = 0.0
    for d in range(ACTIVE_VECTOR_DIMS):
        mixed = (
            (i * (104729 + d * 15485863))
            + ((d + 1) * 32452843)
            + (i * i * (d + 3))
        ) % VECTOR_MODULUS
        value = (mixed / VECTOR_MODULUS) * 2.0 - 1.0
        values.append(value)
        norm_sq += value * value
    norm = math.sqrt(norm_sq) or 1.0
    active = [value / norm for value in values]
    return active + [0.0] * (DIM - ACTIVE_VECTOR_DIMS)


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
        capture_output=True, text=True, check=False,
    )
    return p.stdout.strip() if p.returncode == 0 else None


def evaluate(cur, expected: dict[int, list[int]]) -> dict[str, Any]:
    ids = query_ids()
    latencies: list[float] = []
    recalls: list[float] = []

    for qid in ids:
        cur.execute(
            "SELECT id FROM bench_vec_v2_tuning "
            "ORDER BY v <=> %s::vector LIMIT %s",
            (vector_text(vector_for(qid)), TOP_K),
        )
        cur.fetchall()

    for _ in range(REPETITIONS):
        for qid in ids:
            t0 = time.perf_counter_ns()
            cur.execute(
                "SELECT id FROM bench_vec_v2_tuning "
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
            host="127.0.0.1", port=55433, dbname="father_bench",
            user="father", password="father_bench", autocommit=True
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cur.execute("DROP TABLE IF EXISTS bench_vec_v2_tuning")
                cur.execute(
                    "CREATE TABLE bench_vec_v2_tuning("
                    "id integer PRIMARY KEY, v vector(384) NOT NULL)"
                )

            t0 = time.perf_counter()
            with conn.cursor() as cur:
                with cur.copy("COPY bench_vec_v2_tuning (id, v) FROM STDIN") as copy:
                    for i in range(1, N + 1):
                        copy.write_row((i, vector_text(vector_for(i))))
                        if i % 10_000 == 0 or i == N:
                            print(f"[ingest] {i}/{N}", flush=True)
            ingest_seconds = time.perf_counter() - t0

            exact_expected: dict[int, list[int]] = {}
            with conn.cursor() as cur:
                for qid in query_ids():
                    cur.execute(
                        "SELECT id FROM bench_vec_v2_tuning "
                        "ORDER BY v <=> %s::vector LIMIT %s",
                        (vector_text(vector_for(qid)), TOP_K),
                    )
                    exact_expected[qid] = [row[0] for row in cur.fetchall()]

            results = []
            selected = None

            for idx, config in enumerate(BUILD_MATRIX, start=1):
                m = config["m"]
                efc = config["ef_construction"]
                print(
                    f"[{idx}/{len(BUILD_MATRIX)}] build HNSW "
                    f"m={m} ef_construction={efc}",
                    flush=True,
                )
                with conn.cursor() as cur:
                    cur.execute("DROP INDEX IF EXISTS bench_vec_v2_tuning_hnsw")
                    t_build = time.perf_counter()
                    cur.execute(
                        "CREATE INDEX bench_vec_v2_tuning_hnsw "
                        "ON bench_vec_v2_tuning USING hnsw (v vector_cosine_ops) "
                        f"WITH (m = {m}, ef_construction = {efc})"
                    )
                    build_seconds = time.perf_counter() - t_build
                    cur.execute("ANALYZE bench_vec_v2_tuning")

                    search_results = []
                    first_passing_search = None
                    for ef_search in EF_SEARCH_VALUES:
                        cur.execute(
                            "SELECT set_config('hnsw.ef_search', %s, false)",
                            (str(ef_search),),
                        )
                        measured = evaluate(cur, exact_expected)
                        item = {
                            "ef_search": ef_search,
                            **measured,
                        }
                        search_results.append(item)
                        print(
                            f"  ef_search={ef_search} "
                            f"Recall={measured['recall_at_k_mean']} "
                            f"p95={measured['latency']['p95_ms']}ms "
                            f"PASS={measured['passes_recall_threshold']}",
                            flush=True,
                        )
                        if first_passing_search is None and measured["passes_recall_threshold"]:
                            first_passing_search = item
                            break

                build_result = {
                    "m": m,
                    "ef_construction": efc,
                    "index_build_seconds": round(build_seconds, 4),
                    "search_results": search_results,
                    "first_passing_search": first_passing_search,
                    "passes": first_passing_search is not None,
                }
                results.append(build_result)

                if first_passing_search is not None:
                    selected = {
                        "m": m,
                        "ef_construction": efc,
                        "index_build_seconds": round(build_seconds, 4),
                        **first_passing_search,
                    }
                    print(
                        "[SELECTED] minimum tested passing configuration: "
                        f"m={m}, ef_construction={efc}, "
                        f"ef_search={first_passing_search['ef_search']}",
                        flush=True,
                    )
                    break

        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_M_V2_PGVECTOR_COST_TUNING",
            "contract_version": "1.0",
            "profile": "M",
            "records": N,
            "vector_corpus_version": CORPUS_VERSION,
            "dimensions": DIM,
            "active_vector_dimensions": ACTIVE_VECTOR_DIMS,
            "top_k": TOP_K,
            "recall_threshold": RECALL_THRESHOLD,
            "ingest_seconds": round(ingest_seconds, 4),
            "results": results,
            "selected_minimum_cost_passing_configuration": selected,
            "image_digest": image_digest(),
            "started_epoch": started,
            "completed_epoch": time.time(),
            "passed": selected is not None,
        }
    except Exception as exc:
        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_M_V2_PGVECTOR_COST_TUNING",
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
