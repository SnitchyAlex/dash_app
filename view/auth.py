# view/auth.py
from dash import html
import dash_bootstrap_components as dbc

# Login page layout
def get_login_layout():
    """Returns the login page layout"""
    return html.Div([
        html.H2('Login', className='gradient-title text-center'),
        dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Username',className='form-label'),
                    dbc.Input(id='login-username', type='text', placeholder='Enter username',className='form-control')
                ])
            ], className='mb-3'),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Password', className='form-label'),
                    dbc.Input(id='login-password', type='password', placeholder='Enter password',className='form-control')
                ])
            ], className='mb-3'),
            dbc.Button('Login', id='login-button', color='primary', disabled= True,className='w-100', size = 'lg'),
            html.Div(id='login-output', className='mt-3')
        ])
    ])