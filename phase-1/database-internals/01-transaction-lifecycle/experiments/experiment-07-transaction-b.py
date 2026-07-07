from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener" 

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

Session = sessionmaker(bind=engine)

db = Session()

input("Run AFTER Transaction A executes UPDATE.\nPress ENTER...")

result = db.execute(
    text("""
        SELECT click_count
        FROM urls
        WHERE id = 1
    """)
)

print()

print("Click Count =", result.scalar())

input("Press ENTER to exit...")