from flaskr.extensions import database
from flask_login import current_user
from flaskr.models import Osoba
from flaskr.auth.auth import check_password, hash_password

def validate_password(old_password):
    user = database.session.query(Osoba).filter(Osoba.ID_osoba==current_user.get_id()).first()
    check_result = check_password(current_user.heslo, old_password)
    if check_result:
        return True
    return False

def update_personal_information(name, surname, email, tel_number, password):
    try:
        if name != current_user.jmeno and name != "":
            current_user.jmeno = name
        if surname != current_user.prijmeni and surname != "":
            current_user.prijmeni = surname
        if email != current_user.email and email != "":
            current_user.email = email
        if tel_number != current_user.tel_cislo and tel_number != "":
            current_user.tel_cislo = tel_number
        if password and password != "":
            if not check_password(current_user.heslo, password):
                current_user.heslo = hash_password(password)
            else:

                return (False, "Nové heslo musí být jiné oproti aktuálnímu heslu!")

        database.session.commit()
        return (True, "Údaje byly úspěšně aktualizovány!")

    except Exception as e:
        database.session.rollback()
        return (False, f"An error occurred: {e}")