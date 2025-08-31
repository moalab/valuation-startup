from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import yaml
import math

class CriterionScore(BaseModel):
    id: str
    label: str
    weight: float
    score: float  # 0.0–1.0

class RuleSet(BaseModel):
    id: str
    name: str
    version: str
    elimination_threshold: float = 0.7  # default
    criteria: List[CriterionScore] = []

class ScoreResult(BaseModel):
    total: float
    eliminated: bool
    details: List[CriterionScore]
    reasoning: Dict[str, str] = {}

def load_rules(path: str) -> RuleSet:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    crits = []
    for c in data.get("criteria", []):
        crits.append(CriterionScore(id=c["id"], label=c["label"], weight=float(c["weight"]), score=0.0))
    return RuleSet(
        id=data["id"],
        name=data["name"],
        version=str(data.get("version", "0")),
        elimination_threshold=float(data.get("elimination_threshold", 0.7)),
        criteria=crits
    )

def compute_score(rules: RuleSet, inputs: Dict[str, float], reasoning: Optional[Dict[str, str]] = None) -> ScoreResult:
    total = 0.0
    details = []
    for c in rules.criteria:
        raw = float(inputs.get(c.id, 0.0))
        s = max(0.0, min(1.0, raw))
        details.append(CriterionScore(id=c.id, label=c.label, weight=c.weight, score=s))
        total += s * c.weight
    eliminated = total < rules.elimination_threshold if rules.elimination_threshold > 0 else False
    return ScoreResult(total=total, eliminated=eliminated, details=details, reasoning=reasoning or {})

def what_if(rules: RuleSet, base_inputs: Dict[str, float], deltas: Dict[str, float]) -> ScoreResult:
    new_inputs = dict(base_inputs)
    for k, v in deltas.items():
        new_inputs[k] = max(0.0, min(1.0, new_inputs.get(k, 0.0) + v))
    return compute_score(rules, new_inputs)
