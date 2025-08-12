#database.py

#create_engine creates a connection “engine” to your database.
#Think of it as the database’s doorway — all queries will pass through it.
from sqlalchemy import create_engine #create engine that wraps around databse we are interacting with

#sessionmaker makes “sessions,” which are temporary connections for interacting with the DB (reading, writing, updating data).
#Sessions also track changes until you commit them.
from sqlalchemy.orm import sessionmaker #makes session that we can connect to to interact with our database 

#declarative_base() returns a base class that all your model classes will inherit from.
#This base keeps track of all the models so SQLAlchemy knows what tables to create.
from sqlalchemy.ext.declarative import declarative_base #base class, databases inherit from

#This pulls in your environment-based settings (like DATABASE_URL) from core/config.py.
from core.config import settings

#Creates the actual DB connection engine.
engine = create_engine(
    settings.DATABASE_URL
)

#Pre-configures a session factory bound to your engine.
#autocommit=False → you must explicitly call .commit() to save changes.
#autoflush=False → changes are not automatically flushed to the DB until you commit or flush manually.
#SessionLocal() will give you an independent session object.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Every SQLAlchemy model in your app will inherit from this.
Base = declarative_base()

#give us access to a database session and makes sure we dont 
# have multiple sessions open at one time

#Used with FastAPI dependency injection.
#Provides a fresh DB session to each request, then closes it afterward.
#yield lets FastAPI run your route’s code before the finally block runs.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#create all the tables when app starts up
def create_tables():
    Base.metadata.create_all(bind=engine)
#Scans all models that inherit from Base.
#Automatically creates missing tables in your database when called.
#Typically run once during app startup.



