# app.py
from app import create_app
from rich import print

app = create_app()

if __name__ == "__main__":
    print("[bold green]Starting Portfolio Optimizer Flask app...")
    app.run(debug=True)
