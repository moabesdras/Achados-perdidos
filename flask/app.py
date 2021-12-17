
from flask import Flask
from waitress import serve
from flask import render_template
from flask import request, url_for, redirect, flash, make_response
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
import logging
import os
import datetime
from formObjeto import ChaveForm
from formUsuario import UsuarioForm
from formDevolver import EmprestimoForm
from flask_session import Session
from flask import session
from formLogin import LoginForm
import hashlib

app = Flask(__name__)
bootstrap = Bootstrap(app)
CSRFProtect(app)
CSV_DIR = '/flask/'

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['WTF_CSRF_SSL_STRICT'] = False
Session(app)

logging.basicConfig(filename=CSV_DIR + 'app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + CSV_DIR + 'bd.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from database import db
db.init_app(app)

from Usuarios import Usuario
from Objetos import Chave
from Devolucao import Emprestimo

@app.before_first_request

def inicializar_bd():
    #db.drop_all()
    db.create_all()

@app.route('/')

def root():
    if session.get('autenticado', False)==False:
        return (redirect(url_for('login')))
    return (render_template('index.html'))
        
@app.route('/objetos/cadastrar', methods=['POST', 'GET'])

def cadastrar_objeto():
    if session.get('autenticado', False) == False:
        return (redirect(url_for('login')))
    form = ChaveForm()

    if form.validate_on_submit():
        # Processamento dos dados recebidos
        nome = request.form['nome']
        local = request.form['local']
        entrega = request.form['entrega']
        novoObjeto = Chave(nome=nome, local=local, entrega=entrega)
        db.session.add(novoObjeto)
        db.session.commit()
        flash('Objeto cadastrado com sucesso!')
        return(redirect(url_for('root')))
    return (render_template('form.html', form=form, action=url_for('cadastrar_objeto')))

@app.route('/objetos/listar')

def listar_objetos():
    chaves = Chave.query.order_by(Chave.id.desc()).all()
    return(render_template('objetos.html', chaves=chaves))

@app.route('/usuario/listar')

def listar_usuarios():
    if session.get('autenticado', False) == False:
        return (redirect(url_for('login')))
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return(render_template('usuarios.html', usuarios=usuarios))

@app.route('/usuario/cadastrar', methods=['POST', 'GET'])

def cadastrar_usuario():
    if session.get('autenticado', False) == False:
        return (redirect(url_for('login')))
    form = UsuarioForm()

    if form.validate_on_submit():
        # Processamento dos dados recebidos
        nome = request.form['nome']
        username = request.form['username']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']
        senhahash = hashlib.sha1(senha.encode('utf8')).hexdigest()

        novoUsuario = Usuario(nome=nome, username=username, email=email, telefone=telefone, senha=senhahash)
        db.session.add(novoUsuario)
        db.session.commit()

        flash(u'Usuário cadastrado com sucesso!')
        return(redirect(url_for('root')))
    return (render_template('form.html', form=form, action=url_for('cadastrar_usuario')))

@app.route('/objetos/devolver', methods=['POST', 'GET'])

def devolver_objeto():
    if session.get('autenticado', False) == False:
        return (redirect(url_for('login')))

    form = EmprestimoForm()
    objetos = Chave.query.filter(Chave.disponivel==False).order_by(Chave.nome).all()
    form.chave.choices = [(c.id,c.nome) for c in objetos]

    if form.validate_on_submit():
        # Registro da devolução
        nome = request.form['nome']
        objeto = int(request.form['chave'])
        novaDevolucao = Emprestimo(id_usuario=1, id_chave=objeto, nome_pessoa=nome)
        objetoDevolvido = Chave.query.get(objeto)
        objetoDevolvido.disponivel = True
        db.session.add(novaDevolucao)
        db.session.commit()
        return(redirect(url_for('root')))

    return(render_template('form.html', form=form,action=url_for('devolver_objeto')))

@app.route('/objetos/listar_devolucoes')

def listar_devolucoes():
    emprestimos = Emprestimo.query.order_by(Emprestimo.data_emprestimo.desc()).all()
    return(render_template('devolucoes.html', emprestimos=emprestimos))

@app.route('/devolucoes/remover/<id_devolucao>', methods=['GET', 'POST'])

def remover_devolucao(id_devolucao):
    if session.get('autenticado', False) == False:
        return (redirect(url_for('login')))

    id_devolucao = int(id_devolucao)
    devolucao = Emprestimo.query.get(id_devolucao)
    id_chave = devolucao.id_chave
    objeto = Chave.query.get(id_chave)
    objeto.disponivel = True
    db.session.delete(devolucao)
    db.session.commit()
    return (redirect(url_for('root')))

@app.route('/usuario/login', methods=['POST', 'GET'])

def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Processamento dos dados recebidos
        usuario = request.form['usuario']
        senha = request.form['senha']
        senhahash = hashlib.sha1(senha.encode('utf8')).hexdigest()

        # Verificar se existe alguma linha na tabela usuários com o login e senha recebidos
        linha = Usuario.query.filter(Usuario.username==usuario, Usuario.senha==senhahash).all()

        # Troca o status da sessão para "autenticado"
        if (len(linha)>0):
            session['autenticado'] = True
            session['usuario'] = linha[0].id
            flash(usuario + u' logou com sucesso!', 'success')
            resposta = make_response(redirect(url_for('root')))
            return(resposta)

        # Usuário ou senha não conferem
        else:
            flash(u'Usuário e/ou senha não conferem!', 'error')
            resposta = make_response(redirect(url_for('login')))
            return(resposta)

    return (render_template('form.html', form=form, action=url_for('login')))

@app.route('/usuario/logout', methods=['POST', 'GET'])

def logout():
    session.clear()
    return(redirect(url_for('login')))

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80, url_prefix='/app')
