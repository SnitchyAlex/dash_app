# model/database.py
from pony.orm import Database
import os
from pathlib import Path

# Initialize the database
db = Database()

# Configure the database path - now in the data directory
def configure_db():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    db_path = os.path.join(data_dir, 'dash_app.sqlite')
    db.bind(provider='sqlite', filename=db_path, create_db=True)
    db.generate_mapping(create_tables=True)