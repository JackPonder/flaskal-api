from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os

engine = create_engine(os.environ.get("DATABASE_URI"), pool_pre_ping=True)
SessionLocal = sessionmaker(engine)
