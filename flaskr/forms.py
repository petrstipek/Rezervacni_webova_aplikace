from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField, BooleanField, HiddenField, PasswordField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, NumberRange, Optional, ValidationError

class PersonalInformationForm(FlaskForm):

    name_validator = Regexp(r"^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ]+([-' ][a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ]+)*$",
    message="Jméno může obsahovat pouze písmena, pomlčky, apostrofy a mezery.")

    name = StringField(label="Jméno", validators=[Length(min=2, max=20), DataRequired(),name_validator])
    surname = StringField(label="Příjmení", validators=[Length(min=2, max=30), DataRequired(),name_validator])
    
    tel_number = StringField('Telefonní číslo', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Formát telefonního čísla: '+999999999'!")
    ], render_kw={"type": "tel"})
    email =  StringField('Email', validators=[DataRequired(), Email()], render_kw={"type": "email"})
    age_client = IntegerField('Věk', validators=[Optional(), NumberRange(min=5, max=120)])
    experience_client = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    
    student_client = BooleanField('Žák stejný jako klient', validators=[])
    more_students = BooleanField("Objednat více žáků", validators=[])

    name_client1 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])
    name_client2 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])
    name_client3 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])

    surname_client1 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])
    surname_client2 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])
    surname_client3 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])

    age_client1 = IntegerField('Věk', validators=[Optional(), NumberRange(min=5, max=120)])
    age_client2 = IntegerField('Věk', validators=[Optional(), NumberRange(min=5, max=120)])
    age_client3 = IntegerField('Věk', validators=[Optional(), NumberRange(min=5, max=120)])

    experience_client1 = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    experience_client2 = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    experience_client3 = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])

    lesson_type = SelectField('Výuka', choices=[('individual', 'Individuální'), ('group', 'Skupinová')], validators=[Optional()])
    lesson_length = SelectField("Délka výuky", choices=[("1hodina", "1 hodina"), ("2hodiny", "2 hodiny")])
    lesson_instructor_choices = SelectField("Instruktor", choices = [])
    language_selection = SelectField("Jazyk", choices=[("czech", "čeština"), ("deutsch", "deutsch"), ("english", "english")])

    note = TextAreaField('Note', render_kw={"placeholder": "Napište nám zprávu."}, validators=[Optional(), Length(min=0, max=300)])

    date = HiddenField("date", validators=[DataRequired()])
    time_reservation = HiddenField("time", validators=[DataRequired()])

    lesson_length_hidden = HiddenField()
    lesson_instructor_choices_hidden = HiddenField()

    submit = SubmitField('Odeslat rezervaci')

class ReservationInformationForm(FlaskForm):
    reservation_id = StringField("ID rezervace", validators=[DataRequired()])
    submit = SubmitField('Získat informace')

class LoginForm(FlaskForm):
    username = StringField(label="Přihlašovací jméno: ", validators=[DataRequired()])
    password = PasswordField(label="Heslo:", validators=[DataRequired()])
    submit = SubmitField(label="Přihlásit se")

def validate_on_the_hour(form, field):
    if field.data is not None:
        if field.data.minute != 0:
            raise ValidationError('round hours')

class LessonInsertForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired()], format='%Y-%m-%d')
    time_start = SelectField("Čas začátku", validators=[DataRequired()], choices=[(f'{i:02d}:00', f'{i:02d}:00') for i in range(24)])
    lesson_type = SelectField('Typ lekce', choices=[('ind', 'Individuální'), ('group', 'Skupinová')], validators=[Optional()])
    capacity = IntegerField('Kapacita', validators=[Optional(), NumberRange(min=0, max=20)])
    lesson_instructor_choices = SelectField("Hlavní Instruktor", choices = [], validators=[DataRequired()])
    lesson_instructor_choices2 = SelectField("Instruktor 2", choices = [], validators=[Optional()])
    lesson_instructor_choices3 = SelectField("Instruktor 3", choices = [], validators=[Optional()])
    lesson_instructor_choices4 = SelectField("Instruktor 4", choices = [], validators=[Optional()])
    submit = SubmitField(label="Vložit hodinu")
    date2 = DateField('Datum', validators=[Optional()], format='%Y-%m-%d')

