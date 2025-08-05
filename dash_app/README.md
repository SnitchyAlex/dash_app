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
│
├── model/              # Model (DB e dati)
│   ├── database.py     # Config SQLite
│   └── entities.py     # Classi/tabelle DB
│
├── views/              # View (UI)
│   ├── layout.py       # Layout Dash
│   └── components/     # Componenti riutilizzabili
│
├── controller/         # Controller (logica)
│   ├── callbacks.py    # Callback Dash
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
