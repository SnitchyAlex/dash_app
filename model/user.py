# model/user.py
from pony.orm import Required, Optional, PrimaryKey, Set, Discriminator
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .database import db

# Define the User entity
class User(db.Entity, UserMixin):
    username = Required(str, unique=True)
    password_hash = Required(str)
    is_admin = Required(bool, default=False)
    role = Discriminator(str)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)