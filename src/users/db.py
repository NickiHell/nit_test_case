import databases
import sqlalchemy
from sqlalchemy import Column, Integer, String, Table

from users import config

DATABASE_URL = (f"postgresql://{config.USERS_POSTGRES_USER}:"
                f"{config.USERS_POSTGRES_PASSWORD}"
                f"@{config.USERS_POSTGRES_HOST}:"
                f"{config.USERS_POSTGRES_PORT}/"
                f"{config.USERS_POSTGRES_DB}")

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, nullable=False),
    Column('password', String, nullable=False),
    Column('email', String, nullable=False)
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
