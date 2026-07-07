from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener" 

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

print("=" * 60)
print("STEP 1 : Explicit BEGIN")
print("=" * 60)

db.begin()

input("\nSTEP 1 Complete. Press ENTER...")

print("=" * 60)
print("STEP 2 : Execute SELECT")
print("=" * 60)

db.execute(text("SELECT 1"))

input("\nSTEP 2 Complete. Press ENTER...")

print("=" * 60)
print("STEP 3 : COMMIT")
print("=" * 60)

db.commit()

input("\nSTEP 3 Complete. Press ENTER...")

print("=" * 60)
print("STEP 4 : CLOSE SESSION")
print("=" * 60)

db.close()


input("\nSTEP 4 Complete. Press ENTER to exit...")