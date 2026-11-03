import json
from pathlib import Path

class ModelApplicabilityEngine:
    def __init__(self,path):
        self.path=Path(path)
        self.data=json.loads(self.path.read_text(encoding="utf-8"))
        self.models=self.data["models"]

    def classify(self,task):
        text=str(task.get("text","")).lower()
        modality=task.get("modality","text")
        explicit=task.get("specialization")
        complexity=int(task.get("complexity",2))

        if explicit:
            specialization=explicit
        elif any(x in text for x in ["код","python","ошибк","рефактор","функц","класс","api"]):
            specialization="coding"
        elif any(x in text for x in ["изображ","картин","скрин","фото","диаграм","chart"]):
            specialization="vision"
            modality="vision"
        elif any(x in text for x in ["рассуж","почему","план","сценар","доказ","сравни варианты","критич"]):
            specialization="reasoning"
        elif any(x in text for x in ["rag","база знаний","knowledge","источник","документ"]):
            specialization="rag"
        else:
            specialization="general"

        return {
            "modality":modality,
            "specialization":specialization,
            "complexity":max(1,min(4,complexity))
        }

    def rank(self,task,registered_only=True):
        profile=self.classify(task)
        rows=[]
        for model_id,m in self.models.items():
            if registered_only and not m.get("registered"):
                continue
            if not m.get("installed"):
                continue

            score=0
            reasons=[]
            penalties=[]

            if profile["modality"] in m.get("modality",[]):
                score+=30
                reasons.append("modality_match")
            else:
                continue

            strengths=set(m.get("strengths",[]))
            spec=profile["specialization"]
            aliases={
                "general":{"general analysis","multilingual","structured_output"},
                "rag":{"rag","retrieval-support"},
                "coding":{"coding","code_generation","code_reasoning","devsecops"},
                "reasoning":{"reasoning","multi_step_analysis","planning","critical_analysis"},
                "vision":{"vision","document_understanding","image_analysis"}
            }
            if strengths & aliases.get(spec,{spec}):
                score+=40
                reasons.append("specialization_match")
            else:
                penalties.append("weak_specialization_match")

            if profile["complexity"] in m.get("recommended_complexity",[]):
                score+=20
                reasons.append("complexity_in_range")
            else:
                distance=min(abs(profile["complexity"]-x) for x in m.get("recommended_complexity",[2]))
                score-=10*distance
                penalties.append("complexity_distance_"+str(distance))

            latency=m.get("latency_class")
            if complexity_is_low(profile["complexity"]) and latency=="fast":
                score+=10
                reasons.append("fast_for_simple_task")
            if profile["complexity"]>=4 and "reasoning" in strengths:
                score+=15
                reasons.append("deep_reasoning_bonus")

            local=m.get("local_evidence",{})
            if local.get("stage24_pass_rate")==1.0:
                score+=5
                reasons.append("local_pass_evidence")
            if local.get("stage24_rank")==1:
                score+=3
                reasons.append("local_rank_1")

            rows.append({
                "model_id":model_id,
                "brain_id":m.get("brain_id"),
                "runtime_model":m.get("runtime_model"),
                "score":score,
                "reasons":reasons,
                "penalties":penalties,
                "profile":profile,
                "strengths":m.get("strengths",[]),
                "recommended_complexity":m.get("recommended_complexity",[]),
                "local_evidence":local
            })

        rows.sort(key=lambda x:(-x["score"],x["runtime_model"]))
        for i,row in enumerate(rows,1):
            row["rank"]=i
        return rows

    def choose(self,task,registered_only=True):
        ranking=self.rank(task,registered_only=registered_only)
        return {
            "task_profile":self.classify(task),
            "selected":ranking[0] if ranking else None,
            "ranking":ranking
        }

def complexity_is_low(level):
    return int(level)<=2
