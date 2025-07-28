from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import Config

# Create engine
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=Config.SQLALCHEMY_ECHO,
    **Config.SQLALCHEMY_ENGINE_OPTIONS
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Requests(Base):
    __tablename__ = "Requests"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime) 
    source = Column(String(15))

    def __init__(self, timestamp, source):
        self.timestamp = timestamp
        self.source = source

class Tasks(Base):
    __tablename__ = "Tasks"
    id = Column(String, primary_key=True)
    title = Column(String(48))
    description = Column(String(254))
    done = Column(Boolean, default=False)
    updated_at = Column(DateTime) 

    def __init__(self, id, title, description, done, updated_at):
        self.id = id
        self.title = title
        self.description = description
        self.done = done
        self.updated_at = updated_at

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)