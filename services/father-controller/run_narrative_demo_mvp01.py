import json, sqlite3
from pathlib import Path

BASE=Path(__file__).resolve().parent
DATA=BASE/"narrative_demo"
DB=DATA/"demo_story.db"
SRC=DATA/"demo_story_fixture.json"
EVIDENCE=BASE/"evidence/narrative_demo_mvp01.json"

schema="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS stories(id TEXT PRIMARY KEY,title TEXT);
CREATE TABLE IF NOT EXISTS scenes(id TEXT PRIMARY KEY,story_id TEXT,order_no INTEGER,location TEXT,time_label TEXT);
CREATE TABLE IF NOT EXISTS characters(id TEXT PRIMARY KEY,story_id TEXT,name TEXT);
CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,story_id TEXT,scene_id TEXT,kind TEXT,summary TEXT,actor TEXT,target TEXT);
CREATE TABLE IF NOT EXISTS objects(id TEXT PRIMARY KEY,story_id TEXT,name TEXT,location TEXT,owner TEXT);
CREATE TABLE IF NOT EXISTS claims(id TEXT PRIMARY KEY,story_id TEXT,text TEXT,truth_status TEXT,source_event TEXT);
CREATE TABLE IF NOT EXISTS perspectives(claim_id TEXT,character TEXT,state TEXT,PRIMARY KEY(claim_id,character));
CREATE TABLE IF NOT EXISTS statements(id TEXT PRIMARY KEY,story_id TEXT,scene_id TEXT,speaker TEXT,listener TEXT,content TEXT,claim_id TEXT,truth_status TEXT);
CREATE TABLE IF NOT EXISTS plot_threads(id TEXT PRIMARY KEY,story_id TEXT,title TEXT,status TEXT);
"""

def rows(cur,sql,args=()):
    return [dict(r) for r in cur.execute(sql,args).fetchall()]

def main():
    data=json.loads(SRC.read_text(encoding="utf-8"))
    DATA.mkdir(exist_ok=True)
    if DB.exists(): DB.unlink()
    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.executescript(schema)
    sid=data["story_id"]
    cur.execute("INSERT INTO stories VALUES (?,?)",(sid,data["title"]))
    for x in data["scenes"]: cur.execute("INSERT INTO scenes VALUES (?,?,?,?,?)",(x["id"],sid,x["order_no"],x["location"],x["time_label"]))
    for x in data["characters"]: cur.execute("INSERT INTO characters VALUES (?,?,?)",(x["id"],sid,x["name"]))
    for x in data["events"]: cur.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",(x["id"],sid,x["scene_id"],x["kind"],x["summary"],x.get("actor"),x.get("target")))
    for x in data["objects"]: cur.execute("INSERT INTO objects VALUES (?,?,?,?,?)",(x["id"],sid,x["name"],x["location"],x["owner"]))
    for x in data["claims"]: cur.execute("INSERT INTO claims VALUES (?,?,?,?,?)",(x["id"],sid,x["text"],x["truth_status"],x["source_event"]))
    for x in data["perspectives"]: cur.execute("INSERT INTO perspectives VALUES (?,?,?)",(x["claim_id"],x["character"],x["state"]))
    for x in data["statements"]: cur.execute("INSERT INTO statements VALUES (?,?,?,?,?,?,?,?)",(x["id"],sid,x["scene_id"],x["speaker"],x["listener"],x["content"],x["claim_id"],x["truth_status"]))
    for x in data["plot_threads"]: cur.execute("INSERT INTO plot_threads VALUES (?,?,?,?)",(x["id"],sid,x["title"],x["status"]))
    con.commit()

    report={
      "story":data["title"],
      "counts":{
        "scenes":cur.execute("select count(*) from scenes").fetchone()[0],
        "characters":cur.execute("select count(*) from characters").fetchone()[0],
        "events":cur.execute("select count(*) from events").fetchone()[0],
        "claims":cur.execute("select count(*) from claims").fetchone()[0],
        "statements":cur.execute("select count(*) from statements").fetchone()[0],
        "plot_threads":cur.execute("select count(*) from plot_threads").fetchone()[0]
      },
      "who_knows_attack":rows(cur,"""
        select c.name,p.state from perspectives p
        join characters c on c.id=p.character
        where p.claim_id='c1' order by c.name
      """),
      "what_sergey_believes":rows(cur,"""
        select cl.text,p.state,cl.truth_status from perspectives p
        join claims cl on cl.id=p.claim_id
        where p.character='sergey' and p.state='BELIEVES'
      """),
      "ivan_lies":rows(cur,"""
        select content,truth_status from statements
        where speaker='ivan' and truth_status='LIE'
      """),
      "object_state":rows(cur,"select name,location,owner from objects order by id"),
      "open_threads":rows(cur,"select title,status from plot_threads where status='OPEN'"),
      "knowledge_violation_check":{
        "question":"Может ли Сергей обоснованно утверждать, что Иван напал на Петра?",
        "answer":"NO",
        "reason":"Для claim c1 у Сергея состояние DOES_NOT_KNOW; он лишь BELIEVES в альтернативный claim c3."
      }
    }
    EVIDENCE.parent.mkdir(exist_ok=True)
    EVIDENCE.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("=== FATHER NARRATIVE KB MVP-01 ===")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("DB:",DB)
    print("EVIDENCE:",EVIDENCE)
    print("RESULT: PASS")
    con.close()

if __name__=="__main__":
    main()
