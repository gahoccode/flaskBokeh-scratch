# app/__init__.py
from flask import Flask
from rich import print
import os

def create_app():
    """Flask application factory."""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.abspath(os.path.join(base_dir, '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'replace-this-with-a-secure-random-key')
    # Production-safe: DEBUG and TEMPLATES_AUTO_RELOAD only if dev
    flask_env = os.environ.get('FLASK_ENV', 'production')
    debug_mode = flask_env == 'development' or os.environ.get('DEBUG', '0') == '1'
    app.config['DEBUG'] = debug_mode
    app.config['TEMPLATES_AUTO_RELOAD'] = debug_mode

    @app.route("/", methods=["GET"])
    def main():
        from flask import render_template, request, get_flashed_messages
        error = request.args.get('error')
        messages = get_flashed_messages()
        return render_template("index.html", error=error, messages=messages)

    @app.route("/optimize", methods=["POST"])
    def optimize():
        """
        Handle optimization form submission, validate inputs, run backend logic, generate Bokeh HTML, and serve it.
        """
        from flask import request, send_file, redirect, url_for, flash, session
        import os
        import pandas as pd
        from app.data_loader import DataLoader, DataLoaderError
        from app.portfolio_optimizer import PortfolioOptimizer, PortfolioOptimizerError
        from app.plots import combined_layout
        from bokeh.plotting import output_file, save
        from rich import print as rich_print
        import re

        # Parse and validate form data
        symbols_raw = request.form.get('symbols', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        num_portfolios_raw = request.form.get('num_portfolios', '').strip()
        risk_free_rate_raw = request.form.get('risk_free_rate', '').strip()

        # Validate symbols
        if not symbols_raw:
            flash("Please enter at least one stock symbol.", "error")
            return redirect(url_for('main'))
        symbols = [s.strip().upper() for s in symbols_raw.split(',') if s.strip()]
        if not symbols or any(not re.match(r'^[A-Z0-9.\-]+$', s) for s in symbols):
            flash("Invalid symbol(s) detected. Use only letters, numbers, dashes, or dots.", "error")
            return redirect(url_for('main'))

        # Validate dates
        if not start_date or not end_date:
            flash("Please provide both start and end dates.", "error")
            return redirect(url_for('main'))
        if start_date > end_date:
            flash("Start date must be before end date.", "error")
            return redirect(url_for('main'))

        # Validate num_portfolios
        try:
            num_portfolios = int(num_portfolios_raw)
            if not (100 <= num_portfolios <= 10000):
                raise ValueError
        except Exception:
            flash("Number of portfolios must be an integer between 100 and 10,000.", "error")
            return redirect(url_for('main'))

        # Validate risk_free_rate
        try:
            risk_free_rate = float(risk_free_rate_raw)
        except Exception:
            flash("Risk-free rate must be a valid number.", "error")
            return redirect(url_for('main'))

        # Run DataLoader
        try:
            dl = DataLoader(source_url=None, start_date=start_date, end_date=end_date)
            dl.load(symbols)
            dl.clean()
            dl.filter_dates()
            price_data = dl.get_data()
        except Exception as e:
            rich_print(f"[bold red]Data loading error:[/bold red] {e}")
            flash(f"Data loading error: {e}", "error")
            return redirect(url_for('main', error=str(e)))

        # Run PortfolioOptimizer
        try:
            po = PortfolioOptimizer(price_data, num_portfolios=num_portfolios, risk_free_rate=risk_free_rate)
            po.run_simulation()
            metrics = po.get_metrics_df()
            optimal = po.get_optimal_portfolios()
        except Exception as e:
            rich_print(f"[bold red]Optimization error:[/bold red] {e}")
            flash(f"Optimization error: {e}", "error")
            return redirect(url_for('main', error=str(e)))

        # Store only minimal user input in session if needed
        session['last_inputs'] = dict(symbols=symbols, start_date=start_date, end_date=end_date, num_portfolios=num_portfolios, risk_free_rate=risk_free_rate)

        # Generate Bokeh HTML output
        layout = combined_layout(metrics, optimal, price_data=price_data)
        output_path = os.path.join(os.getcwd(), 'output.html')
        output_file(output_path, title="Portfolio Optimization Results")
        save(layout)
        return redirect(url_for('results'))

    @app.route("/results", methods=["GET"])
    def results():
        from flask import send_file
        import os
        output_path = os.path.join(os.getcwd(), 'output.html')
        if not os.path.exists(output_path):
            return "No results available. Please run an optimization first.", 404
        return send_file(output_path, mimetype='text/html', as_attachment=False)

    return app
