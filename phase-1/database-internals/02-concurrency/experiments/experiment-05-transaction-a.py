from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

db = Session()

print("=" * 60)
print("Transaction A")
print("=" * 60)

result = db.execute(
    text("""
        SELECT *
        FROM urls
        WHERE id = 1
        FOR UPDATE
    """)
)

print(result.first())

print("\nRow Locked")

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")

input("Press ENTER to exit...")
