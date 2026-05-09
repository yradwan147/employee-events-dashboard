"""Project-root path resolution + ML model loader for the dashboard."""
import pickle
from pathlib import Path


# Absolute path to the root of this project (two levels up from this file:
# completed/report/utils.py -> completed/).
project_root = Path(__file__).resolve().parent.parent

# Where the trained sklearn pickle lives.
model_path = project_root / "assets" / "model.pkl"


def load_model():
    """Load and return the trained sklearn estimator from `model.pkl`."""
    with model_path.open("rb") as fh:
        return pickle.load(fh)
