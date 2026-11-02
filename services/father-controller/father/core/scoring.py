import re

def _norm(s):
    return " ".join(str(s or "").lower().replace("ё","е").split())

def score_response(text, rubric):
    t=_norm(text)
    score=0.0
    details={"required_groups":[],"forbidden":[],"length":{}}

    groups=rubric.get("required_groups",[])
    required_weight=float(rubric.get("required_weight",0.70))
    if groups:
        hits=0
        for group in groups:
            ok=any(_norm(term) in t for term in group)
            details["required_groups"].append({"group":group,"passed":ok})
            hits += 1 if ok else 0
        score += required_weight*(hits/len(groups))
    else:
        score += required_weight

    forbidden=rubric.get("forbidden_terms",[])
    forbidden_weight=float(rubric.get("forbidden_weight",0.20))
    bad=[x for x in forbidden if _norm(x) in t]
    details["forbidden"]=bad
    if not bad:
        score += forbidden_weight

    min_chars=int(rubric.get("min_chars",1))
    max_chars=int(rubric.get("max_chars",10000))
    length_weight=float(rubric.get("length_weight",0.10))
    length_ok=min_chars <= len(text or "") <= max_chars
    details["length"]={"chars":len(text or ""),"min":min_chars,"max":max_chars,"passed":length_ok}
    if length_ok:
        score += length_weight

    score=round(max(0.0,min(1.0,score))*100,2)
    return {"score":score,"passed":score>=float(rubric.get("pass_score",75)),
            "details":details,"scorer":"deterministic-rubric-v1"}
