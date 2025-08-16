# view/auth.py
from dash import html
import dash_bootstrap_components as dbc

# Login page layout
def get_login_page():
    """Pagina di login completa con styling"""
    
    return dbc.Container([
        html.Img(
            src="/assets/health.png",
            style={
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "width": "150px",
                "height": "auto",
                "z-index": "1000"
            }
        ),
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

def get_login_layout():
    """Returns the login page layout"""
    return html.Div([
        html.H2('Login', className='gradient-title text-center'),
        dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Username',className='form-label'),
                    dbc.Input(id='login-username', type='text', placeholder='Inserisci lo username',className='form-control')
                ])
            ], className='mb-3'),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Password', className='form-label'),
                    dbc.Input(id='login-password', type='password', placeholder='Inserisci la password',className='form-control')
                ])
            ], className='mb-3'),
            dbc.Button('Login', id='login-button', color='primary', disabled= True,className='w-100', size = 'lg'),
            html.Div(id='login-output', className='mt-3')
        ])
    ])
def get_register_layout():
    """Returns the register page layout with simple message"""
    return dbc.Container([
        html.Img(
            src="/assets/health.png",
            style={
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "width": "150px",
                "height": "auto",
                "z-index": "1000"
            }
        ),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2('Registrazione', className='gradient-title text-center mb-4'),
                        html.P('La funzionalità di registrazione non è ancora disponibile. '
                              'Contatta l\'amministratore per ottenere le credenziali di accesso.',
                              className='text-center mb-4'),
                        dbc.Button(
                            'Torna alla Home', 
                            id='back-to-home-button', 
                            color='primary', 
                            className='w-100', 
                            size='lg',
                            href='/'
                        )
                    ])
                ], className="shadow")
            ], width=6)
        ], justify="center", className="min-vh-100 align-items-center")
    ])