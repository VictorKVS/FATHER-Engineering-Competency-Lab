import json, sqlite3, time, uuid
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS models(
  brain_id TEXT PRIMARY KEY,
  provider TEXT NOT NULL,
  model_name TEXT NOT NULL,
  adapter TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'registered',
  capabilities_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS benchmark_runs(
  run_id TEXT PRIMARY KEY,
  brain_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  competency_id TEXT,
  task_id TEXT NOT NULL,
  task_type TEXT NOT NULL,
  ok INTEGER NOT NULL,
  elapsed_ms INTEGER,
  prompt_eval_count INTEGER,
  eval_count INTEGER,
  response_chars INTEGER,
  knowledge_hits INTEGER,
  quality_score REAL,
  quality_passed INTEGER,
  scorer TEXT,
  scoring_details_json TEXT,
  error TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bench_task ON benchmark_runs(task_type, task_id);
CREATE INDEX IF NOT EXISTS idx_bench_brain ON benchmark_runs(brain_id);
"""

class ModelZooDB:
    def __init__(self,path):
        self.path=str(path)
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.path)
        self.db.row_factory=sqlite3.Row
        self.db.executescript(SCHEMA)
        self._migrate()
        self.db.commit()

    def _columns(self,table):
        return {r[1] for r in self.db.execute(f"PRAGMA table_info({table})").fetchall()}

    def _migrate(self):
        cols=self._columns("benchmark_runs")
        additions={
            "quality_score":"REAL",
            "quality_passed":"INTEGER",
            "scorer":"TEXT",
            "scoring_details_json":"TEXT"
        }
        for name,typ in additions.items():
            if name not in cols:
                self.db.execute(f"ALTER TABLE benchmark_runs ADD COLUMN {name} {typ}")

    def register_models(self,brains_cfg):
        now=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
        for brain_id,c in brains_cfg.items():
            self.db.execute("""
              INSERT INTO models(brain_id,provider,model_name,adapter,status,capabilities_json,created_at,updated_at)
              VALUES(?,?,?,?,?,?,?,?)
              ON CONFLICT(brain_id) DO UPDATE SET model_name=excluded.model_name,updated_at=excluded.updated_at
            """,(brain_id,"ollama",c["model"],c["adapter"],"registered",
                 json.dumps({"chat":True,"text":True}),now,now))
        self.db.commit()

    def record_run(self,brain_id,agent_id,competency_id,task_id,task_type,result,elapsed_ms,quality):
        m=result.metadata; metrics=m.get("metrics") or {}
        self.db.execute("""
          INSERT INTO benchmark_runs(
            run_id,brain_id,agent_id,competency_id,task_id,task_type,ok,elapsed_ms,
            prompt_eval_count,eval_count,response_chars,knowledge_hits,
            quality_score,quality_passed,scorer,scoring_details_json,error,created_at
          ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(str(uuid.uuid4()),brain_id,agent_id,competency_id,task_id,task_type,
             1 if result.ok else 0,elapsed_ms,metrics.get("prompt_eval_count"),
             metrics.get("eval_count"),len(result.content or ""),m.get("knowledge_hits",0),
             quality["score"],1 if quality["passed"] else 0,quality["scorer"],
             json.dumps(quality["details"],ensure_ascii=False),m.get("error"),
             time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())))
        self.db.commit()

    def ranking(self,task_type):
        rows=self.db.execute("""
          SELECT brain_id,
                 COUNT(*) runs,
                 ROUND(AVG(quality_score),2) avg_quality_score,
                 ROUND(100.0*SUM(quality_passed)/COUNT(*),2) quality_pass_pct,
                 ROUND(100.0*SUM(ok)/COUNT(*),2) technical_success_pct,
                 ROUND(AVG(elapsed_ms),1) avg_elapsed_ms
          FROM benchmark_runs
          WHERE task_type=? AND quality_score IS NOT NULL
          GROUP BY brain_id
          ORDER BY avg_quality_score DESC, quality_pass_pct DESC, avg_elapsed_ms ASC
        """,(task_type,)).fetchall()
        return [dict(r) for r in rows]
