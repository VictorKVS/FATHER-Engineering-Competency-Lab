from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import statistics
import subprocess
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

import psycopg

DIM = 384
TOP_K = 10
QUERY_COUNT = 30
REPETITIONS = 3
SEED = 20261114
RECALL_THRESHOLD = 0.95
PGVECTOR_M = 48
PGVECTOR_EF_CONSTRUCTION = 512
PGVECTOR_EF_SEARCH = 1000
QDRANT_HNSW_EF = 64
PROFILES = {
    "M": 100_000,
    "L": 1_000_000,
    "XL": 10_000_000,
}
CONCURRENCY_LEVELS = [1, 4, 16]
A = 7919
B = 104729
_thread_local = threading.local()


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


def latency_summary_ms(samples: list[float]) -> dict[str, float]:
    return {
        "count": len(samples),
        "mean_ms": round(statistics.fmean(samples), 4) if samples else 0.0,
        "p50_ms": round(percentile(samples, 0.50), 4),
        "p95_ms": round(percentile(samples, 0.95), 4),
        "p99_ms": round(percentile(samples, 0.99), 4),
        "max_ms": round(max(samples), 4) if samples else 0.0,
    }


def vector_for(i: int, n: int) -> list[float]:
    theta = (2.0 * math.pi * ((i * A + B) % n)) / n
    return [math.cos(theta), math.sin(theta)] + [0.0] * (DIM - 2)


def vector_text(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.9f}" for x in v) + "]"


def query_ids(n: int) -> list[int]:
    return [((i * 313) + 17) % n + 1 for i in range(QUERY_COUNT)]


def id_for_position(position: int, n: int) -> int:
    inv = pow(A, -1, n)
    residue = ((position - B) * inv) % n
    return n if residue == 0 else residue


def exact_topk(query_id: int, n: int) -> list[int]:
    # A is coprime with M/L/XL profile sizes, so the mapping is a permutation.
    # We only need neighboring angular positions; no O(N) reference scan.
    center = (query_id * A + B) % n
    candidates: list[tuple[int, int]] = []
    distance = 0
    while len(candidates) < TOP_K + 4:
        if distance == 0:
            positions = [center]
        else:
            positions = [(center - distance) % n, (center + distance) % n]
        for pos in positions:
            candidates.append((distance, id_for_position(pos, n)))
        distance += 1
    candidates.sort(key=lambda x: (x[0], x[1]))
    return [item[1] for item in candidates[:TOP_K]]


def recall_at_k(expected: list[int], actual: list[int]) -> float:
    return len(set(expected) & set(actual[:TOP_K])) / TOP_K


def sha256_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def docker_stats(container: str) -> dict[str, Any]:
    p = subprocess.run(
        ["docker", "stats", container, "--no-stream", "--format", "{{json .}}"],
        capture_output=True, text=True, check=False,
    )
    if p.returncode != 0 or not p.stdout.strip():
        return {"error": p.stderr.strip() or "docker stats unavailable"}
    try:
        return json.loads(p.stdout.strip())
    except json.JSONDecodeError:
        return {"raw": p.stdout.strip()}


def docker_du(container: str, path: str) -> dict[str, Any]:
    p = subprocess.run(
        ["docker", "exec", container, "sh", "-lc", f"du -sb {path} 2>/dev/null || du -sk {path}"],
        capture_output=True, text=True, check=False,
    )
    return {
        "path": path,
        "raw": p.stdout.strip(),
        "exit_code": p.returncode,
    }


def image_digest(container: str) -> str | None:
    p = subprocess.run(
        ["docker", "inspect", "-f", "{{.Image}}", container],
        capture_output=True, text=True, check=False,
    )
    return p.stdout.strip() if p.returncode == 0 else None


def pg_connect(port: int):
    return psycopg.connect(
        host="127.0.0.1",
        port=port,
        dbname="father_bench",
        user="father",
        password="father_bench",
        autocommit=True,
    )


def pg_thread_connection(port: int, ef_search: int | None = None):
    key = f"conn_{port}_{ef_search}"
    conn = getattr(_thread_local, key, None)
    if conn is None or conn.closed:
        conn = pg_connect(port)
        if ef_search is not None:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT set_config('hnsw.ef_search', %s, false)",
                    (str(ef_search),),
                )
        setattr(_thread_local, key, conn)
    return conn


