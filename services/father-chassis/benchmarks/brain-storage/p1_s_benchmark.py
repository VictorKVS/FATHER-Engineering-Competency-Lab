from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

N = 10_000
DIM = 384
TOP_K = 10
QUERY_COUNT = 30
MEASURED_REPETITIONS = 3
WARMUP_REPETITIONS = 1
SEED = 20261114


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
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


def vector_for(i: int) -> list[float]:
    # 384 dimensions are preserved, while the first two coordinates define
    # a deterministic unit-circle geometry. This gives an exact analytical
    # reference without requiring a second vector database.
    theta = (2.0 * math.pi * ((i * 7919 + 104729) % N)) / N
    return [math.cos(theta), math.sin(theta)] + [0.0] * (DIM - 2)


def vector_text(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.9f}" for x in v) + "]"


def query_ids() -> list[int]:
    # Deterministic, evenly distributed IDs.
    return [((i * 313) + 17) % N + 1 for i in range(QUERY_COUNT)]


def exact_topk(query_id: int) -> list[int]:
    q = vector_for(query_id)
    qx, qy = q[0], q[1]
    scored: list[tuple[float, int]] = []
    for i in range(1, N + 1):
        v = vector_for(i)
        score = qx * v[0] + qy * v[1]
        scored.append((score, i))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [i for _, i in scored[:TOP_K]]


def recall_at_k(expected: list[int], actual: list[int]) -> float:
    return len(set(expected) & set(actual[:TOP_K])) / TOP_K


def sha256_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def docker_stats(container: str) -> dict[str, Any]:
    result = subprocess.run(
        ["docker", "stats", container, "--no-stream", "--format", "{{json .}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return {"error": result.stderr.strip() or "docker stats unavailable"}
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"raw": result.stdout.strip()}


def image_digest(container: str) -> str | None:
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.Image}}", container],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def require_psycopg():
    try:
        import psycopg  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "P1_ENVIRONMENT_BLOCKED: psycopg is required. "
            'Install with: python -m pip install "psycopg[binary]>=3.2"'
        ) from exc


def pg_connect(port: int):
    require_psycopg()
    import psycopg

    return psycopg.connect(
        host="127.0.0.1",
        port=port,
        dbname="father_bench",
        user="father",
        password="father_bench",
        autocommit=True,
    )


