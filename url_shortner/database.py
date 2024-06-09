import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()

DEBUG = os.getenv("DEBUG").lower() == 'true'

MYSQL_HOST = os.getenv("MYSQL_HOST") if not DEBUG else "localhost"
MYSQL_USER = os.getenv("MYSQL_ROOT_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")

SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


#############     Redis     #############

REDIS_HOST = os.getenv("REDIS_HOST") if not DEBUG else "localhost"
REDIS_PORT = os.getenv("REDIS_PORT")

REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
