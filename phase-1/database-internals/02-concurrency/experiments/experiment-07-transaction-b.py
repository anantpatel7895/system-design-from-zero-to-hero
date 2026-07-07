from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

db = Session()

print("Transaction B")

db.execute(text("""
    UPDATE urls
    SET click_count = click_count + 1
    WHERE id = 1
"""))

print("Locked Row 1")

input("Press ENTER to lock Row 2...")

db.execute(text("""
    UPDATE urls
    SET click_count = click_count + 1
    WHERE id = 2
"""))

print("Locked Row 2")

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")
