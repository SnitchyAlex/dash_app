# mvc_app.py
import dash
import dash_bootstrap_components as dbc
from flask_login import LoginManager
import os

# Importa il modello
import model

from controller.auth import register_auth_callbacks
from view.layout import get_main_layout

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

server = app.server

# Set a secure secret key for session management
server.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-for-development')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# Set app layout

app.layout = get_main_layout()

# User loader per Flask-Login
@login_manager.user_loader
def load_user(username):
    from pony.orm import db_session
    with db_session:
        return model.User.get(username=username)
    
# Register all callbacks
register_auth_callbacks(app)


# Run the app
if __name__ == '__main__':
    print("Starting Dash MVC Application...")
    print("Access the application at http://127.0.0.1:8050/")
    app.run(debug=True)