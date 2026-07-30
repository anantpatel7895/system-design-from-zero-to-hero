from app.db import SessionLocal
from app.service import ProductService

db = SessionLocal()

print("transaction b")

service = ProductService()

service.atomic_purchase(
    db=db,
    product_id=1,
)

db.close()