def run_concurrency(query_fn, ids: list[int], concurrency: int) -> dict[str, Any]:
    work = ids * REPETITIONS
    latencies: list[float] = []
    errors = 0

    def wrapped(qid: int):
        t0 = time.perf_counter_ns()
        try:
            result = query_fn(qid)
            ok = True
        except Exception as exc:
            result = {"error": repr(exc)}
            ok = False
        elapsed = (time.perf_counter_ns() - t0) / 1_000_000
        return elapsed, ok, result

    t_wall = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(wrapped, qid) for qid in work]
        for fut in concurrent.futures.as_completed(futures):
            elapsed, ok, _ = fut.result()
            latencies.append(elapsed)
            if not ok:
                errors += 1
    wall = time.perf_counter() - t_wall

    completed = len(work) - errors
    return {
        "concurrency": concurrency,
        "operations": len(work),
        "completed": completed,
        "errors": errors,
        "wall_seconds": round(wall, 4),
        "throughput_ops_sec": round(completed / wall, 2) if wall > 0 else 0.0,
        "latency": latency_summary_ms(latencies),
        "passed": errors == 0,
    }


def run_rel(candidate: str, n: int, profile: str) -> dict[str, Any]:
    port = 55432 if candidate == "postgres" else 55433
    container = f"father-bench-{candidate}"
    before = docker_stats(container)

    with pg_connect(port) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS bench_rel_scale")
            cur.execute(
                """
                CREATE TABLE bench_rel_scale(
                    id integer PRIMARY KEY,
                    domain text NOT NULL,
                    class_id integer NOT NULL,
                    score integer NOT NULL,
                    body text NOT NULL
                )
                """
            )

        t0 = time.perf_counter()
        with conn.cursor() as cur:
            with cur.copy(
                "COPY bench_rel_scale (id, domain, class_id, score, body) FROM STDIN"
            ) as copy:
                for i in range(1, n + 1):
                    copy.write_row((
                        i,
                        f"domain-{i % 17}",
                        i % 7,
                        (i * 37) % 1000,
                        f"father deterministic scale record {i}",
                    ))
        ingest_seconds = time.perf_counter() - t0

        with conn.cursor() as cur:
            t_idx = time.perf_counter()
            cur.execute(
                "CREATE INDEX bench_rel_scale_filter_idx "
                "ON bench_rel_scale(domain, class_id, score)"
            )
            index_seconds = time.perf_counter() - t_idx
            cur.execute("ANALYZE bench_rel_scale")

    ids = query_ids(n)

    def query(qid: int):
        conn = pg_thread_connection(port)
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM bench_rel_scale WHERE id=%s", (qid,))
            row = cur.fetchone()
            if row is None or row[0] != qid:
                raise RuntimeError(f"incorrect result for {qid}")
            return row[0]

    # warm-up
    for qid in ids:
        query(qid)

    concurrency_results = [
        run_concurrency(query, ids, c) for c in CONCURRENCY_LEVELS
    ]

    after = docker_stats(container)
    disk = docker_du(container, "/var/lib/postgresql")
    return {
        "league": f"REL-{profile}",
        "candidate": candidate,
        "records": n,
        "ingest_seconds": round(ingest_seconds, 4),
        "ingest_records_per_second": round(n / ingest_seconds, 2),
        "index_build_seconds": round(index_seconds, 4),
        "concurrency_results": concurrency_results,
        "resource_snapshot_before": before,
        "resource_snapshot_after": after,
        "disk_usage": disk,
        "image_digest": image_digest(container),
        "correctness_pass": all(x["passed"] for x in concurrency_results),
        "passed": all(x["passed"] for x in concurrency_results),
    }


