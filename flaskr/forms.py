
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, NumberRange, Optional

class PersonalInformationForm(FlaskForm):
    name = StringField(label="Jméno", validators=[Length(min=2, max=30), DataRequired()])
    surname = StringField(label="Příjmení", validators=[Length(min=2, max=30), DataRequired()])
    tel_number = StringField('Telefonní číslo', validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ], render_kw={"type": "tel"})
    email =  StringField('Email', validators=[DataRequired(), Email()], render_kw={"type": "email"})
    age_client = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=120)])
    experience_client = SelectField('Choose Option', choices=[('value1', 'Option 1'), ('value2', 'Option 2'), ('value3', 'Option 3')], validators=[DataRequired()])
    
    name_client1 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])
    name_client2 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])
    name_client3 = StringField(label="Jméno", validators=[Length(min=2, max=30), Optional()])

    surname_client1 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])
    surname_client2 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])
    surname_client3 = StringField(label="Příjmení", validators=[Length(min=2, max=30), Optional()])

    age_client1 = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=120)])
    age_client2 = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=120)])
    age_client3 = IntegerField('Age', validators=[Optional(), NumberRange(min=0, max=120)])

    experience_client1 = SelectField('Choose Option', choices=[('value1', 'Option 1'), ('value2', 'Option 2'), ('value3', 'Option 3')], validators=[Optional()])
    experience_client2 = SelectField('Choose Option', choices=[('value1', 'Option 1'), ('value2', 'Option 2'), ('value3', 'Option 3')], validators=[Optional()])
    experience_client3 = SelectField('Choose Option', choices=[('value1', 'Option 1'), ('value2', 'Option 2'), ('value3', 'Option 3')], validators=[Optional()])

    lesson_type = SelectField('Lesson type', choices=[('value1', 'Option 1'), ('value2', 'Option 2'), ('value3', 'Option 3')], validators=[Optional()])
    note = TextAreaField('Note')

    submit = SubmitField('Submit')