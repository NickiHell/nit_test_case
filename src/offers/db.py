import databases
import sqlalchemy
from sqlalchemy import Column, Integer, String, Table

from offers import config

DATABASE_URL = (f"postgresql://{config.OFFERS_POSTGRES_USER}:"
                f"{config.OFFERS_POSTGRES_PASSWORD}"
                f"@{config.OFFERS_POSTGRES_HOST}:"
                f"{config.OFFERS_POSTGRES_PORT}/"
                f"{config.OFFERS_POSTGRES_DB}")

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

offers = Table(
    'offers',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, nullable=False),
    Column('title', String, nullable=False),
    Column('text', String, nullable=False)
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
