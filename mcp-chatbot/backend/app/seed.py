from datetime import datetime

from .db import DB_BACKEND, get_db, get_mongo
from .models import Order


SAMPLE = [
    {"orderId": "ORD123", "status": "FAILED", "errorMessage": "Payment declined", "timestamp": datetime.fromisoformat("2025-09-14T10:30:00")},
    {"orderId": "ORD124", "status": "SUCCESS", "errorMessage": None, "timestamp": datetime.fromisoformat("2025-09-14T11:00:00")},
    {"orderId": "ORD125", "status": "FAILED", "errorMessage": "Inventory unavailable", "timestamp": datetime.fromisoformat("2025-09-15T08:45:00")},
]


def run():
    if DB_BACKEND == "sql":
        db = next(get_db())
        for i, s in enumerate(SAMPLE, start=1):
            exists = db.query(Order).filter(Order.orderId == s["orderId"]).first()
            if exists:
                continue
            obj = Order(orderId=s["orderId"], status=s["status"], errorMessage=s["errorMessage"], timestamp=s["timestamp"]) 
            db.add(obj)
        db.commit()
        print("Seeded SQL orders")
    else:
        mongo = get_mongo()
        for i, s in enumerate(SAMPLE, start=1):
            if mongo["orders"].find_one({"orderId": s["orderId"]}):
                continue
            doc = {"id": i, **s}
            mongo["orders"].insert_one(doc)
        print("Seeded Mongo orders")


if __name__ == "__main__":
    run()


