"""
Evaluation runner for the AI Customer Support Email Agent.
Usage: python -m evals.evaluator
"""

import json
import sys
import os
import logging
from pathlib import Path

# Ensure project root is on the path when run as a module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.logger import setup_logging
from services.pipeline import process_email

setup_logging()
logger = logging.getLogger(__name__)

TEST_CASES_PATH = Path(__file__).parent / "test_cases.json"


def run_eval(test_cases: list[dict]) -> dict:
    results = []

    for i, case in enumerate(test_cases):
        email_input = case["input"]
        expected_intent = case.get("expected_intent")
        expected_urgency = case.get("expected_urgency")

        logger.info("Running test case %d/%d: %s", i + 1, len(test_cases), case.get("label", ""))

        try:
            response = process_email(email_input)
            intent_correct = response.intent == expected_intent
            urgency_correct = response.urgency == expected_urgency

            results.append({
                "label": case.get("label", f"case_{i+1}"),
                "input": email_input,
                "expected_intent": expected_intent,
                "expected_urgency": expected_urgency,
                "predicted_intent": response.intent,
                "predicted_urgency": response.urgency,
                "confidence": response.confidence,
                "needs_human": response.needs_human,
                "intent_correct": intent_correct,
                "urgency_correct": urgency_correct,
                "exact_match": intent_correct and urgency_correct,
                "error": None,
            })

        except Exception as e:
            logger.error("Test case %d failed with error: %s", i + 1, e)
            results.append({
                "label": case.get("label", f"case_{i+1}"),
                "input": email_input,
                "expected_intent": expected_intent,
                "expected_urgency": expected_urgency,
                "predicted_intent": None,
                "predicted_urgency": None,
                "confidence": None,
                "needs_human": None,
                "intent_correct": False,
                "urgency_correct": False,
                "exact_match": False,
                "error": str(e),
            })

    total = len(results)
    successes = [r for r in results if r["error"] is None]
    n_success = len(successes)

    metrics = {
        "total_cases": total,
        "pipeline_success_rate": round(n_success / total, 3) if total else 0,
        "intent_accuracy": round(sum(r["intent_correct"] for r in successes) / n_success, 3) if n_success else 0,
        "urgency_accuracy": round(sum(r["urgency_correct"] for r in successes) / n_success, 3) if n_success else 0,
        "exact_match_accuracy": round(sum(r["exact_match"] for r in successes) / n_success, 3) if n_success else 0,
        "needs_human_rate": round(sum(1 for r in successes if r["needs_human"]) / n_success, 3) if n_success else 0,
        "avg_confidence": round(sum(r["confidence"] for r in successes) / n_success, 3) if n_success else 0,
    }

    return {"metrics": metrics, "results": results}


def save_results(output: dict):
    results_path = Path(__file__).parent / "results.md"
    metrics = output["metrics"]
    results = output["results"]

    lines = [
        "# Evaluation Results\n",
        f"**Total test cases:** {metrics['total_cases']}  \n",
        f"**Pipeline success rate:** {metrics['pipeline_success_rate'] * 100:.1f}%  \n",
        f"**Intent accuracy:** {metrics['intent_accuracy'] * 100:.1f}%  \n",
        f"**Urgency accuracy:** {metrics['urgency_accuracy'] * 100:.1f}%  \n",
        f"**Exact match (intent + urgency):** {metrics['exact_match_accuracy'] * 100:.1f}%  \n",
        f"**Needs-human rate:** {metrics['needs_human_rate'] * 100:.1f}%  \n",
        f"**Average confidence:** {metrics['avg_confidence']:.2f}  \n\n",
        "## Per-case Results\n\n",
        "| # | Label | Intent ✓ | Urgency ✓ | Exact | Confidence | Error |\n",
        "|---|-------|----------|-----------|-------|------------|-------|\n",
    ]

    for i, r in enumerate(results):
        intent_mark = "✅" if r["intent_correct"] else "❌"
        urgency_mark = "✅" if r["urgency_correct"] else "❌"
        exact_mark = "✅" if r["exact_match"] else "❌"
        conf = f"{r['confidence']:.2f}" if r["confidence"] is not None else "—"
        err = r["error"][:40] if r["error"] else "—"
        lines.append(
            f"| {i+1} | {r['label']} | {intent_mark} | {urgency_mark} | {exact_mark} | {conf} | {err} |\n"
        )

    results_path.write_text("".join(lines), encoding="utf-8")
    logger.info("Results saved to %s", results_path)


if __name__ == "__main__":
    if not TEST_CASES_PATH.exists():
        logger.error("test_cases.json not found at %s", TEST_CASES_PATH)
        sys.exit(1)

    with open(TEST_CASES_PATH, encoding="utf-8") as f:
        test_cases = json.load(f)

    logger.info("Loaded %d test cases", len(test_cases))
    output = run_eval(test_cases)

    metrics = output["metrics"]
    print("\n========== EVALUATION RESULTS ==========")
    print(f"  Total cases:          {metrics['total_cases']}")
    print(f"  Pipeline success:     {metrics['pipeline_success_rate']*100:.1f}%")
    print(f"  Intent accuracy:      {metrics['intent_accuracy']*100:.1f}%")
    print(f"  Urgency accuracy:     {metrics['urgency_accuracy']*100:.1f}%")
    print(f"  Exact match:          {metrics['exact_match_accuracy']*100:.1f}%")
    print(f"  Avg confidence:       {metrics['avg_confidence']:.2f}")
    print(f"  Needs-human rate:     {metrics['needs_human_rate']*100:.1f}%")
    print("=========================================\n")

    save_results(output)
