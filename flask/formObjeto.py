
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ChaveForm(FlaskForm):
    nome = StringField('Nome do Objeto', validators=[DataRequired()])
    local = StringField('Onde foi achado', validators=[DataRequired()])
    entrega = StringField('Data de entrega', validators=[DataRequired()])
    enviar = SubmitField('CADASTRAR')