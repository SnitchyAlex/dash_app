from pony.orm import db_session, select, delete, commit, desc, count
from werkzeug.security import generate_password_hash
from datetime import date, datetime
from pony.orm import commit

@db_session
def initialize_db():
    # Import locali per evitare problemi circolari
    from .user import User
    from .paziente import Paziente
    from .medico import Medico
    
    # Controlla se già esistono utenti
    total_users = User.select().count()
    print(f"Current users in database: {total_users}")
    
    if total_users == 0:
        print("No users found, creating initial data...")
        
        try:
            # Crea l'admin
            admin = User(
                username='ale',
                password_hash=generate_password_hash('ale'),
                is_admin=True,
                name='Alessia',
                surname='Gallista',
                telefono='123456789'
            )
            print(f"Created admin: {admin.username}")
            
            # Crea un paziente di esempio
            paziente = Paziente(
                username='anna.sandre', 
                password_hash=generate_password_hash('anna'), 
                is_admin=False,
                name='Anna',
                surname='Sandre',
                telefono='123456789',
                # Attributi specifici del paziente
                eta=30,
                codice_fiscale='SNRANN90A01H501Z'
            )
            print(f"Created patient: {paziente.username}")
            
            # Crea un medico di esempio
            medico = Medico(
                username='dr.rossi',
                password_hash=generate_password_hash('dr.rossi'),
                is_admin=False,
                name='Mario',
                surname='Rossi',
                telefono='987654321',
                # Attributi specifici del medico
                specializzazione='Cardiologia',
            )
            print(f"Created doctor: {medico.username}")
            
            # Crea un altro medico
            medico2 = Medico(
                username='dr.bianchi',
                password_hash=generate_password_hash('dr.bianchi'),
                is_admin=False,
                name='Laura',
                surname='Bianchi',
                telefono='555666777',
                # Attributi specifici del medico
                specializzazione='Neurologia',
            )
            print(f"Created doctor: {medico2.username}")
            
            # Assegna medici al paziente (relazione many-to-many)
            paziente.doctors.add(medico)
            paziente.doctors.add(medico2)
            
            print("=== Initialization Summary ===")
            print(f"Admin: {admin.username} ({admin.name} {admin.surname}) - Role: {admin.role}")
            print(f"Patient: {paziente.username} ({paziente.name} {paziente.surname}) - Role: {paziente.role}")
            print(f"  - Age: {paziente.eta}, CF: {paziente.codice_fiscale}")
            print(f"  - Assigned doctors: {len(paziente.doctors)}")
            print(f"Doctor 1: {medico.username} ({medico.name} {medico.surname}) - Role: {medico.role}")
            print(f"  - Specialization: {medico.specializzazione}")
            print(f"Doctor 2: {medico2.username} ({medico2.name} {medico2.surname}) - Role: {medico2.role}")
            print(f"  - Specialization: {medico2.specializzazione}")
            
            # Forza il commit per assicurarsi che tutto sia salvato
            commit()
            print("Database initialization completed successfully!")
            
        except Exception as e:
            print(f"Error during database initialization: {e}")
            import traceback
            traceback.print_exc()
            raise
    else:
        print("Users already exist, skipping initialization")
        # Stampa info sugli utenti esistenti
        users = User.select()
        for user in users:
            print(f"Existing user: {user.username} ({user.role})")


@db_session
def assign_doctor_to_patient(patient_username, doctor_username):
    """Assegna un medico a un paziente"""
    from .paziente import Paziente
    from .medico import Medico
    
    paziente = Paziente.get(username=patient_username)
    medico = Medico.get(username=doctor_username)
    
    if paziente and medico:
        paziente.doctors.add(medico)
        print(f"Assigned doctor {medico.name} to patient {paziente.name}")
        return True
    return False

@db_session
def get_user_by_username(username):
    """Get a user by username"""
    from .user import User
    return User.get(username=username)

@db_session
def add_user(username, password, name, surname, telefono=None, role="User", is_admin=False):
    """Add a new user to the database"""
    from .user import User
    from .medico import Medico
    from .paziente import Paziente

    if User.get(username=username):
        return False
    
    password_hash = generate_password_hash(password)
    try:
        if role.lower() == "medico":
            user = Medico(
                username=username,
                password_hash=password_hash,
                name=name,
                surname=surname,
                telefono=telefono,
                is_admin=is_admin
            )
        elif role.lower() == "paziente":
            user = Paziente(
                username=username,
                password_hash=password_hash,
                name=name,
                surname=surname,
                telefono=telefono,
                is_admin=is_admin
            )
        else:
             user = User(
                username=username,
                password_hash=password_hash,
                name=name,
                surname=surname,
                telefono=telefono,
                is_admin=is_admin
            )
        commit()
        return True

    except Exception as e:
        return False

@db_session
def delete_user(username):
    """Elimina un utente (solo per admin)"""
    from .user import User
    
    try:
        user = User.get(username=username)
        if not user:
            return False
        
        # Non permettere di eliminare admin
        if user.role == "admin":
            return False
        
        user.delete()
        return True
    
    except Exception as e:
        print(f"Errore durante l'eliminazione dell'utente {username}: {e}")
        return False


@db_session
def validate_user(username, password):
    """Validate user credentials"""
    from .user import User
    user = User.get(username=username)
    if user and user.check_password(password):
        return user
    return None


@db_session
def get_patient_doctors(patient_username):
    """Ottieni tutti i medici di un paziente"""
    from .paziente import Paziente
    
    paziente = Paziente.get(username=patient_username)
    if paziente:
        return list(paziente.doctors)
    return []


@db_session
def get_doctor_patients(doctor_username):
    """Ottieni tutti i pazienti di un medico"""
    from .medico import Medico
    
    medico = Medico.get(username=doctor_username)
    if medico:
        return list(medico.patients)
    return []


