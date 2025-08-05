# model/paziente.py
from datetime import datetime
from pony.orm import Required, Optional, PrimaryKey, Set
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .user import User
from .database import db

# Define the paziente entity
class Paziente(User):
    name = Required(str)
    surname = Required(str)
    birth_date = Optional(datetime)
    eta = Optional(int)
    telefono = Optional(str)

    #Rlations
    doctors = Set("Medico", reverse="patients")
    # Valore fisso per il discriminator
    role = "paziente"
    