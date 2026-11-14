from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import time
import urllib.request
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
A = 7919
B = 104729

PG_EF_VALUES = [300, 500, 800, 1000]
QDRANT_EF_VALUES = [64, 128, 256, 512, 1024]


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


def id_for_position(position: int) -> int:
    inv = pow(A, -1, N)
    residue = ((position - B) * inv) % N
    return N if residue == 0 else residue


def exact_topk(query_id: int) -> list[int]:
    center = (query_id * A + B) % N
    candidates: list[tuple[int, int]] = []
    distance = 0
    while len(candidates) < TOP_K + 4:
        positions = [center] if distance == 0 else [
            (center - distance) % N,
            (center + distance) % N,
        ]
        for pos in positions:
            candidates.append((distance, id_for_position(pos)))
        distance += 1
    candidates.sort(key=lambda x: (x[0], x[1]))
    return [item[1] for item in candidates[:TOP_K]]


def recall_at_k(expected: list[int], actual: list[int]) -> float:
    return len(set(expected) & set(actual[:TOP_K])) / TOP_K


def sha256_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def image_digest(container: str) -> str | None:
    p = subprocess.run(
        ["docker", "inspect", "-f", "{{.Image}}", container],
        capture_output=True,
        text=True,
        check=False,
    )
    return p.stdout.strip() if p.returncode == 0 else None


def http_json(method: str, url: str, body: dict[str, Any] | None = None, timeout: int = 120):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def qdrant_ids(payload: dict[str, Any]) -> list[int]:
    result = payload.get("result", {})
    points = result.get("points") if isinstance(result, dict) else result
    return [int(point["id"]) for point in (points or [])]


def evaluate(query_fn, expected: dict[int, list[int]]) -> dict[str, Any]:
    ids = query_ids()
    for qid in ids:
        query_fn(qid)

    latencies: list[float] = []
    recalls: list[float] = []

    for _ in range(REPETITIONS):
        for qid in ids:
            t0 = time.perf_counter_ns()
            actual = query_fn(qid)
            latencies.append((time.perf_counter_ns() - t0) / 1_000_000)
            recalls.append(recall_at_k(expected[qid], actual))

    mean_recall = statistics.fmean(recalls)
    return {
        "recall_at_k_mean": round(mean_recall, 6),
        "recall_at_k_min": round(min(recalls), 6),
        "latency": latency_summary(latencies),
        "passes_recall_threshold": mean_recall >= RECALL_THRESHOLD,
    }


def tune_pgvector() -> dict[str, Any]:
    theoretical_expected = {qid: exact_topk(qid) for qid in query_ids()}

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
            cur.execute("DROP TABLE IF EXISTS bench_vec_m_tuning")
            cur.execute(
                "CREATE TABLE bench_vec_m_tuning("
                "id integer PRIMARY KEY, v vector(384) NOT NULL)"
            )

        t0 = time.perf_counter()
        with conn.cursor() as cur:
            with cur.copy("COPY bench_vec_m_tuning (id, v) FROM STDIN") as copy:
                for i in range(1, N + 1):
                    copy.write_row((i, vector_text(vector_for(i))))
        ingest_seconds = time.perf_counter() - t0

        with conn.cursor() as cur:
            t1 = time.perf_counter()
            cur.execute(
                "CREATE INDEX bench_vec_m_tuning_hnsw "
                "ON bench_vec_m_tuning USING hnsw (v vector_cosine_ops)"
            )
            index_seconds = time.perf_counter() - t1
            cur.execute("ANALYZE bench_vec_m_tuning")

        # Ground truth must be calculated from the vectors as actually stored
        # by pgvector. At 100k, float32 representation makes several theoretical
        # neighbors effectively tied, so pre-storage double-precision geometry
        # is diagnostic only and must not be the ANN qualification oracle.
        stored_exact: dict[int, list[int]] = {}
        with conn.cursor() as cur:
            cur.execute("SET enable_indexscan = off")
            cur.execute("SET enable_bitmapscan = off")
            for qid in query_ids():
                cur.execute(
                    "SELECT id FROM bench_vec_m_tuning "
                    "ORDER BY v <=> %s::vector LIMIT %s",
                    (vector_text(vector_for(qid)), TOP_K),
                )
                stored_exact[qid] = [row[0] for row in cur.fetchall()]
            cur.execute("SET enable_indexscan = on")
            cur.execute("SET enable_bitmapscan = on")

        representation_recalls = [
            recall_at_k(theoretical_expected[qid], stored_exact[qid])
            for qid in query_ids()
        ]

        results = []
        selected = None

        for ef in PG_EF_VALUES:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT set_config('hnsw.ef_search', %s, false)",
                    (str(ef),),
                )

                def query(qid: int) -> list[int]:
                    cur.execute(
                        "SELECT id FROM bench_vec_m_tuning "
                        "ORDER BY v <=> %s::vector LIMIT %s",
                        (vector_text(vector_for(qid)), TOP_K),
                    )
                    return [row[0] for row in cur.fetchall()]

                item = {"ef_search": ef, **evaluate(query, stored_exact)}

            results.append(item)
            if selected is None and item["passes_recall_threshold"]:
                selected = item

    return {
        "candidate": "pgvector",
        "profile": "M",
        "records": N,
        "dimensions": DIM,
        "top_k": TOP_K,
        "index": "HNSW vector_cosine_ops",
        "tested_ef_search": PG_EF_VALUES,
        "ground_truth": {
            "method": "exact sequential scan over stored pgvector values",
            "theoretical_pre_storage_agreement_mean": round(
                statistics.fmean(representation_recalls), 6
            ),
            "theoretical_pre_storage_agreement_min": round(
                min(representation_recalls), 6
            ),
            "qualification_uses_theoretical_pre_storage_reference": False,
        },
        "ingest_seconds": round(ingest_seconds, 4),
        "index_build_seconds": round(index_seconds, 4),
        "results": results,
        "selected_minimum_passing_configuration": selected,
        "image_digest": image_digest("father-bench-pgvector"),
        "passed": selected is not None,
    }


