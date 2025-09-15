from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth.jwt import get_current_user
from ..db import DB_BACKEND, get_db, get_mongo
from ..models import Order


router = APIRouter(prefix="/orders", tags=["orders"]) 


class OrderOut(BaseModel):
    id: int
    orderId: str
    status: str
    errorMessage: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[OrderOut])
def list_orders(current_user: str = Depends(get_current_user), db=Depends(get_db)):
    if DB_BACKEND == "sql":
        return db.query(Order).all()
    else:
        mongo = get_mongo()
        docs = list(mongo["orders"].find())
        # Normalize Mongo docs to OrderOut-like dicts
        results = []
        for d in docs:
            results.append({
                "id": int(d.get("id", 0)),
                "orderId": d.get("orderId"),
                "status": d.get("status"),
                "errorMessage": d.get("errorMessage"),
                "timestamp": d.get("timestamp"),
            })
        return results


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, current_user: str = Depends(get_current_user), db=Depends(get_db)):
    if DB_BACKEND == "sql":
        obj = db.query(Order).filter(Order.orderId == order_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Order not found")
        return obj
    else:
        mongo = get_mongo()
        d = mongo["orders"].find_one({"orderId": order_id})
        if not d:
            raise HTTPException(status_code=404, detail="Order not found")
        return {
            "id": int(d.get("id", 0)),
            "orderId": d.get("orderId"),
            "status": d.get("status"),
            "errorMessage": d.get("errorMessage"),
            "timestamp": d.get("timestamp"),
        }


@router.get("/errors", response_model=List[OrderOut])
def list_errors(current_user: str = Depends(get_current_user), db=Depends(get_db)):
    if DB_BACKEND == "sql":
        return db.query(Order).filter((Order.status == "FAILED") | (Order.errorMessage.isnot(None))).all()
    else:
        mongo = get_mongo()
        docs = list(mongo["orders"].find({"$or": [{"status": "FAILED"}, {"errorMessage": {"$ne": None}}]}))
        results = []
        for d in docs:
            results.append({
                "id": int(d.get("id", 0)),
                "orderId": d.get("orderId"),
                "status": d.get("status"),
                "errorMessage": d.get("errorMessage"),
                "timestamp": d.get("timestamp"),
            })
        return results


