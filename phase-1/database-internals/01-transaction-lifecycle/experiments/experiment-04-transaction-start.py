from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener" 

engine = create_engine(
    DATABASE_URL,
    echo=True,
)
SessionLocal = sessionmaker(bind=engine)

print("=" * 60)
print("STEP 1 : Create Session")
print("=" * 60)
db = SessionLocal()
input("\nSTEP 1 Complete. Press ENTER...")

print("=" * 60)
print("STEP 2 : Execute SELECT")
print("=" * 60)
db.execute(text("SELECT 1"))
input("\nSTEP 2 Complete. Press ENTER...")

print("=" * 60)
print("STEP 3 : Commit")
print("=" * 60)
db.commit()
input("\nSTEP 3 Complete. Press ENTER...")

print("=" * 60)
print("STEP 4 : Close Session")
print("=" * 60)
db.close()
input("\nSTEP 4 Complete. Press ENTER to exit...")
