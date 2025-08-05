# model/medico.py
from pony.orm import Required, Optional, PrimaryKey, Set
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .user import User
from .database import db

# Define the paziente entity
class Medico(User):
    name = Required(str)
    surname = Required(str)
    telefono = Optional(str)
    specializzazione = Optional(str)
    ##relazioni
    patients = Set("Paziente", reverse="doctors")
    # Valore fisso per il discriminator
    role = "medico"
    