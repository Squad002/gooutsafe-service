import os
from dotenv import load_dotenv

# DOT ENV
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# APP
from monolith import create_app

app = create_app(os.getenv("FLASK_CONFIG") or "default")


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    pass