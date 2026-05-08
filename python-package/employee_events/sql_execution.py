"""SQLite execution helpers — used by every query class in this package."""
from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd


# Absolute path to the bundled employee_events.db SQLite file.
db_path = Path(__file__).resolve().parent / "employee_events.db"


class QueryMixin:
    """Mixed into QueryBase / Employee / Team to give them DB access."""

    def pandas_query(self, sql_query: str) -> pd.DataFrame:
        with connect(db_path) as conn:
            return pd.read_sql_query(sql_query, conn)

    def query(self, sql_query: str):
        with connect(db_path) as conn:
            cursor = conn.cursor()
            return cursor.execute(sql_query).fetchall()


def query(func):
    """Decorator form — runs the returned SQL and returns list-of-tuples."""
    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result
    return run_query
