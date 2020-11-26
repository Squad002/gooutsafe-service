from monolith.models import (
    User,
    Review,
    Operator,
    Restaurant,
    RestaurantsPrecautions,
    Precautions,
    Table,
    Mark,
    HealthAuthority,
    Booking,
)

import os
from dotenv import load_dotenv

# DOT ENV
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# APP
from monolith import create_app, db
from flask_migrate import Migrate, upgrade

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)

# Shell
@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Review": Review,
        "Operator": Operator,
        "Restaurant": Restaurant,
        "RestaurantsPrecautions": RestaurantsPrecautions,
        "Precautions": Precautions,
        "Table": Table,
        "Mark": Mark,
        "HealthAuthority": HealthAuthority,
        "Booking": Booking,
    }


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    # upgrade()

    # Insert fake data
    Restaurant.force_index()