def wait_qdrant_index(base: str, collection: str, timeout_seconds: int = 180) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last = {}
    while time.time() < deadline:
        last = http_json("GET", f"{base}/collections/{collection}", timeout=20)
        result = last.get("result", {})
        status = result.get("status")
        optimizer_status = result.get("optimizer_status")
        indexed = result.get("indexed_vectors_count", 0) or 0
        points = result.get("points_count", 0) or 0
        optimizer_ok = optimizer_status == "ok" or (
            isinstance(optimizer_status, dict)
            and optimizer_status.get("ok") is True
        )
        if status == "green" and optimizer_ok and points >= N and indexed >= int(N * 0.95):
            return {
                "ready": True,
                "status": status,
                "optimizer_status": optimizer_status,
                "indexed_vectors_count": indexed,
                "points_count": points,
            }
        time.sleep(1)

    result = last.get("result", {}) if isinstance(last, dict) else {}
    return {
        "ready": False,
        "status": result.get("status"),
        "optimizer_status": result.get("optimizer_status"),
        "indexed_vectors_count": result.get("indexed_vectors_count"),
        "points_count": result.get("points_count"),
    }


def tune_qdrant() -> dict[str, Any]:
    base = "http://127.0.0.1:56333"
    collection = "father_p1_m_tuning"
    theoretical_expected = {qid: exact_topk(qid) for qid in query_ids()}

    try:
        http_json("DELETE", f"{base}/collections/{collection}", timeout=20)
    except Exception:
        pass

    http_json(
        "PUT",
        f"{base}/collections/{collection}",
        {
            "vectors": {"size": DIM, "distance": "Cosine"},
            "hnsw_config": {
                "m": 16,
                "ef_construct": 100,
                "full_scan_threshold": 10000,
            },
        },
    )

    t0 = time.perf_counter()
    batch_size = 500
    for start in range(1, N + 1, batch_size):
        end = min(N + 1, start + batch_size)
        points = [
            {"id": i, "vector": vector_for(i)}
            for i in range(start, end)
        ]
        http_json(
            "PUT",
            f"{base}/collections/{collection}/points?wait=true",
            {"points": points},
            timeout=180,
        )
    ingest_seconds = time.perf_counter() - t0

    index_state = wait_qdrant_index(base, collection)

    def query_with(ef: int | None, exact: bool = False):
        def query(qid: int) -> list[int]:
            params: dict[str, Any] = {"exact": exact}
            if ef is not None:
                params["hnsw_ef"] = ef
            payload = http_json(
                "POST",
                f"{base}/collections/{collection}/points/query",
                {
                    "query": vector_for(qid),
                    "limit": TOP_K,
                    "with_payload": False,
                    "with_vector": False,
                    "params": params,
                },
                timeout=120,
            )
            return qdrant_ids(payload)
        return query

    exact_query = query_with(None, exact=True)
    stored_exact = {qid: exact_query(qid) for qid in query_ids()}
    representation_recalls = [
        recall_at_k(theoretical_expected[qid], stored_exact[qid])
        for qid in query_ids()
    ]
    exact_control = evaluate(exact_query, stored_exact)

    results = []
    selected = None
    for ef in QDRANT_EF_VALUES:
        item = {
            "hnsw_ef": ef,
            **evaluate(query_with(ef, exact=False), stored_exact),
        }
        results.append(item)
        if selected is None and item["passes_recall_threshold"]:
            selected = item

    return {
        "candidate": "qdrant",
        "profile": "M",
        "records": N,
        "dimensions": DIM,
        "top_k": TOP_K,
        "index": "Qdrant HNSW",
        "hnsw_config": {"m": 16, "ef_construct": 100, "full_scan_threshold": 10000},
        "index_state_before_measurement": index_state,
        "ingest_seconds": round(ingest_seconds, 4),
        "ground_truth": {
            "method": "Qdrant exact=true over stored float32 vectors",
            "theoretical_pre_storage_agreement_mean": round(
                statistics.fmean(representation_recalls), 6
            ),
            "theoretical_pre_storage_agreement_min": round(
                min(representation_recalls), 6
            ),
            "qualification_uses_theoretical_pre_storage_reference": False,
        },
        "exact_control": exact_control,
        "tested_hnsw_ef": QDRANT_EF_VALUES,
        "results": results,
        "selected_minimum_passing_configuration": selected,
        "image_digest": image_digest("father-bench-qdrant"),
        "passed": selected is not None and exact_control["recall_at_k_mean"] >= 0.999,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", choices=["pgvector", "qdrant"], required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    started = time.time()
    try:
        result = tune_pgvector() if args.candidate == "pgvector" else tune_qdrant()
        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_M_VECTOR_TUNING",
            "contract_version": "1.0",
            "seed": SEED,
            "recall_threshold": RECALL_THRESHOLD,
            "started_epoch": started,
            "completed_epoch": time.time(),
            "result": result,
        }
    except Exception as exc:
        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_M_VECTOR_TUNING",
            "contract_version": "1.0",
            "seed": SEED,
            "candidate": args.candidate,
            "started_epoch": started,
            "completed_epoch": time.time(),
            "status": "FAIL",
            "reason": repr(exc),
            "passed": False,
        }

    envelope["evidence_hash"] = sha256_json(envelope)
    Path(args.out).write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    print(json.dumps(envelope, indent=2))

    if "result" in envelope:
        return 0 if envelope["result"]["passed"] else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
