from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener" 

print("=" * 60)
print("STEP 1 : Creating Engine")
print("=" * 60)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
input("\nSTEP 1 Complete. Press ENTER...")

print("=" * 60)
print("STEP 2 : Creating Session")
print("=" * 60)
db = SessionLocal()
input("\nSTEP 2 Complete. Press ENTER...")

print("=" * 60)
print("STEP 3 : Executing First SQL")
print("=" * 60)
db.execute(text("SELECT 1"))
input("\nSTEP 3 Complete. Press ENTER...")

print("=" * 60)
print("STEP 4 : Closing Session")
print("=" * 60)
db.close()
input("\nSTEP 4 Complete. Press ENTER to exit...")
