# Portfolio Optimization Web App

## Setup Instructions

1. **Install Python 3.10.11**
2. **Create Virtual Environment & Install Dependencies**
   - Use the batch script or run:
     - `uv venv .venv --python 3.10.11`
     - `uv pip install -r requirements.txt`
3. **Run the App**
   - Activate the environment and run:
     - `python app.py`

## Project Structure
- `app/` - Application modules
- `templates/` - HTML templates
- `static/css/` - Stylesheets
- `static/js/` - JavaScript
- `tests/` - Test suite
- `scripts/` - Utilities, PRD, setup scripts

## Environment Management
- All dependencies pinned in requirements.txt and pyproject.toml
- Use uv for dependency management

## Features
- Portfolio optimization using Monte Carlo simulation
- Interactive Bokeh visualizations (efficient frontier, asset weights)
- Responsive Flask web UI
- Robust error handling and logging (Rich)
- Fully tested with pytest (unit, integration, visualization)

## Testing
- Run all tests:
  - `pytest --maxfail=2 --disable-warnings -v`
- Test coverage includes data loading, optimization, visualization, Flask routes, and session handling.
- All tests must pass before deployment.

## Deployment
- Procfile included for Heroku-style deployment:
  - `web: gunicorn app:app`
- Set environment variables (e.g., `SECRET_KEY`) via Heroku config or `.env` file (not committed).
- All dependencies are pinned in requirements.txt and pyproject.toml.
- To deploy:
  1. Ensure all tests pass and code is linted (ruff).
  2. Push to your deployment platform (Heroku, Render, etc.).
  3. Static files and templates are served by Flask; Bokeh output is generated as HTML.

## Code Quality
- All core modules and functions have Google-style docstrings.
- Linting via ruff (see pyproject.toml).
- Logging and error handling via Rich for clear diagnostics.
