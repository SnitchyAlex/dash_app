from pony.orm import db_session, select, delete, commit, desc, count
from werkzeug.security import generate_password_hash
from datetime import date, datetime

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
def add_user(username, password, email=None, is_admin=False):
    """Add a new user to the database"""
    from .user import User
    if User.get(username=username):
        return False
    
    User(
        username=username, 
        password_hash=generate_password_hash(password),
        is_admin=is_admin,
        role='paziente' #paziente è il ruolo di default
    )
    return True

@db_session
def validate_user(username, password):
    """Validate user credentials"""
    from .user import User
    user = User.get(username=username)
    if user and user.check_password(password):
        return user
    return None

@db_session
def remove_doctor_from_patient(patient_username, doctor_username):
    """Rimuove un medico da un paziente"""
    from .paziente import Paziente
    from .medico import Medico
    
    paziente = Paziente.get(username=patient_username)
    medico = Medico.get(username=doctor_username)
    
    if paziente and medico and medico in paziente.doctors:
        paziente.doctors.remove(medico)
        print(f"Removed doctor {medico.name} from patient {paziente.name}")
        return True
    return False


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


@db_session
def get_patient_info(patient_username):
    """Ottieni informazioni complete di un paziente"""
    from .paziente import Paziente
    
    paziente = Paziente.get(username=patient_username)
    if paziente:
        return {
            'username': paziente.username,
            'name': paziente.name,
            'surname': paziente.surname,
            'telefono': paziente.telefono,
            'eta': paziente.eta,
            'codice_fiscale': paziente.codice_fiscale,
            'birth_date': paziente.birth_date,
            'doctors': [{'username': d.username, 'name': f"Dr. {d.name} {d.surname}", 'specializzazione': d.specializzazione} for d in paziente.doctors]
        }
    return None


@db_session
def get_doctor_info(doctor_username):
    """Ottieni informazioni complete di un medico"""
    from .medico import Medico
    
    medico = Medico.get(username=doctor_username)
    if medico:
        return {
            'username': medico.username,
            'name': medico.name,
            'surname': medico.surname,
            'telefono': medico.telefono,
            'specializzazione': medico.specializzazione,
            'patients': [{'username': p.username, 'name': f"{p.name} {p.surname}", 'eta': p.eta} for p in medico.patients]
        }
    return None