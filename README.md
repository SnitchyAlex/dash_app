# Dash MVC Application

A web application built with Dash and following the Model-View-Controller (MVC) architectural pattern.

## Features //sistemare

- Multiple pages with URL routing
- User authentication with login/logout
- Dynamic navigation based on login status
- Protected routes for authenticated users only
- Admin capabilities for user management
- Project management functionality
- Pony ORM with SQLite database

## Project Structure

dash_app/
|
│──assets/
│   |__ add.png
|   ├── admin.png     
│   |── bin.png      
|   |── doctor.png
|   ├── health.png
│   |__ home.png
|   ├── login.png    
│   |── patient.png      
|   |── register.png
|   ├── sfondo.gif      # Sfondo animato bubbles
|   |── style.css       # File css per lo stile generale
|   |── wave.gif
|   |── bell_ring.png
    |── dati.png
    |── farmaco.png
    |── glicemia.png
    |── gmail.png
    |── grafico.png
    |── messaggi.png
    |── pc.gif
    |── segui.png
    |── sintomi.png
    |── terapia.png
    |── valigia.png
    |── wave.png
    


|
├── data/
|   |__dash_app.sqlite  # file.sqlite (database)
|
├── model/              # Model (DB e dati)
│     |__ __init__.py
|     ├── database.py     # Config SQLite
│     |── medico.py       # Classi/tabelle DB
|     |── paziente.py
|     ├── user.py
|     ├── glicemia.py
|     ├── operations.py
|     ├── sintomi.py
|     ├── terapia.py
|     └── assunzione.py

│
├── view/              # View (UI)
│   ├── layout.py      # Layout dash
    ├── doctor.py
    ├── patient.py
|   |── auth.py       
│   └── admin.py
│
├── controller/         # Controller (logica)
    ├──__init__.py
    ├── doctor.py
    ├── patient.py
│   ├── admin.py    
│   └── auth.py         # Autenticazione (Flask-Login)
│
├── app.py              # App principale (Flask + Dash)
└── requirements.txt    # Dipendenze

## Default Users //sistemare

The application comes with two default users:
- Regular user: username `user1`, password `password1`
- Admin user: username `admin`, password `adminpass`
- Quick admin login: username `a`, password `a`

## MVC Architecture

This application follows the Model-View-Controller (MVC) architectural pattern:

- **Model**: Handles data logic and database operations
- **View**: Manages the UI components and layouts
- **Controller**: Processes user inputs and coordinates the Model and View
