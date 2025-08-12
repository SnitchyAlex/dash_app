# controller/auth.py
import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import login_user, logout_user, current_user
from pony.orm import db_session
from dash import html, dcc
from model.operations import validate_user, get_user_by_username
from controller.admin import register_admin_callbacks

def register_auth_callbacks(app):
    """Register authentication-related callbacks"""
    
    register_admin_callbacks(app)
    # Callback for login form
    @app.callback(
        [Output('login-output', 'children'),
         Output('url', 'pathname', allow_duplicate=True)],
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def login_callback(n_clicks, username, password):
        if not n_clicks or not username or not password:
            return '', dash.no_update
        
        user = validate_user(username, password)
        if user:
            login_user(user)
            return dbc.Alert('Login effettuato!', color='success'), '/dashboard'
        else:
            return dbc.Alert('Username o password non validi', color='danger'), dash.no_update
    # Callback per abilitare/disabilitare il bottone login
    @app.callback(
        Output('login-button', 'disabled'),
        [Input('login-username', 'value'),
         Input('login-password', 'value')]
    )
    def toggle_login_button(username, password):
        # Disabilita se username o password sono vuoti/None
        if not username or not password:
            return True  # Disabilitato
        else:
            return False  # Abilitato
        
    # CALLBACK PRINCIPALE PER IL ROUTING
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/' or pathname is None:
            # Pagina iniziale di benvenuto
            from view.layout import get_welcome_page
            return get_welcome_page()
        elif pathname == '/login':
            # Pagina di login
            from view.auth import get_login_page
            return get_login_page()
        elif pathname == '/dashboard':
            # Dashboard (solo se autenticato)
            if current_user.is_authenticated:
                if current_user.is_admin:
                    from view.admin import get_admin_dashboard
                    return get_admin_dashboard()
                else:
                    from view.layout import get_dashboard_layout
                    return get_dashboard_layout(current_user.username)
            else:
                return dcc.Location(pathname='/login', id='redirect-to-login')
        elif pathname == '/logout':
            # Logout
            logout_user()
            return dcc.Location(pathname='/', id='redirect-after-logout')
        else:
            return html.Div(" 404 - Pagina non trovata")