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
        SELECT *
        FROM urls
        WHERE id = 1
        FOR UPDATE
    """)
)

print(result.first())

db.commit()

print("Committed")