class InstructorInsertForm(FlaskForm):
    name = StringField(label="Jméno", validators=[Length(min=2, max=30), DataRequired()])
    surname = StringField(label="Příjmení", validators=[Length(min=2, max=30), DataRequired()])
    tel_number = StringField('Telefonní číslo', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ], render_kw={"type": "tel"})
    email =  StringField('Email', validators=[DataRequired(), Email()], render_kw={"type": "email"})
    experience = SelectField('Zkušenosti', choices=[('junior', 'Junior'), ('senior', 'Senior')], validators=[Optional()])
    date_birth = DateField('Datum narození', validators=[DataRequired()], format='%Y-%m-%d')
    date_started = DateField('Datum nástupu', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField(label="Vložit instruktora")

class ReservationInformationAdmin(FlaskForm):
    name = StringField(label="Jméno klienta", validators=[Length(min=2, max=30), Optional()])
    surname = StringField(label="Příjmení klienta", validators=[Length(min=2, max=30), Optional()])
    tel_number = StringField('Telefonní číslo', validators=[
        Optional(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ], render_kw={"type": "tel"})
    email =  StringField('Email', validators=[Optional(), Email()], render_kw={"type": "email"})
    reservation_id = StringField(label="ID rezervace", validators=[Optional()])
    submit = SubmitField(label="Najít rezervaci")

class RegistrationForm(FlaskForm):
    name = StringField(label="Jméno klienta", validators=[Length(min=2, max=30), DataRequired()])
    surname = StringField(label="Příjmení klienta", validators=[Length(min=2, max=30), DataRequired()])
    password = PasswordField(label="Heslo:", validators=[DataRequired()])
    tel_number = StringField('Telefonní číslo', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ], render_kw={"type": "tel"})
    email =  StringField('Email', validators=[DataRequired(), Email()], render_kw={"type": "email"})
    submit = SubmitField(label="Registrovat se")

class PasswordRenewalForm(FlaskForm):
    email =  StringField('Email', validators=[Optional(), Email()], render_kw={"type": "email"})
    submit = SubmitField(label="Změnit heslo")

class PasswordResetForm(FlaskForm):
    new_password = PasswordField(label="Heslo:", validators=[DataRequired()])
    submit = SubmitField(label="Změnit heslo")

class PersonalInformationFormUser(FlaskForm):
    name = StringField(label="Jméno klienta", validators=[Length(min=2, max=30), Optional()])
    surname = StringField(label="Příjmení klienta", validators=[Length(min=2, max=30), Optional()])
    old_password = PasswordField(label="Aktuální heslo:", validators=[Optional()])
    new_password = PasswordField(label="Nové heslo:", validators=[Optional()])
    tel_number = StringField('Telefonní číslo', validators=[
        Optional(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ], render_kw={"type": "tel"})
    email =  StringField('Email', validators=[Optional(), Email()], render_kw={"type": "email"})
    submit = SubmitField(label="Registrovat se")

class ChangeReservation(FlaskForm):
    name_validator = Regexp(r"^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ]+([-' ][a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ]+)*$",
    message="Jméno může obsahovat pouze písmena, pomlčky, apostrofy a mezery.")

    name = StringField(label="Jméno", validators=[Length(min=2, max=20), DataRequired(),name_validator])
    surname = StringField(label="Příjmení", validators=[Length(min=2, max=30), DataRequired(),name_validator])
    
    tel_number = StringField('Telefonní číslo', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Formát telefonního čísla: '+999999999'!")
    ], render_kw={"type": "tel"})
    email =  StringField('Email', validators=[DataRequired(), Email()], render_kw={"type": "email"})
    age_client = IntegerField('Věk', validators=[Optional(), NumberRange(min=5, max=120)])
    experience_client = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    
    student_client = BooleanField('Žák stejný jako klient', validators=[])
    more_students = BooleanField("Objednat více žáků", validators=[])

    name_client1 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])
    name_client2 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])
    name_client3 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])

    surname_client1 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])
    surname_client2 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])
    surname_client3 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])

    age_client1 = IntegerField('Věk', validators=[Optional(), NumberRange(min=5, max=120)])
    age_client2 = IntegerField('Věk', validators=[Optional(), NumberRange(min=5, max=120)])
    age_client3 = IntegerField('Věk', validators=[Optional(), NumberRange(min=5, max=120)])

    experience_client1 = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    experience_client2 = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    experience_client3 = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])

    lesson_type = SelectField('Výuka', choices=[('individual', 'Individuální'), ('group', 'Skupinová')], validators=[Optional()])
    lesson_length = SelectField("Délka výuky", choices=[("1hodina", "1 hodina"), ("2hodiny", "2 hodiny")])
    lesson_instructor_choices = SelectField("Instruktor", choices = [], validators=[Optional()])
    language_selection = SelectField("Jazyk", choices=[("czech", "čeština"), ("deutsch", "deutsch"), ("english", "english")])

    note = TextAreaField('Note', render_kw={"placeholder": "Napište nám zprávu."}, validators=[Optional(), Length(min=0, max=300)])

    lesson_length_hidden = HiddenField()
    lesson_instructor_choices_hidden = HiddenField()

    date = DateField('Datum rezervace', format='%Y-%m-%d', validators=[Optional()])
    time_reservation = SelectField("Čas rezervace", choices = [], validators=[Optional()])

    reservation_id = HiddenField()

    submit = SubmitField('Odeslat rezervaci')
