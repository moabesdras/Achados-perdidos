
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

class EmprestimoForm(FlaskForm):
    nome = StringField('Devolvido à: ', validators=[DataRequired()])
    chave = SelectField('Objeto', coerce=int)
    enviar = SubmitField('DEVOLVER')