def run_vec_pgvector(n: int, profile: str) -> dict[str, Any]:
    container = "father-bench-pgvector"
    before = docker_stats(container)
    ids = query_ids(n)

    with pg_connect(55433) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("DROP TABLE IF EXISTS bench_vec_scale")
            cur.execute(
                "CREATE TABLE bench_vec_scale("
                "id integer PRIMARY KEY, domain text NOT NULL, v vector(384) NOT NULL)"
            )

        t0 = time.perf_counter()
        with conn.cursor() as cur:
            with cur.copy("COPY bench_vec_scale (id, domain, v) FROM STDIN") as copy:
                for i in range(1, n + 1):
                    copy.write_row((i, f"domain-{i % 17}", vector_text(vector_for(i, n))))
        ingest_seconds = time.perf_counter() - t0

        # Exact persisted ground truth is captured before ANN index creation.
        exact_expected: dict[int, list[int]] = {}
        exact_latencies: list[float] = []
        with conn.cursor() as cur:
            for qid in ids:
                t_exact = time.perf_counter_ns()
                cur.execute(
                    "SELECT id FROM bench_vec_scale "
                    "ORDER BY v <=> %s::vector LIMIT %s",
                    (vector_text(vector_for(qid, n)), TOP_K),
                )
                exact_expected[qid] = [r[0] for r in cur.fetchall()]
                exact_latencies.append(
                    (time.perf_counter_ns() - t_exact) / 1_000_000
                )

        with conn.cursor() as cur:
            t_idx = time.perf_counter()
            cur.execute(
                "CREATE INDEX bench_vec_scale_hnsw "
                "ON bench_vec_scale USING hnsw (v vector_cosine_ops) "
                f"WITH (m = {PGVECTOR_M}, "
                f"ef_construction = {PGVECTOR_EF_CONSTRUCTION})"
            )
            index_seconds = time.perf_counter() - t_idx
            cur.execute("ANALYZE bench_vec_scale")

    def query(qid: int):
        conn = pg_thread_connection(55433, PGVECTOR_EF_SEARCH)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM bench_vec_scale "
                "ORDER BY v <=> %s::vector LIMIT %s",
                (vector_text(vector_for(qid, n)), TOP_K),
            )
            return [r[0] for r in cur.fetchall()]

    for qid in ids:
        query(qid)

    concurrency_results = []
    quality_samples = []

    for c in CONCURRENCY_LEVELS:
        perf = run_concurrency(query, ids, c)
        actual_by_id = {qid: query(qid) for qid in ids}
        recalls = [
            recall_at_k(exact_expected[qid], actual_by_id[qid])
            for qid in ids
        ]
        mean_recall = statistics.fmean(recalls)
        perf["recall_at_k_mean"] = round(mean_recall, 6)
        perf["recall_at_k_min"] = round(min(recalls), 6)
        perf["quality_pass"] = mean_recall >= RECALL_THRESHOLD
        perf["passed"] = perf["passed"] and perf["quality_pass"]
        concurrency_results.append(perf)
        quality_samples.extend(recalls)

    after = docker_stats(container)
    disk = docker_du(container, "/var/lib/postgresql")
    overall_recall = statistics.fmean(quality_samples)

    return {
        "league": f"VEC-{profile}",
        "candidate": "pgvector",
        "records": n,
        "dimensions": DIM,
        "top_k": TOP_K,
        "index": "HNSW vector_cosine_ops",
        "m": PGVECTOR_M,
        "ef_construction": PGVECTOR_EF_CONSTRUCTION,
        "ef_search": PGVECTOR_EF_SEARCH,
        "ground_truth": {
            "method": "exact search over persisted pgvector values before ANN index",
            "exact_latency": latency_summary_ms(exact_latencies),
        },
        "ingest_seconds": round(ingest_seconds, 4),
        "ingest_records_per_second": round(n / ingest_seconds, 2),
        "index_build_seconds": round(index_seconds, 4),
        "concurrency_results": concurrency_results,
        "recall_at_k_mean": round(overall_recall, 6),
        "resource_snapshot_before": before,
        "resource_snapshot_after": after,
        "disk_usage": disk,
        "image_digest": image_digest(container),
        "passed": all(x["passed"] for x in concurrency_results),
    }


def http_json(method: str, url: str, body: dict[str, Any] | None = None, timeout: int = 120):
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def qdrant_ids(payload: dict[str, Any]) -> list[int]:
    result = payload.get("result", {})
    points = result.get("points") if isinstance(result, dict) else result
    return [int(p["id"]) for p in (points or [])]


