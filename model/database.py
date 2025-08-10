# model/database.py
from pony.orm import Database
import os

# Initialize the database
db = Database()

# Flag per evitare doppia configurazione
_db_configured = False

# Configure the database path - now in the data directory
def configure_db():
    global _db_configured
    
    if _db_configured:
        print("Database already configured, skipping...")
        return None
        
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
        
    db_path = os.path.join(data_dir, 'dash_app.sqlite')
    print(f"Database path: {db_path}")
    
    # Se il database esiste ma è vuoto/corrotto, rimuovilo
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        if file_size == 0:
            os.remove(db_path)
            print("Removed empty database file")
    
    try:
        db.bind(provider='sqlite', filename=db_path, create_db=True)
        _db_configured = True
        print("Database bound successfully")
    except Exception as e:
        print(f"Error binding database: {e}")
        # Se c'è un errore, prova a rimuovere il database e ricreare
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Removed corrupted database, trying again...")
            try:
                db.bind(provider='sqlite', filename=db_path, create_db=True)
                _db_configured = True
                print("Database bound successfully after cleanup")
            except Exception as e2:
                print(f"Error binding database after cleanup: {e2}")
                return None
    
    return db_path