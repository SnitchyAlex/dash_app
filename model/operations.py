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
            )
            print(f"Created admin: {admin.username}")

            admin2 = User(
                username='indi',
                password_hash=generate_password_hash('indi'),
                is_admin=True,
                name='Indira',
                surname='Adilovic',
            )
            print(f"Created admin: {admin2.username}")
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
            print(f"Admin2: {admin2.username} ({admin2.name} {admin2.surname}) - Role: {admin2.role}")
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
                is_admin=is_admin
            )
        elif role.lower() == "paziente":
            user = Paziente(
                username=username,
                password_hash=password_hash,
                name=name,
                surname=surname,
                is_admin=is_admin
            )
        else:
             user = User(
                username=username,
                password_hash=password_hash,
                name=name,
                surname=surname,
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

# AGGIUNGI QUESTE FUNZIONI in model/operations.py

@db_session
def delete_user_with_relations(username):
    """
    Elimina un utente e tutte le sue relazioni dal database
    Returns: (success: bool, message: str)
    """
    from .user import User
    from .medico import Medico
    from .paziente import Paziente
    from .glicemia import Glicemia  # AGGIUNTA: Import del modello Glicemia
    
    try:
        user = User.get(username=username)
        if not user:
            return False, "Utente non trovato"
        
        # Non permettere di eliminare admin
        if user.is_admin:
            return False, "Non è possibile eliminare un utente amministratore"
        
        user_info = f"{user.name} {user.surname} (@{user.username})"
        relations_removed = []
        
        # Gestisci le relazioni specifiche in base al tipo di utente
        if hasattr(user, 'specializzazione'):  # È un medico
            medico = Medico.get(username=username)
            if medico and hasattr(medico, 'patients'):
                num_patients = len(medico.patients)
                if num_patients > 0:
                    # Rimuovi tutte le relazioni medico-paziente
                    for paziente in list(medico.patients):
                        medico.patients.remove(paziente)
                    relations_removed.append(f"{num_patients} relazioni medico-paziente")
        
        elif hasattr(user, 'codice_fiscale'):  # È un paziente
            paziente = Paziente.get(username=username)
            if paziente:
                # AGGIUNTA: Elimina tutte le registrazioni glicemiche del paziente
                if hasattr(paziente, 'glicemie'):
                    glicemie_count = paziente.glicemie.count()
                    if glicemie_count > 0:
                        # Elimina tutte le registrazioni glicemiche
                        for glicemia in list(paziente.glicemie):
                            glicemia.delete()
                        relations_removed.append(f"{glicemie_count} registrazioni glicemiche")
                
                # Gestisci le relazioni paziente-medico
                if hasattr(paziente, 'doctors'):
                    num_doctors = len(paziente.doctors)
                    if num_doctors > 0:
                        # Rimuovi tutte le relazioni paziente-medico
                        for medico in list(paziente.doctors):
                            paziente.doctors.remove(medico)
                        relations_removed.append(f"{num_doctors} relazioni paziente-medico")
        
        # Qui puoi aggiungere altre relazioni se esistono (es: appuntamenti, cartelle cliniche, etc.)
        # Esempio:
        # if hasattr(user, 'appointments'):
        #     appointments_count = len(user.appointments)
        #     if appointments_count > 0:
        #         for appointment in list(user.appointments):
        #             appointment.delete()
        #         relations_removed.append(f"{appointments_count} appuntamenti")
        
        # Forza il commit delle modifiche alle relazioni prima di eliminare l'utente
        commit()
        
        # Elimina l'utente
        user.delete()
        
        # Commit finale
        commit()
        
        # Costruisci il messaggio di successo
        success_message = f"Utente {user_info} eliminato con successo"
        if relations_removed:
            success_message += f" (rimosse anche: {', '.join(relations_removed)})"
        
        return True, success_message
        
    except Exception as e:
        print(f"Errore durante l'eliminazione dell'utente {username}: {e}")
        import traceback
        traceback.print_exc()
        return False, f"Errore interno: {str(e)}"

@db_session
def get_all_users_for_dropdown():
    """
    Restituisce tutti gli utenti non-admin formattati per dropdown
    Returns: list di dict con label e value
    """
    from .user import User
    
    try:
        users = User.select()
        options = []
        
        for user in users:
            # Non mostrare gli admin nella lista
            if not user.is_admin:
                # Determina il tipo di utente per l'etichetta
                user_type = ""
                if hasattr(user, 'specializzazione'):  # È un medico
                    user_type = "👨‍⚕️ Dr. "
                elif hasattr(user, 'codice_fiscale'):  # È un paziente
                    user_type = "👤 "
                else:
                    user_type = "👥 "
                
                label = f"{user_type}{user.name} {user.surname} ({user.username})"
                options.append({"label": label, "value": user.username})
        
        return options
        
    except Exception as e:
        print(f"Errore nel recupero utenti per dropdown: {e}")
        return []


@db_session
def check_user_relations(username):
    """
    Controlla le relazioni di un utente prima dell'eliminazione
    Returns: dict con informazioni sulle relazioni
    """
    from .user import User
    
    try:
        user = User.get(username=username)
        if not user:
            return {'exists': False}
        
        relations = {
            'exists': True,
            'user_type': user.role,
            'is_admin': user.is_admin,
            'relations': []
        }
        
        if hasattr(user, 'specializzazione'):  # Medico
            if hasattr(user, 'patients'):
                patients_count = len(user.patients)
                if patients_count > 0:
                    relations['relations'].append({
                        'type': 'patients',
                        'count': patients_count,
                        'description': f'{patients_count} pazienti assegnati'
                    })
        
        elif hasattr(user, 'codice_fiscale'):  # Paziente
            if hasattr(user, 'doctors'):
                doctors_count = len(user.doctors)
                if doctors_count > 0:
                    relations['relations'].append({
                        'type': 'doctors', 
                        'count': doctors_count,
                        'description': f'{doctors_count} medici assegnati'
                    })
        
        return relations
        
    except Exception as e:
        print(f"Errore nel controllo relazioni utente {username}: {e}")
        return {'exists': False, 'error': str(e)}