def run_vec_qdrant(n: int, profile: str) -> dict[str, Any]:
    container = "father-bench-qdrant"
    base = "http://127.0.0.1:56333"
    before = docker_stats(container)
    ids = query_ids(n)

    try:
        http_json("DELETE", f"{base}/collections/father_p1_scale", timeout=20)
    except Exception:
        pass

    http_json(
        "PUT",
        f"{base}/collections/father_p1_scale",
        {
            "vectors": {"size": DIM, "distance": "Cosine"},
            "hnsw_config": {
                "m": 16,
                "ef_construct": 100,
                "full_scan_threshold": 10000,
            },
        },
    )

    batch_size = 500
    t0 = time.perf_counter()
    for start in range(1, n + 1, batch_size):
        end = min(n + 1, start + batch_size)
        points = [
            {
                "id": i,
                "vector": vector_for(i, n),
                "payload": {"domain": f"domain-{i % 17}"},
            }
            for i in range(start, end)
        ]
        http_json(
            "PUT",
            f"{base}/collections/father_p1_scale/points?wait=true",
            {"points": points},
            timeout=180,
        )
    ingest_seconds = time.perf_counter() - t0

    def query_with(qid: int, *, exact: bool) -> list[int]:
        params: dict[str, Any] = {"exact": exact}
        if not exact:
            params["hnsw_ef"] = QDRANT_HNSW_EF
        payload = http_json(
            "POST",
            f"{base}/collections/father_p1_scale/points/query",
            {
                "query": vector_for(qid, n),
                "limit": TOP_K,
                "with_payload": False,
                "with_vector": False,
                "params": params,
            },
            timeout=120,
        )
        return qdrant_ids(payload)

    exact_expected = {qid: query_with(qid, exact=True) for qid in ids}

    def query(qid: int):
        return query_with(qid, exact=False)

    for qid in ids:
        query(qid)

    concurrency_results = []
    quality_samples = []
    for c in CONCURRENCY_LEVELS:
        perf = run_concurrency(query, ids, c)
        actual_by_id = {qid: query(qid) for qid in ids}
        recalls = [
            recall_at_k(exact_expected[qid], actual_by_id[qid])
            for qid in ids
        ]
        mean_recall = statistics.fmean(recalls)
        perf["recall_at_k_mean"] = round(mean_recall, 6)
        perf["recall_at_k_min"] = round(min(recalls), 6)
        perf["quality_pass"] = mean_recall >= RECALL_THRESHOLD
        perf["passed"] = perf["passed"] and perf["quality_pass"]
        concurrency_results.append(perf)
        quality_samples.extend(recalls)

    after = docker_stats(container)
    disk = docker_du(container, "/qdrant/storage")
    overall_recall = statistics.fmean(quality_samples)

    return {
        "league": f"VEC-{profile}",
        "candidate": "qdrant",
        "records": n,
        "dimensions": DIM,
        "top_k": TOP_K,
        "index": "Qdrant HNSW",
        "hnsw_config": {
            "m": 16,
            "ef_construct": 100,
            "full_scan_threshold": 10000,
        },
        "hnsw_ef": QDRANT_HNSW_EF,
        "ground_truth": {
            "method": "Qdrant exact=true over persisted vectors",
        },
        "ingest_seconds": round(ingest_seconds, 4),
        "ingest_records_per_second": round(n / ingest_seconds, 2),
        "index_build_seconds": None,
        "concurrency_results": concurrency_results,
        "recall_at_k_mean": round(overall_recall, 6),
        "resource_snapshot_before": before,
        "resource_snapshot_after": after,
        "disk_usage": disk,
        "image_digest": image_digest(container),
        "passed": all(x["passed"] for x in concurrency_results),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--league", choices=["rel", "vec"], required=True)
    parser.add_argument("--candidate", choices=["postgres", "pgvector", "qdrant"], required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    profile = args.profile
    n = PROFILES[profile]
    started = time.time()

    envelope: dict[str, Any]
    try:
        if args.league == "rel":
            if args.candidate not in {"postgres", "pgvector"}:
                raise ValueError("REL supports postgres/pgvector")
            result = run_rel(args.candidate, n, profile)
        elif args.candidate == "pgvector":
            result = run_vec_pgvector(n, profile)
        elif args.candidate == "qdrant":
            result = run_vec_qdrant(n, profile)
        else:
            raise ValueError("VEC supports pgvector/qdrant")

        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_SCALE",
            "contract_version": "1.0",
            "profile": profile,
            "records": n,
            "storage_mode": "docker_named_volume",
            "compose_profile": "scale",
            "seed": SEED,
            "started_epoch": started,
            "completed_epoch": time.time(),
            "result": result,
        }
    except Exception as exc:
        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_SCALE",
            "contract_version": "1.0",
            "profile": profile,
            "records": n,
            "seed": SEED,
            "league": args.league,
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
        return 0 if envelope["result"].get("passed") else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
