"""Dashboard report — fasthtml app that renders an Employee/Team
recruitment-risk page with a cumulative-events line chart, a predicted
risk bar, and a recent-notes table."""
from fasthtml.common import *
import matplotlib.pyplot as plt
import pandas as pd

from employee_events import QueryBase, Employee, Team

from utils import load_model

from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable,
)
from combined_components import FormGroup, CombinedComponent


# ---------------------------------------------------------------------------
# Dropdown — Employee/Team selector at the top of the dashboard
# ---------------------------------------------------------------------------
class ReportDropdown(Dropdown):
    """Dropdown that knows it's listing entities of `model`'s type."""

    def build_component(self, entity_id, model):
        # Use the human-readable model name as the dropdown label.
        self.label = model.name
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        # Employee.names() / Team.names() return [(name, id), ...].
        return model.names()


# ---------------------------------------------------------------------------
# Header — H1 with the entity type currently being reported on
# ---------------------------------------------------------------------------
class Header(BaseComponent):
    """A simple H1 banner showing which entity type the page is for."""

    def build_component(self, entity_id, model):
        return H1(model.name)


# ---------------------------------------------------------------------------
# LineChart — cumulative positive/negative events over time
# ---------------------------------------------------------------------------
class LineChart(MatplotlibViz):
    """Cumulative positive/negative events plotted against day."""

    def visualization(self, asset_id, model):
        # Pull (event_date, positive_events, negative_events) from the DB.
        df = model.event_counts(asset_id)

        # Replace NaN with 0 so cumsum doesn't propagate gaps.
        df = df.fillna(0)

        # Use the date column as the index and sort it chronologically.
        df = df.set_index("event_date")
        df = df.sort_index()

        # Convert raw daily counts into a running total.
        df = df.cumsum()

        # Match the rubric's expected column names.
        df.columns = ["Positive", "Negative"]

        # Render onto a fresh axis (matplotlib2fasthtml decorator already
        # opened a new figure for us).
        fig, ax = plt.subplots()
        df.plot(ax=ax)

        # Apply the standard MatplotlibViz styling — black border / black
        # text so the chart contrasts against the white dashboard card.
        self.set_axis_styling(ax, bordercolor="black", fontcolor="black")

        # Title + axis labels.
        ax.set_title("Cumulative Employee Events")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Event Count")


# ---------------------------------------------------------------------------
# BarChart — single-bar visualisation of the predicted recruitment risk
# ---------------------------------------------------------------------------
class BarChart(MatplotlibViz):
    """Single horizontal bar showing the model's risk prediction."""

    # Load the trained sklearn estimator once at import time.
    predictor = load_model()

    def visualization(self, asset_id, model):
        # Pull the (positive_events, negative_events) feature row(s) for this
        # asset_id; for Employee it's a single row, for Team it's one row
        # per employee on the team.
        data = model.model_data(asset_id)

        # predict_proba returns shape (n_records, n_classes); take the
        # positive class (index 1) which is the recruitment-risk prob.
        proba = self.predictor.predict_proba(data)
        proba_positive = proba[:, 1]

        # For the Team page, the headline number is the *mean* per-employee
        # risk; for the Employee page, the single record IS the prediction.
        if model.name == "team":
            pred = proba_positive.mean()
        else:
            pred = proba_positive[0]

        # Build the single-bar plot and apply the standard styling.
        fig, ax = plt.subplots()
        ax.barh([""], [pred])
        ax.set_xlim(0, 1)
        ax.set_title("Predicted Recruitment Risk", fontsize=20)

        self.set_axis_styling(ax, bordercolor="black", fontcolor="black")


# ---------------------------------------------------------------------------
# Visualizations — line chart + bar chart side-by-side in a grid
# ---------------------------------------------------------------------------
class Visualizations(CombinedComponent):
    """Two-card grid of (LineChart, BarChart)."""

    children = [LineChart(), BarChart()]
    outer_div_type = Div(cls="grid")


# ---------------------------------------------------------------------------
# NotesTable — recent notes for this employee/team at the bottom of the page
# ---------------------------------------------------------------------------
class NotesTable(DataTable):
    """A DataTable wired up to the Employee/Team .notes() query."""

    def component_data(self, entity_id, model):
        return model.notes(entity_id)


# ---------------------------------------------------------------------------
# Dashboard filters — radio + dropdown form at the top
# ---------------------------------------------------------------------------
class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name="profile_type",
            hx_get="/update_dropdown",
            hx_target="#selector",
        ),
        ReportDropdown(
            id="selector",
            name="user-selection",
        ),
    ]


# ---------------------------------------------------------------------------
# Report — header, filters, visualisations, notes
# ---------------------------------------------------------------------------
class Report(CombinedComponent):
    """Top-level dashboard report — assembles every page section."""

    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]


# ---------------------------------------------------------------------------
# fasthtml app + routes
# ---------------------------------------------------------------------------
app = FastHTML()
report = Report()


@app.get("/")
def index():
    # Default landing page: employee #1.
    return report(1, Employee())


@app.get("/employee/{id:str}")
def employee(id: str):
    return report(id, Employee())


@app.get("/team/{id:str}")
def team(id: str):
    return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()
