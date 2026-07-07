from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 



DATABASE_URL = "postgresql+psycopg2://postgres:Anant%407895@localhost:5432/url_shortener" 
print("=" * 60) 
print("STEP 1 : Creating Engine") 
print("=" * 60) 


engine = create_engine(DATABASE_URL) 
SessionLocal = sessionmaker(bind=engine) 


print("Engine Created") 
input("\nPress ENTER to create Session...") 
print("=" * 60) 
print("STEP 2 : Creating SQLAlchemy Session") 
print("=" * 60) 

db = SessionLocal() 

print("Session Created") 
input("\nPress ENTER to exit...")