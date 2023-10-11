from sqlalchemy import create_engine
import os

from sqlalchemy.orm import sessionmaker

from models import Base

env = os.getenv('environment', 'dev')

if env == 'dev':
    # engine = create_engine("sqlite:///foo.db")
    engine = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/postgres")
else:
    db_path = env = os.getenv('db_path')
    engine = create_engine(db_path)

Base.metadata.create_all(engine)

Session = sessionmaker(engine)

