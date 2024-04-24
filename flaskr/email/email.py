from flask_mail import Message
from flaskr.extensions import mail
from flaskr.email.email_services import get_instructor_email, get_reservation_code
from flask import url_for

def send_email(subject, recipients, html_body):
    #sender = "jl6701543@gmail.com"
    sender = "noreply.skiressystem@gmail.com"
    msg = Message(subject, sender=sender, recipients=[recipients])
    msg.html = html_body
    mail.send(msg)

def send_reservation_confirmation(user_email, reservation_details):
    formatted_time = reservation_details.cas_zacatku.strftime('%H:%M')
    formatted_date = reservation_details.termin.strftime('%d.%m.%Y')

    instructors = get_instructor_email(reservation_details.ID_rezervace)
    final_instructor = ", ".join(instructors)

    if reservation_details.typ_rezervace == "group-ind":
        typ_rezervace = "Skupinová individuální - jeden instruktor."
    elif reservation_details.typ_rezervace == "group":
        typ_rezervace = "Skupinová - více instruktorů."
    else:
        typ_rezervace = "Individuální."

    html_content = f"""
    <html>
        <body>
            <p>Dobrý den,</p>
            <p>děkujeme Vám za rezervaci hodiny v naší lyžařské škole.</p>
            <p>Níže naleznete všechny důležité informace týkající se Vaší rezervace:</p>
            <ul>
                <li> Rezervační kód: {reservation_details.rezervacni_kod}</li>
                <li>Termín rezervace: {formatted_date}</li>
                <li>Čas rezervace: {formatted_time}</li>
                <li>Instruktor: {final_instructor}</li>
                <li>Stav platby: {reservation_details.platba}</li>
                <li>Délka rezervace: {reservation_details.doba_vyuky}</li>
                <li>Počet žáků: {reservation_details.pocet_zaku}</li>
                <li>Typ výuky: {typ_rezervace}</li>
            </ul>
            <p>V případě jakýchkoli otázek se neváhejte obrátit na školu pro více informací.<br>Případně můžete provést registraci (v případě že jste tak již neučinili) a přistoupit tak ke všem informacím, které se týkají Vaší rezervace, spolu s možnými úpravami a stornem.</p>
            <p>S přáním hezkého dne,<br>Rezervační systém.</p>
        </body>
    </html>
    """

    result = send_email("Rezervace - Ski škola Bublava", user_email, html_content)
    return result

def send_registration_confirmation(user_email):
    link = url_for('information.school_page', _external=True)
    html_content = f"""
    <html>
        <body>
            <p>Dobrý den,</p>
            <p>vítejte v lyžařské škole. Do webové aplikace školy se můžete přihlásit pomocí svého emailu a hesla, které jste uvedli při registraci.<br>V případě zapomenutí hesla je heslo možné na přihlašovací stránce obnovit.</p>
            <p>Webová aplikace Vám umožňuje nahlížet na všechny Vaše rezervace spolu se všemi dostupnými detaily jako například termín, čas začátku, nebo zdali je rezervace zaplacena.<br>Rezervaci můžete v systému také upravovat a měnit její parametry.</p>
            <p>V případě dalších otázek se prosím obraťte přímo na školu, kontakty najdete v sekci <a href="{link}">O nás</a>.</p>
            <p>Děkujeme za využívání rezervačního systému Ski školy Bublava.</p>
            <p>S přáním pěkného dne,<br>Rezervační systém.</p>
        </body>
    </html>
    """
    result = send_email("Registrace - Ski škola Bublava", user_email, html_content)
    return result
    

def send_password_reset(user_email, reset_link):
    
    html_content = f"""
    <html>
        <body>
            <p>Dobrý den,</p>
            <p>obdrželi jsme požadavek na změnu hesla. Pokud jste o změnu hesla nepožádali, prosím tento email ignorujte.</p>
            <p>Pro změnu hesla využijte následující link:</p>
            <p><a href="{reset_link}" style="color: #007BFF;">Změnit heslo</a></p>
            <p>S přáním pěkného dne,<br>Rezervační systém.</p>
        </body>
    </html>
    """
    result = send_email("Obnova hesla - Ski škola Bublava", user_email, html_content)

def send_reservation_cancelation(user_email, reservation_code, payment):
    if payment == "zaplaceno":
        text_payment = "Vaše rezervace byla zaplacena! Pro vrácení penět se prosím stavte osobně na pokladně školy, případně kontaktujte školu pro vrácení penět na účet."
    else:
        text_payment = ""
    html_content = f"""
    <html>
        <body>
            <p>Dobrý den,</p>
            <p>Informujeme Vás, že Vaše rezervace byla zrušena.</p>
            <p>ID zrušené rezervace: {reservation_code}</p>
            <p>{text_payment}</p>
            <p>S přáním pěkného dne,<br>Rezervační systém.</p>
        </body>
    </html>
    """
    result = send_email("Zrušení rezervace - Ski škola Bublava", user_email, html_content)
    return result


def send_payment_confirmation(user_email, reservation_id):
    reservation_code = get_reservation_code(reservation_id)
    html_content = f"""
    <html>
        <body>
            <p>Dobrý den,</p>
            <p>Informujeme Vás, že Vaše platba za rezervaci byla úspěšně zaznamenána.</p>
            <p>ID rezervace: {reservation_code}</p>
            <p>S přáním pěkného dne,<br>Rezervační systém.</p>
        </body>
    </html>
    """
    result = send_email("Potvrzení platby - Ski škola Bublava", user_email, html_content)