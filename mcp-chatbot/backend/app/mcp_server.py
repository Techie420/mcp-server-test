"""
Minimal MCP server exposing tools for orders and NL queries.

Tools:
- list_orders()
- get_order(orderId)
- list_errors()
- nl_query(query)

Run (stdio transport):
  python -m app.mcp_server
"""

from typing import Any, Dict, List

from datetime import datetime

try:
    # Model Context Protocol Python SDK
    from mcp.server import Server
    from mcp.types import TextContent
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "The 'mcp' package is required. Install with: pip install mcp"
    ) from exc

from .db import DB_BACKEND, get_db, get_mongo
from .models import Order
from .langchain_agent import run_nl_query


server = Server("orders-mcp")


def _serialize_sql_order(o: Order) -> Dict[str, Any]:
    return {
        "id": o.id,
        "orderId": o.orderId,
        "status": o.status,
        "errorMessage": o.errorMessage,
        "timestamp": o.timestamp,
    }


def _serialize_mongo_doc(d: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": int(d.get("id", 0)),
        "orderId": d.get("orderId"),
        "status": d.get("status"),
        "errorMessage": d.get("errorMessage"),
        "timestamp": d.get("timestamp"),
    }


@server.tool()
def list_orders() -> List[Dict[str, Any]]:
    if DB_BACKEND == "sql":
        db = next(get_db())
        return [_serialize_sql_order(o) for o in db.query(Order).all()]
    mongo = get_mongo()
    return [_serialize_mongo_doc(d) for d in mongo["orders"].find()]


@server.tool()
def get_order(orderId: str) -> Dict[str, Any]:  # noqa: N803 (param case)
    if DB_BACKEND == "sql":
        db = next(get_db())
        obj = db.query(Order).filter(Order.orderId == orderId).first()
        if not obj:
            return {"error": "Order not found", "orderId": orderId}
        return _serialize_sql_order(obj)
    mongo = get_mongo()
    d = mongo["orders"].find_one({"orderId": orderId})
    if not d:
        return {"error": "Order not found", "orderId": orderId}
    return _serialize_mongo_doc(d)


@server.tool()
def list_errors() -> List[Dict[str, Any]]:
    if DB_BACKEND == "sql":
        db = next(get_db())
        rows = db.query(Order).filter((Order.status == "FAILED") | (Order.errorMessage.isnot(None))).all()
        return [_serialize_sql_order(o) for o in rows]
    mongo = get_mongo()
    return [
        _serialize_mongo_doc(d)
        for d in mongo["orders"].find({"$or": [{"status": "FAILED"}, {"errorMessage": {"$ne": None}}]})
    ]


@server.tool()
def nl_query(query: str) -> Dict[str, Any]:  # noqa: A002 (shadow builtins)
    return run_nl_query(query)


if __name__ == "__main__":
    # Run over stdio for MCP client integration
    server.run()


