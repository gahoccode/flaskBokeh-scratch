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

### Procfile Deployment (Heroku, etc.)
- Procfile included for production deployment:
  - `web: gunicorn wsgi:app`
- Set environment variables in your deployment platform:
  - `SECRET_KEY`: Generate a secure random key
  - `FLASK_ENV`: Set to `production` for production deployments

### Docker Deployment
- Dockerfile and docker-compose.yml provided for containerized deployment
- Environment variables can be set in docker-compose.yml or passed at runtime
- Suitable for any container orchestration platform (Kubernetes, ECS, etc.)
- Images are based on Python 3.10-slim for minimal size and security

#### Docker Usage Instructions
1. **Build and start the container**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - Open your browser and navigate to `http://localhost:5000` (or the port specified in your .env file)

3. **Run in detached mode**:
   ```bash
   docker-compose up -d
   ```

4. **Stop the container**:
   ```bash
   docker-compose down
   ```

5. **View logs**:
   ```bash
   docker-compose logs -f
   ```

6. **Override environment variables**:
   ```bash
   SECRET_KEY=your-secure-key docker-compose up
   ```

### Render Deployment
1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app` (not app:app)
   - **Environment Variables**: Add `SECRET_KEY` and `FLASK_ENV=production`

### Troubleshooting Deployment
- If you see `Failed to find attribute 'app' in 'app'` error:
  - Verify your start command is `gunicorn wsgi:app`
  - Check that wsgi.py exists and contains `app = create_app()`
- If static files (CSS/JS) return 404 errors:
  - Ensure static files are in the correct location
  - Check Flask app configuration for static folder path
  - For Render, you may need to set `STATIC_URL_PATH` environment variable

- To deploy:
  1. Ensure all tests pass and code is linted (ruff).
  2. Push to your deployment platform (Heroku, Render, etc.).
  3. Static files and templates are served by Flask; Bokeh output is generated as HTML.

## Code Quality
- All core modules and functions have Google-style docstrings.
- Linting via ruff (see pyproject.toml).
- Logging and error handling via Rich for clear diagnostics.
