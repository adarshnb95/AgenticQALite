import json
from datetime import datetime
from typing import List, Dict, Any

def build_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    failed = total - passed

    summary = {
        "run_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "total_tests": total,
        "passed": passed,
        "failed": failed,
    }

    return {
        "summary": summary,
        "results": results,
    }

def print_summary(report: Dict[str, Any]) -> None:
    summary = report["summary"]
    print("\n=== AgenticQALite Summary ===")
    print(f"Run ID: {summary['run_id']}")
    print(f"Total: {summary['total_tests']}  "
          f"Passed: {summary['passed']}  Failed: {summary['failed']}")
    print("=============================\n")
