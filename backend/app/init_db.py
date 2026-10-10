"""Create missing tables for a fresh database; never alter existing tables."""
from . import models  # noqa: F401 - registers mappings with Base
from .database import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete. Existing tables were not altered.")
