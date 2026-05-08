# Data Science Dashboard — Employee Events

Final project for Udacity's *Data Scientist Nanodegree* dashboard project
(nd025). A FastHTML + SQLite dashboard that lets a manager pick an
individual employee or a whole team and see:

* a time-series of positive vs negative events,
* the most recent feedback notes,
* a model prediction of the employee/team's expected future events.

## Repo layout

```
python-package/employee_events/      Reusable Python package with the SQLite
├── __init__.py
├── employee.py            Employee subclass — names, username, model_data
├── team.py                Team subclass     — names, username, model_data
├── query_base.py          QueryBase class — event_counts, notes
├── sql_execution.py       db_path + QueryMixin (pandas_query, query)
└── employee_events.db     sqlite3 file with employees / teams / events / notes

report/
├── dashboard.py            FastHTML app entrypoint
├── utils.py
├── base_components/        DataTable, Dropdown, Radio, MatplotlibViz, BaseComponent
└── combined_components/    FormGroup, CombinedComponent

assets/                    model.pkl + report.css
tests/                     pytest suite for the SQL package
```

## Running

```bash
pip install -r requirements.txt
pip install -e python-package/

# Tests for the SQL package
pytest -q tests/

# Dashboard
python report/dashboard.py
# Open the printed URL in a browser.
```

## What I implemented

* `sql_execution.py` — the absolute path to the SQLite file via `pathlib`,
  a context-managed `pandas_query` and a `query` method on `QueryMixin`,
  and a `query` decorator for legacy call sites.
* `query_base.py` — `QueryBase` class with shared `event_counts(id)` and
  `notes(id)` methods that f-string the `name` class attribute into the
  table joins so a subclass can re-use them just by setting `name`.
* `employee.py` — `Employee(QueryBase)` with `name = "employee"`, `names`
  returning full-name + id tuples, `username(id)` for one employee, and
  `model_data(id)` for the prediction page.
* `team.py` — `Team(QueryBase)` with `name = "team"`, an analogous
  `names`, `username`, and a `model_data(id)` that aggregates per-employee.

## Standing-out work

* `pandas_query` and `query` both wrap their connections in a `with`
  block so the SQLite file handle closes even on exception.
* The `model_data` query for `Team` aggregates per employee_id first so
  the dashboard's prediction is the right shape for the trained
  classifier.
* `QueryBase.event_counts` orders by `event_date` so the line chart in
  the dashboard never shows the dates out of order.

## License

Educational submission for Udacity nd025.
