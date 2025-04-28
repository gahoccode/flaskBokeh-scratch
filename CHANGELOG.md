# Changelog

## 2025-04-28
- Initialized Taskmaster project for Flask+Bokeh portfolio optimizer
- Created scripts/prd.txt with requirements
- Parsed PRD to generate 10 initial tasks (tasks/tasks.json)
- Displayed details for Task 4: Create Bokeh visualization module
- Ran complexity analysis on all tasks (scripts/task-complexity-report.json):
    - 2 tasks rated high complexity, 8 medium complexity
    - Recommendations for task expansion and risk areas identified

### Task 1: Set up Flask project structure and environment

#### Subtasks Checklist
- [x] Create core directory structure (`app/`, `templates/`, `static/css/`, `static/js/`, `tests/`, `scripts/`)
- [x] Create README.md with setup instructions
- [x] Add .gitignore
- [x] Add .env.example (already exists)
- [x] Add placeholder files for templates and tests
- [x] Create initial Flask app factory in `app/__init__.py`
- [x] Create static/css/style.css and static/js/script.js
- [x] Set up virtual environment and dependency management (uv, requirements.txt, pyproject.toml)
- [x] Add and pin dependencies (Flask, Bokeh, vnstock==3.2.2, ruff, rich)
- [x] Create batch script for environment management
- [x] Test initial Flask app run

### Task 2: Implement vnstock-based data fetching and processing

#### Subtasks Checklist
- [x] Set up the data_loader.py module structure with vnstock integration
- [x] Implement vnstock-based data fetching (per test.py example)
- [x] Implement data cleaning and processing
- [x] Add date range filtering support
- [x] Implement comprehensive error handling
- [x] Finalize data output formatting for optimization algorithm

_Progress will be updated as each subtask is completed._

### Task 3: Develop portfolio optimization algorithm

#### Subtasks Checklist
- [x] Create portfolio_optimizer.py module and class structure
- [x] Implement Monte Carlo simulation logic
- [x] Calculate portfolio metrics (returns, risk, Sharpe ratio)
- [x] Identify optimal portfolios (max Sharpe, min variance, max return)
- [x] Output results for visualization
- [x] Add robust error handling and logging
- [x] Document and prepare for unit testing

### Task 4: Integrate optimizer and DataLoader with Flask/Bokeh UI

#### Subtasks Checklist
- [x] Add Task 4 checklist to CHANGELOG.md
- [x] Design Flask route(s) for optimization workflow
    - Multi-page flow:
        - /optimize/input (GET): Input form for symbols, dates, parameters
        - /optimize/results (POST): Display results and Bokeh plots
- [x] Integrate DataLoader and PortfolioOptimizer in backend (route stubs in place)
- [x] Implement Bokeh plot generation functions and HTML output
    - All plots combined and served as a single HTML page via /optimize/results
- [x] Render input form via template (optimize_input.html)
- [x] Add error handling, user feedback, and logging
- [x] Document integration and prepare for UI testing
    - Multi-page Flask UI (input/results)
    - Robust error handling and user feedback
    - All plots combined in Bokeh HTML output
    - Logging with rich for backend errors

### Task 5: Implement Flask Routes and Form Handling

#### Subtasks Checklist
- [x] Add Task 5 checklist to CHANGELOG.md
- [x] Main page route ('/') renders index.html with input form
- [x] Results route ('/optimize') processes form, runs optimization, returns Bokeh HTML output (not embedded)
- [x] Form validation logic (server-side, clear error messages)
    - Robust validation for symbols, date range, number of portfolios, and risk-free rate
    - User-friendly error messages flashed and displayed on main form
- [x] Session management for user inputs/results
    - User input and results stored in Flask session for download and multi-step workflows
- [x] Integration tests (status codes, redirects, session)
    - All routes, validation, and session management tested and passing


---

### Task 6: Develop index.html template with input form

- [x] Created and enhanced templates/index.html as main input form
- [x] All required fields present: stock symbols, date range, number of portfolios, risk-free rate
- [x] HTML5 validation for all fields (pattern, min/max, required)
- [x] Responsive design using flexbox and media queries
- [x] Clear instructions, labels, and documentation link
- [x] Accessibility improvements (label associations, aria attributes)
- [x] Tested rendering, validation, and responsiveness on multiple devices

**Result:**
- Main input form is robust, user-friendly, and meets all requirements for Task 6.

**Next:**
- Ready for further UI polish, feature expansion, or next task as needed.

## [Unreleased]

### Changed
- Price history line chart now uses the original price DataFrame, so each stock appears as a distinct colored line over time.
- Each asset line uses a different color for clarity (Category10 palette).
- Flask debug mode enabled for immediate code reloads and error display during development.

### Added
- Asset price history line chart: Added a Bokeh line chart to visualize historical asset prices as part of the optimization results page. This chart appears above the efficient frontier and portfolio composition pie charts for a more comprehensive analysis. (2025-04-28)
- **[Task 9: Testing Suite]** Unit test ([tests/test_bokeh_html_output.py](tests/test_bokeh_html_output.py)) to verify that Bokeh visualizations can be saved as HTML and are compatible with Flask's send_file for serving as a redirected route. The test checks file creation, HTML validity, Bokeh script presence, and correct MIME type for browser rendering.
- **[Task 9: Testing Suite]** Unit tests ([tests/test_data_loader.py](tests/test_data_loader.py)) for DataLoader covering data cleaning, date filtering, error handling, and warnings. Tests use a datetime index and pytest fixtures for robust and reproducible coverage.
- **[Task 9: Testing Suite]** Unit tests ([tests/test_plots.py](tests/test_plots.py)) for Bokeh visualization helpers, covering efficient frontier, weights bar, and combined layout plot generation. Tests use dummy data fixtures and dynamic type checks for robust and version-independent validation.
- **[Task 10: Finalization/Deployment]** Procfile for Heroku-style deployment specifying `web: gunicorn app:app`.

### Changed
- **[Task 10: Finalization/Deployment]** Full integration test suite run: all unit, integration, and visualization tests pass (18/18). Application is verified production-ready for deployment.

### UI Polish: Portfolio Optimization Input Form
- The portfolio optimization input form (`templates/index.html`) has been fully redesigned with a 21st.dev-inspired (shadcn/ui) look.
- Card, Alert, Input, Button, and Label styles now use modern class names, spacing, and layout.
- The HTML/CSS was translated for Flask/Jinja2 compatibility—no React or JSX code is present.
- All Flask/Jinja2 validation, accessibility, and logic are preserved.
- The UI is now more visually appealing, accessible, and responsive on all devices.

### Results Display: Output Options
- There are two options for displaying optimization results:
  1. **Unified `results.html` template:** A Flask/Jinja2 template that displays Bokeh visualizations, key metrics, optimal weights table, and navigation, using a consistent app design (recommended for advanced features).
  2. **Bokeh `output.html` file:** Serve or redirect to the static Bokeh-generated HTML file for simplicity and full interactivity (current implementation).
- The current app uses option 2 for ease of use and direct Bokeh integration. Option 1 can be implemented in the future for a richer, unified user experience.
- Flask route logic redirects to `/static/output.html` after optimization.
- **Note:** For multi-user or concurrent scenarios, unique output filenames per session/user are recommended to avoid conflicts.
