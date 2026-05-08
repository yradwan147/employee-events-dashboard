"""Base class for the employee_events sql query classes."""
import pandas as pd

from .sql_execution import QueryMixin


class QueryBase(QueryMixin):
    """Default behaviour shared by both Employee and Team subclasses."""

    name = ""

    def names(self):
        # Each subclass should override this.
        return []

    def event_counts(self, id):
        """Sum positive and negative events grouped by date."""
        sql = f"""
            SELECT  event_date,
                    SUM(positive_events) AS positive_events,
                    SUM(negative_events) AS negative_events
              FROM  {self.name}
              JOIN  employee_events
              USING ({self.name}_id)
             WHERE  {self.name}.{self.name}_id = {id}
             GROUP BY event_date
             ORDER BY event_date
        """
        return self.pandas_query(sql)

    def notes(self, id):
        """Return notes for the given Employee/Team id."""
        sql = f"""
            SELECT  note_date, note
              FROM  notes
              JOIN  {self.name}
              USING ({self.name}_id)
             WHERE  {self.name}.{self.name}_id = {id}
             ORDER BY note_date
        """
        return self.pandas_query(sql)
