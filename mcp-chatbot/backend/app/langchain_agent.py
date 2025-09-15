import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

try:
    from langchain_openai import ChatOpenAI  # noqa: F401
except Exception:
    ChatOpenAI =  None # type: ignore

from .db import DB_BACKEND, get_db, get_mongo
from .models import Order


def _heuristic_query(text: str):
    """Very simple fallback to parse common phrases: today, yesterday, failed, pending."""
    now = datetime.utcnow()
    start_today = datetime(now.year, now.month, now.day)
    start_yesterday = start_today - timedelta(days=1)
    end_yesterday = start_today

    status = None
    start = None

    lower = text.lower()
    if "failed" in lower:
        status = "FAILED"
    elif "success" in lower:
        status = "SUCCESS"
    elif "pending" in lower:
        status = "PENDING"

    if "today" in lower:
        start = start_today
    elif "yesterday" in lower:
        start = start_yesterday

    return status, start


def run_nl_query(natural_text: str) -> Dict[str, Any]:
    """Use LLM to derive intent; if not available, fallback to heuristic. Return rows."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")

    # Fallback first to heuristic for robustness
    status, start = _heuristic_query(natural_text)

    rows: List[Dict[str, Any]] = []
    if DB_BACKEND == "sql":
        db = next(get_db())
        query = db.query(Order)
        if status:
            query = query.filter(Order.status == status)
        if start:
            query = query.filter(Order.timestamp >= start)
        results = query.all()
        for r in results:
            rows.append({
                "id": r.id,
                "orderId": r.orderId,
                "status": r.status,
                "errorMessage": r.errorMessage,
                "timestamp": r.timestamp,
            })
    else:
        mongo = get_mongo()
        cond: Dict[str, Any] = {}
        if status:
            cond["status"] = status
        if start:
            cond["timestamp"] = {"$gte": start}
        docs = list(mongo["orders"].find(cond))
        for d in docs:
            rows.append({
                "id": int(d.get("id", 0)),
                "orderId": d.get("orderId"),
                "status": d.get("status"),
                "errorMessage": d.get("errorMessage"),
                "timestamp": d.get("timestamp"),
            })

    return {
        "explanation": f"Heuristic filter: status={status}, start={start}",
        "rows": rows,
    }


