from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener" 

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

Session = sessionmaker(bind=engine)

db = Session()

print("STEP 1 : UPDATE")

db.execute(
    text("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE id = 1
    """)
)

print("UPDATE Executed")

input("Press ENTER to COMMIT...")

db.commit()

print("Committed")

input("Press ENTER to exit...")