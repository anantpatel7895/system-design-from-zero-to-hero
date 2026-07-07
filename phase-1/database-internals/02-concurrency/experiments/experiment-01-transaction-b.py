from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener" 

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

db = Session()

print("=" * 60)
print("Transaction B")
print("=" * 60)

result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)

count = result.scalar()

print("Current Value:", count)

input("Press ENTER to UPDATE...")

new_value = count + 1

db.execute(
    text("""
        UPDATE urls
        SET click_count = :value
        WHERE id = 1
    """),
    {"value": new_value},
)

print("Updated to:", new_value)

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")

input("Press ENTER to exit...")