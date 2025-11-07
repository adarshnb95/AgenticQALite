# src/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from .runner import execute_tests

app = FastAPI(title="Agentic QA Lite")

@app.get("/")
def root():
    return {"message": "Agentic QA Lite API is running"}

class EndpointBody(BaseModel):
    method: str
    url: str
    sample_request: Optional[Dict[str, Any]] = None
    sample_response: Optional[Dict[str, Any]] = None
    auth: Optional[Dict[str, Any]] = None
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

    ep = body.endpoint

    # simple auth header
    headers = {}
    if ep.auth and ep.auth.get("type") == "bearer" and ep.auth.get("token"):
        headers["Authorization"] = f"Bearer {ep.auth['token']}"

    # Happy path
    tests = [{
        "name": "happy_path",
        "method": ep.method,
        "url": ep.url,
        "headers": headers,
        "body": ep.sample_request if ep.method.upper() in ("POST","PUT","PATCH") else None,
        "expected_status": ep.expected_status or 200
    }]

    # Edge case: missing the first field (only for JSON body)
    if ep.sample_request and isinstance(ep.sample_request, dict) and ep.method.upper() in ("POST","PUT","PATCH"):
        first_key = next(iter(ep.sample_request.keys()))
        bad_body = dict(ep.sample_request)
        bad_body.pop(first_key, None)
        tests.append({
            "name": f"missing_{first_key}",
            "method": ep.method,
            "url": ep.url,
            "headers": headers,
            "body": bad_body,
            "expected_status": 400  # common choice; adjust if your API uses 422
        })

    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    exec_out = execute_tests(tests)

    return {
        "summary": {
            "run_id": run_id,
            "total_tests": exec_out["summary"]["total"],
            "passed": exec_out["summary"]["passed"],
            "failed": exec_out["summary"]["failed"],
            "notes": "Happy path + one edge case"
        },
        "results": exec_out["results"],
        "failures": [r for r in exec_out["results"] if not r["passed"]]
    }
