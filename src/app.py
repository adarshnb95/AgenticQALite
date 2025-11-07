from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

app = FastAPI(title="Agentic QA Lite")

@app.get("/")
def root():
    return {"message": "Agentic QA Lite API is running"}

# ---------- Request models ----------
class EndpointBody(BaseModel):
    method: str
    url: str
    sample_request: Optional[Dict[str, Any]] = None
    sample_response: Optional[Dict[str, Any]] = None
    auth: Optional[Dict[str, Any]] = None
    expected_status: Optional[int] = None

class RunRequest(BaseModel):
    openapi_url: Optional[str] = None   # not used yet in MVP
    endpoint: Optional[EndpointBody] = None
    max_tests: int = Field(default=5, ge=1, le=10)

# ---------- Route ----------
@app.post("/run_tests")
def run_tests(body: RunRequest):
    if not body.endpoint and not body.openapi_url:
        raise HTTPException(status_code=400, detail="Provide 'endpoint' or 'openapi_url'")

    # Mocked execution summary (we will replace this with planner + runner soon)
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    summary = {
        "run_id": run_id,
        "total_tests": min(body.max_tests, 5),
        "passed": 4,
        "failed": 1,
        "notes": "Mock summary. Planner and executor coming next."
    }
    failures = [{
        "name": "invalid_email",
        "expected_status": 422,
        "status": 200,
        "elapsed_ms": 120
    }]

    return {
        "summary": summary,
        "failures": failures
    }
