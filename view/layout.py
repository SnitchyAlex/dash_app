from dash import dcc, html
import dash_bootstrap_components as dbc
from view.auth import get_login_layout

def get_main_layout():
    """Layout principale dell'app con routing"""
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

def get_dashboard_layout(username):
    """Layout della dashboard"""
    return dbc.Container([
        html.H1("Dashboard", className="mb-4"),
        dbc.Alert(f"Benvenuto/a, {username}!", color="success"),
        dbc.Button("Logout", href="/logout", color="secondary")
    ])

def get_login_page():
    """Pagina di login completa con styling"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        get_login_layout()
                    ])
                ], className="shadow")
            ], width=6)
        ], justify="center", className="min-vh-100 align-items-center")
    ])
def get_welcome_page():
    """Pagina di benvenuto iniziale"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H1("Benvenuto/a nella nostra app", className="text-center mb-4"),
                        html.P("Accedi per continuare o registrati", className="text-center text-muted mb-4"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("Vai al Login", href="/login", size="lg",className="welcome-btn")
                        ], width = 5),
                        dbc.Col([
                            dbc.Button("Registrati", href="/register", color="outline-primary", size="lg",className="welcome-btn")
                        ], width = 3)
                    ],justify="center")
                ])
                ], className="shadow")
            ], width=6)
        ], justify="center", className="min-vh-100 align-items-center")
    ])