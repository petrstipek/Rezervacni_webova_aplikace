from flask_mail import Message
from .extensions import mail

def send_reservation_confirmation(user_email, reservation_details):
    msg = Message("Reservation Confirmation", recipients=[user_email])
    msg.body = f"Hello, your reservation is confirmed. Details: {reservation_details}"
    mail.send(msg)