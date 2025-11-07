import json
from pathlib import Path
from typing import Dict, Any

from .agent.llm import call_llm

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "planner_system.txt"
PLANNER_SYSTEM = PROMPT_PATH.read_text(encoding="utf-8")

def _extract_json(text: str) -> Dict[str, Any]:
    s, e = text.find("{"), text.rfind("}")
    if s != -1 and e != -1:
        return json.loads(text[s:e+1])
    raise ValueError("No JSON found in LLM output")

def _rule_based_fallback(endpoint: Dict[str, Any], max_tests: int = 5) -> Dict[str, Any]:
    method = endpoint.get("method", "GET").upper()
    url = endpoint["url"]
    sample = endpoint.get("sample_request") or {}
    expected = int(endpoint.get("expected_status") or 200)
    tests = [{
        "name": "happy_path",
        "method": method, "url": url, "headers": {},
        "body": sample if method in ("POST","PUT","PATCH") else None,
        "expected_status": expected, "rationale": "Happy path"
    }]
    # missing first field
    if isinstance(sample, dict) and sample and method in ("POST","PUT","PATCH"):
        k = next(iter(sample.keys()))
        bad = dict(sample); bad.pop(k, None)
        tests.append({
            "name": f"missing_{k}", "method": method, "url": url, "headers": {},
            "body": bad, "expected_status": 400, "rationale": f"Missing {k}"
        })
    # invalid email if present
    if isinstance(sample, dict) and "email" in sample and method in ("POST","PUT","PATCH"):
        bad2 = dict(sample); bad2["email"] = "not-an-email"
        tests.append({
            "name": "invalid_email", "method": method, "url": url, "headers": {},
            "body": bad2, "expected_status": 422, "rationale": "Email validation"
        })
    return {"notes": "Rule-based fallback", "tests": tests[:max_tests]}

def plan_tests(endpoint: Dict[str, Any], max_tests: int = 5) -> Dict[str, Any]:
    user_prompt = json.dumps({"endpoint": endpoint, "max_tests": max_tests}, ensure_ascii=False)
    try:
        content = call_llm(PLANNER_SYSTEM, user_prompt)
        return _extract_json(content)
    except Exception:
        return _rule_based_fallback(endpoint, max_tests)
