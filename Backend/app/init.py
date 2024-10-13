# __init__.py

# Import the modules so they are available at the package level
from .db import init_db, save_to_db, get_history
from .anthropic_api import get_claude_response_with_history
from .routes import tax_router

# Initialize the database
init_db()

# You can add other initial setup or configurations here if needed
