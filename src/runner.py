# src/runner.py
import time
import requests
from typing import Dict, Any, List, Optional

def run_single_happy_path(method: str, url: str, headers=None, body=None, expected_status: int = 200, timeout: int = 15):
    method = method.upper()
    headers = headers or {}
    start = time.time()
    try:
        if method in ("POST", "PUT", "PATCH"):
            resp = requests.request(method, url, headers=headers, json=body, timeout=timeout)
        else:
            resp = requests.request(method, url, headers=headers, timeout=timeout)
        elapsed_ms = int((time.time() - start) * 1000)
        passed = (resp.status_code == expected_status)
        return {
            "name": "happy_path",
            "status": resp.status_code,
            "expected_status": expected_status,
            "elapsed_ms": elapsed_ms,
            "passed": passed,
            "response_snippet": resp.text[:280] if resp.text else ""
        }
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "name": "happy_path",
            "status": -1,
            "expected_status": expected_status,
            "elapsed_ms": elapsed_ms,
            "passed": False,
            "error": str(e)
        }

def execute_tests(tests: List[Dict[str, Any]], timeout: int = 15) -> Dict[str, Any]:
    """Run a small list of HTTP tests and return aggregated results."""
    results: List[Dict[str, Any]] = []

    for t in tests:
        method = t.get("method", "GET").upper()
        url = t["url"]
        headers = t.get("headers") or {}
        body = t.get("body")
        expected = int(t.get("expected_status", 200))
        name = t.get("name", "test")

        start = time.time()
        try:
            if method in ("POST", "PUT", "PATCH"):
                resp = requests.request(method, url, headers=headers, json=body, timeout=timeout)
            else:
                resp = requests.request(method, url, headers=headers, timeout=timeout)
            elapsed_ms = int((time.time() - start) * 1000)
            passed = (resp.status_code == expected)
            results.append({
                "name": name,
                "status": resp.status_code,
                "expected_status": expected,
                "elapsed_ms": elapsed_ms,
                "passed": passed,
                "response_snippet": resp.text[:280] if resp.text else ""
            })
        except Exception as e:
            elapsed_ms = int((time.time() - start) * 1000)
            results.append({
                "name": name,
                "status": -1,
                "expected_status": expected,
                "elapsed_ms": elapsed_ms,
                "passed": False,
                "error": str(e)
            })

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = total - passed_count
    return {"results": results, "summary": {"total": total, "passed": passed_count, "failed": failed_count}}
