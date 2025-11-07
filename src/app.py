from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from .runner import execute_tests
from .planner import plan_tests




app = FastAPI(title="Agentic QA Lite")

@app.get("/")
def root():
    return {"message": "Agentic QA Lite API is running"}

class EndpointBody(BaseModel):
    method: str
    url: str
    sample_request: Optional[Dict[str, Any]] = None
    sample_response: Optional[Dict[str, Any]] = None
    auth: Dict[str, Any] = Field(default_factory=dict)
    expected_status: Optional[int] = 200

class RunRequest(BaseModel):
    openapi_url: Optional[str] = None
    endpoint: Optional[EndpointBody] = None
    max_tests: int = Field(default=5, ge=1, le=10)

@app.post("/run_tests")
def run_tests(body: RunRequest):
    if not body.endpoint and not body.openapi_url:
        raise HTTPException(status_code=400, detail="Provide 'endpoint' or 'openapi_url'")
    if not body.endpoint:
        raise HTTPException(status_code=501, detail="OpenAPI ingestion not implemented yet")

    ep = body.endpoint.model_dump()

    # Minimal auth header support (null-safe)
    headers = {}
    auth_cfg = (ep.get("auth") or {})  # <- handles None
    if isinstance(auth_cfg, dict) and auth_cfg.get("type") == "bearer" and auth_cfg.get("token"):
        headers["Authorization"] = f"Bearer {auth_cfg['token']}"

    # Ask the agent to plan tests (JSON)
    plan = plan_tests(ep, max_tests=body.max_tests)

    # Ensure method/url/headers are set on each test if missing
    for t in plan.get("tests", []):
        t.setdefault("method", ep["method"])
        t.setdefault("url", ep["url"])
        t.setdefault("headers", headers.copy())

    exec_out = execute_tests(plan.get("tests", []))

    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    return {
        "summary": {
            "run_id": run_id,
            "total_tests": exec_out["summary"]["total"],
            "passed": exec_out["summary"]["passed"],
            "failed": exec_out["summary"]["failed"],
            "notes": plan.get("notes", "planned by agent")
        },
        "results": exec_out["results"],
        "failures": [r for r in exec_out["results"] if not r["passed"]]
    }
