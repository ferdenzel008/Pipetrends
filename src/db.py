from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from config import DATABASE_URL
import logging
from datetime import datetime

logger = logging.getLogger("db")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s %(message)s]",
    datefmt="%Y-%m-%d %H:%M:%S")

_engine = None
# Create SQLAlchemy engine (used to connect to the postgresdb)
def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, echo=False, future=True)
    return _engine
#create the tables
def create_tables():
    engine = get_engine()
    with engine.begin() as conn, open("src/models.sql") as f:
        sql = f.read()
        conn.execute(text(sql))
    logging.info("Tables created/verified.")