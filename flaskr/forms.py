from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField, BooleanField, HiddenField, PasswordField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, NumberRange, Optional, ValidationError

class PersonalInformationForm(FlaskForm):
    name = StringField(label="Jméno", validators=[Length(min=2, max=30), DataRequired()])
    surname = StringField(label="Příjmení", validators=[Length(min=2, max=30), DataRequired()])
    tel_number = StringField('Telefonní číslo', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ], render_kw={"type": "tel"})
    email =  StringField('Email', validators=[DataRequired(), Email()], render_kw={"type": "email"})
    age_client = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=120)])
    experience_client = SelectField('Zkušenosti', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    
    student_client = BooleanField('Žák stejný jako klient', validators=[])
    more_students = BooleanField("Objednat více žáků", validators=[])

    name_client1 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])
    name_client2 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])
    name_client3 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])

    surname_client1 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])
    surname_client2 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])
    surname_client3 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])

    age_client1 = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=120)])
    age_client2 = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=120)])
    age_client3 = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=120)])

    experience_client1 = SelectField('Choose Option', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    experience_client2 = SelectField('Choose Option', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])
    experience_client3 = SelectField('Choose Option', choices=[('value1', 'Začátečník'), ('value2', 'Středně pokročilý'), ('value3', 'Pokročilý')], validators=[Optional()])

    lesson_type = SelectField('Typ výuky', choices=[('individual', 'Individuální'), ('group', 'Skupinová')], validators=[Optional()])
    lesson_length = SelectField("Délka výuky", choices=[("1hodina", "1 hodina"), ("2hodiny", "2 hodiny")])
    lesson_instructor_choices = SelectField("Instruktor", choices = [])
    language_selection = SelectField("Jazyk", choices=[("czech", "čeština"), ("deutsch", "deutsch"), ("english", "english")])

    note = TextAreaField('Note', render_kw={"placeholder": "Napište nám zprávu"})

    date = HiddenField("date")
    time = HiddenField("time")

    submit = SubmitField('Submit')

class ReservationInformationForm(FlaskForm):
    reservation_id = IntegerField("Reservation ID", validators=[DataRequired()])
    submit = SubmitField('Submit')

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
    time_start = TimeField("Čas začátku", validators=[DataRequired(), validate_on_the_hour])
    lesson_type = SelectField('Typ lekce', choices=[('ind', 'Individuální'), ('group', 'Skupinová')], validators=[Optional()])
    capacity = IntegerField('Kapacita', validators=[Optional(), NumberRange(min=0, max=20)])
    lesson_instructor_choices = SelectField("Instruktor", choices = [])
    submit = SubmitField(label="Vložit hodinu")

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
