
from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener"

print("=" * 60)
print("STEP 1 : Creating Engine")
print("=" * 60)

engine = create_engine(DATABASE_URL)

print("Engine Created")

input("\nPress ENTER to exit...")