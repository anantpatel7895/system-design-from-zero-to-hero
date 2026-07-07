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
print("STEP 1 : Read Current Value")
print("=" * 60)

result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)

print(result.scalar())

input("\nPress ENTER to UPDATE...")

print("=" * 60)
print("STEP 2 : UPDATE")
print("=" * 60)

db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 1
    """)
)

input("\nPress ENTER to CLOSE SESSION...")

print("=" * 60)
print("STEP 3 : CLOSE SESSION")
print("=" * 60)

db.close()

print("Session Closed")

input("\nPress ENTER to exit...")