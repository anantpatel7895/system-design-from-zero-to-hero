from app.db import SessionLocal
from app.service import ProductService

db = SessionLocal()

service = ProductService()

service.purchase(
    db=db,
    product_id=1,
)

db.close()