def run_rel(candidate: str) -> dict[str, Any]:
    if candidate not in {"postgres", "pgvector"}:
        raise ValueError(candidate)

    port = 55432 if candidate == "postgres" else 55433
    container = f"father-bench-{candidate}"
    before = docker_stats(container)

    with pg_connect(port) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS bench_rel")
            cur.execute(
                """
                CREATE TABLE bench_rel(
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
                "COPY bench_rel (id, domain, class_id, score, body) FROM STDIN"
            ) as copy:
                for i in range(1, N + 1):
                    copy.write_row(
                        (
                            i,
                            f"domain-{i % 17}",
                            i % 7,
                            (i * 37) % 1000,
                            f"father deterministic benchmark record {i}",
                        )
                    )
        ingest_seconds = time.perf_counter() - t0

        with conn.cursor() as cur:
            t_idx = time.perf_counter()
            cur.execute("CREATE INDEX bench_rel_filter_idx ON bench_rel(domain, class_id, score)")
            index_seconds = time.perf_counter() - t_idx
            cur.execute("ANALYZE bench_rel")

        queries = query_ids()

        # Warm-up
        with conn.cursor() as cur:
            for qid in queries:
                cur.execute("SELECT id, score FROM bench_rel WHERE id = %s", (qid,))
                cur.fetchone()
                cur.execute(
                    """
                    SELECT id FROM bench_rel
                    WHERE domain=%s AND class_id=%s AND score >= %s
                    ORDER BY score DESC, id
                    LIMIT 20
                    """,
                    (f"domain-{qid % 17}", qid % 7, (qid * 37) % 500),
                )
                cur.fetchall()

        point_samples: list[float] = []
        filter_samples: list[float] = []
        correctness = True

        for _ in range(MEASURED_REPETITIONS):
            with conn.cursor() as cur:
                for qid in queries:
                    t1 = time.perf_counter_ns()
                    cur.execute("SELECT id, score FROM bench_rel WHERE id = %s", (qid,))
                    row = cur.fetchone()
                    point_samples.append((time.perf_counter_ns() - t1) / 1_000_000)
                    correctness = correctness and row is not None and row[0] == qid

                    t2 = time.perf_counter_ns()
                    cur.execute(
                        """
                        SELECT id, score FROM bench_rel
                        WHERE domain=%s AND class_id=%s AND score >= %s
                        ORDER BY score DESC, id
                        LIMIT 20
                        """,
                        (f"domain-{qid % 17}", qid % 7, (qid * 37) % 500),
                    )
                    rows = cur.fetchall()
                    filter_samples.append((time.perf_counter_ns() - t2) / 1_000_000)
                    correctness = correctness and len(rows) <= 20

        update_samples: list[float] = []
        with conn.cursor() as cur:
            for qid in queries:
                t3 = time.perf_counter_ns()
                cur.execute("UPDATE bench_rel SET score=score+1 WHERE id=%s", (qid,))
                update_samples.append((time.perf_counter_ns() - t3) / 1_000_000)

    after = docker_stats(container)
    return {
        "league": "REL-S",
        "candidate": candidate,
        "records": N,
        "ingest_seconds": round(ingest_seconds, 4),
        "ingest_records_per_second": round(N / ingest_seconds, 2),
        "index_build_seconds": round(index_seconds, 4),
        "point_lookup": latency_summary_ms(point_samples),
        "filtered_lookup": latency_summary_ms(filter_samples),
        "update_latency": latency_summary_ms(update_samples),
        "correctness_pass": bool(correctness),
        "resource_snapshot_before": before,
        "resource_snapshot_after": after,
        "image_digest": image_digest(container),
        "passed": bool(correctness),
    }


def http_json(method: str, url: str, body: dict[str, Any] | None = None, timeout: int = 30):
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def qdrant_result_ids(payload: dict[str, Any]) -> list[int]:
    result = payload.get("result", {})
    points = result.get("points") if isinstance(result, dict) else result
    if points is None:
        points = []
    return [int(p["id"]) for p in points]


def run_vec_pgvector() -> dict[str, Any]:
    candidate = "pgvector"
    container = "father-bench-pgvector"
    before = docker_stats(container)

    expected = {qid: exact_topk(qid) for qid in query_ids()}

    with pg_connect(55433) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("DROP TABLE IF EXISTS bench_vec")
            cur.execute(
                "CREATE TABLE bench_vec(id integer PRIMARY KEY, domain text NOT NULL, v vector(384) NOT NULL)"
            )

        t0 = time.perf_counter()
        with conn.cursor() as cur:
            with cur.copy("COPY bench_vec (id, domain, v) FROM STDIN") as copy:
                for i in range(1, N + 1):
                    copy.write_row((i, f"domain-{i % 17}", vector_text(vector_for(i))))
        ingest_seconds = time.perf_counter() - t0

        with conn.cursor() as cur:
            t_idx = time.perf_counter()
            cur.execute("CREATE INDEX bench_vec_hnsw ON bench_vec USING hnsw (v vector_cosine_ops)")
            index_seconds = time.perf_counter() - t_idx
            cur.execute("ANALYZE bench_vec")
            cur.execute("SET hnsw.ef_search = 100")

        latencies: list[float] = []
        recalls: list[float] = []
        qids = query_ids()

        # warm-up
        with conn.cursor() as cur:
            for qid in qids:
                qv = vector_text(vector_for(qid))
                cur.execute(
                    "SELECT id FROM bench_vec ORDER BY v <=> %s::vector LIMIT %s",
                    (qv, TOP_K),
                )
                cur.fetchall()

        for _ in range(MEASURED_REPETITIONS):
            with conn.cursor() as cur:
                for qid in qids:
                    qv = vector_text(vector_for(qid))
                    t1 = time.perf_counter_ns()
                    cur.execute(
                        "SELECT id FROM bench_vec ORDER BY v <=> %s::vector LIMIT %s",
                        (qv, TOP_K),
                    )
                    actual = [r[0] for r in cur.fetchall()]
                    latencies.append((time.perf_counter_ns() - t1) / 1_000_000)
                    recalls.append(recall_at_k(expected[qid], actual))

    after = docker_stats(container)
    mean_recall = statistics.fmean(recalls) if recalls else 0.0
    return {
        "league": "VEC-S",
        "candidate": candidate,
        "records": N,
        "dimensions": DIM,
        "top_k": TOP_K,
        "index": "HNSW vector_cosine_ops",
        "ingest_seconds": round(ingest_seconds, 4),
        "ingest_records_per_second": round(N / ingest_seconds, 2),
        "index_build_seconds": round(index_seconds, 4),
        "query_latency": latency_summary_ms(latencies),
        "recall_at_k_mean": round(mean_recall, 6),
        "recall_at_k_min": round(min(recalls), 6) if recalls else 0.0,
        "resource_snapshot_before": before,
        "resource_snapshot_after": after,
        "image_digest": image_digest(container),
        "passed": mean_recall >= 0.95,
    }


def run_vec_qdrant() -> dict[str, Any]:
    candidate = "qdrant"
    container = "father-bench-qdrant"
    base = "http://127.0.0.1:56333"
    before = docker_stats(container)

    expected = {qid: exact_topk(qid) for qid in query_ids()}

    try:
        http_json("DELETE", f"{base}/collections/father_p1_vec", timeout=10)
    except Exception:
        pass

    http_json(
        "PUT",
        f"{base}/collections/father_p1_vec",
        {"vectors": {"size": DIM, "distance": "Cosine"}},
    )

    t0 = time.perf_counter()
    batch_size = 250
    for start in range(1, N + 1, batch_size):
        end = min(N + 1, start + batch_size)
        points = [
            {
                "id": i,
                "vector": vector_for(i),
                "payload": {"domain": f"domain-{i % 17}"},
            }
            for i in range(start, end)
        ]
        http_json(
            "PUT",
            f"{base}/collections/father_p1_vec/points?wait=true",
            {"points": points},
            timeout=120,
        )
    ingest_seconds = time.perf_counter() - t0

    qids = query_ids()
    latencies: list[float] = []
    recalls: list[float] = []

    def query(qid: int) -> list[int]:
        payload = http_json(
            "POST",
            f"{base}/collections/father_p1_vec/points/query",
            {
                "query": vector_for(qid),
                "limit": TOP_K,
                "with_payload": False,
                "with_vector": False,
            },
            timeout=30,
        )
        return qdrant_result_ids(payload)

    for qid in qids:
        query(qid)

    for _ in range(MEASURED_REPETITIONS):
        for qid in qids:
            t1 = time.perf_counter_ns()
            actual = query(qid)
            latencies.append((time.perf_counter_ns() - t1) / 1_000_000)
            recalls.append(recall_at_k(expected[qid], actual))

    after = docker_stats(container)
    mean_recall = statistics.fmean(recalls) if recalls else 0.0
    return {
        "league": "VEC-S",
        "candidate": candidate,
        "records": N,
        "dimensions": DIM,
        "top_k": TOP_K,
        "index": "Qdrant default vector index/config",
        "ingest_seconds": round(ingest_seconds, 4),
        "ingest_records_per_second": round(N / ingest_seconds, 2),
        "index_build_seconds": None,
        "query_latency": latency_summary_ms(latencies),
        "recall_at_k_mean": round(mean_recall, 6),
        "recall_at_k_min": round(min(recalls), 6) if recalls else 0.0,
        "resource_snapshot_before": before,
        "resource_snapshot_after": after,
        "image_digest": image_digest(container),
        "passed": mean_recall >= 0.95,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", choices=["rel", "vec"], required=True)
    parser.add_argument("--candidate", choices=["postgres", "pgvector", "qdrant"], required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    started = time.time()
    try:
        if args.league == "rel":
            result = run_rel(args.candidate)
        elif args.candidate == "pgvector":
            result = run_vec_pgvector()
        elif args.candidate == "qdrant":
            result = run_vec_qdrant()
        else:
            raise ValueError(f"unsupported league/candidate: {args.league}/{args.candidate}")

        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_S",
            "contract_version": "1.0",
            "seed": SEED,
            "started_epoch": started,
            "completed_epoch": time.time(),
            "result": result,
        }
        envelope["evidence_hash"] = sha256_json(envelope)
        Path(args.out).write_text(json.dumps(envelope, indent=2), encoding="utf-8")
        print(json.dumps(envelope, indent=2))
        return 0 if result.get("passed") else 1
    except Exception as exc:
        envelope = {
            "qualification": "BRAIN_STORAGE_BENCH_P1_S",
            "contract_version": "1.0",
            "seed": SEED,
            "started_epoch": started,
            "completed_epoch": time.time(),
            "league": args.league,
            "candidate": args.candidate,
            "status": "FAIL",
            "reason": repr(exc),
            "passed": False,
        }
        envelope["evidence_hash"] = sha256_json(envelope)
        Path(args.out).write_text(json.dumps(envelope, indent=2), encoding="utf-8")
        print(json.dumps(envelope, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
