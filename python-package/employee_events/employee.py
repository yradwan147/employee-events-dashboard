"""Employee-level queries against the employee_events database."""
import pandas as pd

from .query_base import QueryBase
from .sql_execution import QueryMixin


class Employee(QueryBase):
    name = "employee"

    def names(self):
        return self.query(
            """
            SELECT first_name || ' ' || last_name AS full_name,
                   employee_id
              FROM employee
            """
        )

    def username(self, id):
        return self.query(
            f"""
            SELECT first_name || ' ' || last_name AS full_name
              FROM employee
             WHERE employee_id = {id}
            """
        )

    def model_data(self, id):
        sql = f"""
            SELECT SUM(positive_events) positive_events,
                   SUM(negative_events) negative_events
              FROM {self.name}
              JOIN employee_events USING({self.name}_id)
             WHERE {self.name}.{self.name}_id = {id}
        """
        return self.pandas_query(sql)
