
from sqlalchemy.orm import backref
from database import db

class Chave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=False, nullable=False)
    local = db.Column(db.String(50), unique=False, nullable=False)
    entrega = db.Column(db.String(10), unique=False, nullable=False)
    disponivel = db.Column(db.Boolean, default=False)
    emprestimos = db.relationship('Emprestimo', backref='chave', lazy=True)