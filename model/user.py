# model/user.py
from pony.orm import PrimaryKey, Required, Optional, Discriminator
from werkzeug.security import check_password_hash
from flask_login import UserMixin

from .database import db

# Define the User entity con solo gli attributi comuni
class User(db.Entity, UserMixin):
    username = PrimaryKey(str)
    password_hash = Required(str)
    is_admin = Required(bool, default=False)
    role = Discriminator(str)
    
    # Solo attributi comuni a tutti
    name = Required(str)
    surname = Required(str)
    telefono = Optional(str)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.username)