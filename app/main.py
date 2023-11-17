from flask import Flask, jsonify, request
from flask_pydantic_spec import FlaskPydanticSpec
from sqlalchemy import create_engine, Column, Integer, String, text, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.decl_api import declarative_base
from datetime import datetime
import configparser

# Criar um objeto ConfigParser
config = configparser.ConfigParser()

# Ler o arquivo
config.read('config.ini')


# Acessar os valores
porta = config['BancoDeDados']['porta']
usuario = config['BancoDeDados']['usuario']
senha = config['BancoDeDados']['senha']
banco = config['BancoDeDados']['banco']

# # Construir a string de conexão
db_url = f"postgresql+psycopg2://{usuario}:{senha}@db:{porta}/{banco}"


# Criar uma conexão com o banco de dados
engine = create_engine(db_url)

with open('model.sql', 'r') as arquivo_sql:
    comandos_sql = arquivo_sql.read()

# Executar os comandos SQL no banco de dados
with engine.connect() as connection:
    trans = connection.begin()  # Iniciar uma transação
    try:
        connection.execute(text(comandos_sql))  # Executar os comandos SQL
        trans.commit()  # Confirmar a transação se executou com sucesso
        print("Comandos SQL executados com sucesso!")
    except Exception as e:
        trans.rollback()  # Reverter a transação se ocorreu algum erro
        print(f"Erro ao executar os comandos SQL: {e}")




app = Flask(__name__)
spec = FlaskPydanticSpec('Flask',title='Api Clima Bom')
spec.register(app)



engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()

Base.metadata.create_all(engine)


class Sala(Base):
    __tablename__ = 'salas'
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    andar = Column(String)
    bloco = Column(String)
    ip = Column(String)

class Equipamento(Base):
    __tablename__ = 'equipamento'
    id = Column(Integer, primary_key=True)
    modelo = Column(String)
    descricao = Column(String)
    marca = Column(String)
    id_protocolo = Column(Integer)
    comandos = relationship('Comandos', back_populates='equipamento')
    logs = relationship('Logs', back_populates='equipamento')
    usuarios = relationship('Usuario', back_populates='equipamento')
    relacoes = relationship('Relacao', back_populates='equipamento')

class Comandos(Base):
    __tablename__ = 'comandos'
    id = Column(Integer, primary_key=True)
    comando = Column(String)
    descricao = Column(String)
    id_protocolo = Column(Integer, ForeignKey('equipamento.id'))

    equipamento = relationship('Equipamento', back_populates='comandos')

class Agenda(Base):
    __tablename__ = 'agenda'
    id = Column(Integer, primary_key=True)
    disciplina = Column(String)
    datas = Column(TIMESTAMP)
    hora_inicio = Column(TIMESTAMP)
    hora_fim = Column(TIMESTAMP)
    id_sala = Column(Integer, ForeignKey('salas.id'))

class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    datas = Column(TIMESTAMP)
    hora = Column(TIMESTAMP)
    equipamento = Column(String)
    id_equipamento = Column(Integer, ForeignKey('equipamento.id'))
    usuario = Column(String)
    sala = Column(String)
    acao = Column(String)

    equipamento = relationship('Equipamento', back_populates='logs')

class Permissoes(Base):
    __tablename__ = 'permissoes'
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    acesso = Column(String)

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String)
    senha = Column(String)
    permissao = Column(String)
    id_permissoes = Column(Integer, ForeignKey('permissoes.id'))
    id_logs = Column(Integer, ForeignKey('logs.id'))

    equipamento = relationship('Equipamento', back_populates='usuarios')

class Relacao(Base):
    __tablename__ = 'relacao'
    id = Column(Integer, primary_key=True)
    id_sala = Column(Integer, ForeignKey('salas.id'))
    id_equipamento = Column(Integer, ForeignKey('equipamento.id'))

    equipamento = relationship('Equipamento', back_populates='relacoes')

class Protocolo(Base):
    __tablename__ = 'protocolo'
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    id_comando = Column(Integer, ForeignKey('comandos.id'))
# Rota para buscar todos os registros de uma tabela

###### SALAS #######

@app.route('/salas', methods=['GET'])
def get_salas():
    Session = sessionmaker(bind=engine)
    Session = Session()
    salas = Session.query(Sala).all()
    Session.close()
    return jsonify([s.__dict__ for s in salas])

@app.route('/salas', methods=['POST'])
def create_sala():
    data = request.get_json()
    nova_sala = Sala(**data)
    Session = Sessionmaker(bind=engine)
    Session = Session()
    Session.add(nova_sala)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Sala criada com sucesso!'}), 201

@app.route('/salas/<int:id>', methods=['GET'])
def get_sala(id):
    Session = Sessionmaker(bind=engine)
    Session = Session()
    sala = Session.query(Sala).filter_by(id=id).first()
    Session.close()
    return jsonify(sala.__dict__)

@app.route('/salas/<int:id>', methods=['PUT'])
def update_sala(id):
    data = request.get_json()
    Session = Sessionmaker(bind=engine)
    Session = Session()
    sala = Session.query(Sala).filter_by(id=id).first()
    for key, value in data.items():
        setattr(sala, key, value)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Sala atualizada com sucesso!'})


@app.route('/salas/<int:id>', methods=['DELETE'])
def delete_sala(id):
    Session = Sessionmaker(bind=engine)
    Session = Session()
    sala = Session.query(Sala).filter_by(id=id).first()
    Session.delete(sala)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Sala excluída com sucesso!'})

####### EQUIPAMENTO #######

@app.route('/equipamentos', methods=['GET'])
def get_equipamentos():
    Session = Sessionmaker(bind=engine)
    Session = Session()
    equipamentos = Session.query(Equipamento).all()
    Session.close()
    return jsonify([e.__dict__ for e in equipamentos])

@app.route('/equipamentos', methods=['POST'])
def create_equipamento():
    data = request.get_json()
    novo_equipamento = Equipamento(**data) 
    Session = Sessionmaker(bind=engine)
    Session = Session()
    Session.add(novo_equipamento)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Equipamento criado com sucesso!'}), 201

@app.route('/equipamentos/<int:id>', methods=['GET'])
def get_equipamento(id):
    Session = Sessionmaker(bind=engine)
    Session = Session()
    equipamento = Session.query(Equipamento).filter_by(id=id).first()
    Session.close()
    return jsonify(equipamento.__dict__)

@app.route('/equipamentos/<int:id>', methods=['PUT'])
def update_equipamento(id):
    data = request.get_json()
    Session = Sessionmaker(bind=engine)
    Session = Session()
    equipamento = Session.query(Equipamento).filter_by(id=id).first()
    for key, value in data.items():
        setattr(equipamento, key, value)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Equipamento atualizado com sucesso!'})

@app.route('/equipamentos/<int:id>', methods=['DELETE'])
def delete_equipamento(id):
    Session = Sessionmaker(bind=engine)
    Session = Session()
    equipamento = Session.query(Equipamento).filter_by(id=id).first()
    Session.delete(equipamento)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Equipamento excluído com sucesso!'})

########### COMANDOS #####################

@app.route('/comandos', methods=['GET'])
def get_comandos():
    comandos = Comandos.query.all()
    output = []
    for comando in comandos:
        comando_data = {}
        comando_data['id'] = comando.id
        comando_data['comando'] = comando.comando
        comando_data['descricao'] = comando.descricao
        comando_data['id_protocolo'] = comando.id_protocolo
        output.append(comando_data)
    return jsonify({'comandos': output})

@app.route('/comandos/<id>', methods=['GET'])
def get_comando(id):
    comando = Comandos.query.get(id)
    if not comando:
        return jsonify({'message': 'Comando não encontrado'})
    comando_data = {}
    comando_data['id'] = comando.id
    comando_data['comando'] = comando.comando
    comando_data['descricao'] = comando.descricao
    comando_data['id_protocolo'] = comando.id_protocolo
    return jsonify({'comando': comando_data})

@app.route('/comandos', methods=['POST'])
def add_comando():
    data = request.get_json()
    new_comando = Comandos(comando=data['comando'], descricao=data['descricao'], id_protocolo=data['id_protocolo'])
    Session.add(new_comando)
    Session.commit()
    return jsonify({'message': 'Comando criado com sucesso'})

@app.route('/comandos/<id>', methods=['PUT'])
def update_comando(id):
    comando = Comandos.query.get(id)
    if not comando:
        return jsonify({'message': 'Comando não encontrado'})
    data = request.get_json()
    comando.comando = data['comando']
    comando.descricao = data['descricao']
    comando.id_protocolo = data['id_protocolo']
    Session.commit()
    return jsonify({'message': 'Comando atualizado com sucesso'})

@app.route('/comandos/<id>', methods=['DELETE'])
def delete_comando(id):
    comando = Comandos.query.get(id)
    if not comando:
        return jsonify({'message': 'Comando não encontrado'})
    Session.delete(comando)
    Session.commit()
    return jsonify({'message': 'Comando excluído com sucesso'})


########## AGENDA #############

@app.route('/agenda', methods=['GET'])
def get_agenda():
    agenda = Agenda.query.all()
    output = []
    for item in agenda:
        agenda_data = {
            'id': item.id,
            'disciplina': item.disciplina,
            'datas': item.datas.strftime("%Y-%m-%d"),
            'hora_inicio': item.hora_inicio.strftime("%H:%M:%S"),
            'hora_fim': item.hora_fim.strftime("%H:%M:%S"),
            'id_sala': item.id_sala
        }
        output.append(agenda_data)
    return jsonify({'agenda': output})

@app.route('/agenda/<id>', methods=['GET'])
def get_agenda_by_id(id):
    item = Agenda.query.get(id)
    if not item:
        return jsonify({'message': 'Item da agenda não encontrado'})
    
    agenda_data = {
        'id': item.id,
        'disciplina': item.disciplina,
        'datas': item.datas.strftime("%Y-%m-%d"),
        'hora_inicio': item.hora_inicio.strftime("%H:%M:%S"),
        'hora_fim': item.hora_fim.strftime("%H:%M:%S"),
        'id_sala': item.id_sala
    }
    return jsonify({'agenda': agenda_data})

@app.route('/agenda', methods=['POST'])
def add_agenda():
    data = request.get_json()
    new_item = Agenda(
        disciplina=data['disciplina'],
        datas=data['datas'],
        hora_inicio=data['hora_inicio'],
        hora_fim=data['hora_fim'],
        id_sala=data['id_sala']
    )
    Session.add(new_item)
    Session.commit()
    return jsonify({'message': 'Item da agenda criado com sucesso'})

@app.route('/agenda/<id>', methods=['PUT'])
def update_agenda(id):
    item = Agenda.query.get(id)
    if not item:
        return jsonify({'message': 'Item da agenda não encontrado'})
    data = request.get_json()
    item.disciplina = data['disciplina']
    item.datas = data['datas']
    item.hora_inicio = data['hora_inicio']
    item.hora_fim = data['hora_fim']
    item.id_sala = data['id_sala']
    Session.commit()
    return jsonify({'message': 'Item da agenda atualizado com sucesso'})

@app.route('/agenda/<id>', methods=['DELETE'])
def delete_agenda(id):
    item = Agenda.query.get(id)
    if not item:
        return jsonify({'message': 'Item da agenda não encontrado'})
    Session.delete(item)
    Session.commit()
    return jsonify({'message': 'Item da agenda excluído com sucesso'})



############## LOGS ##################

@app.route('/logs', methods=['GET'])
def get_logs():
    Session = Sessionmaker(bind=engine)
    Session = Session()
    logs = Session.query(Logs).all()
    Session.close()
    return jsonify([l.__dict__ for l in logs])

@app.route('/logs', methods=['POST'])
def create_log():
    data = request.get_json()
    novo_log = Logs(**data)
    Session = Sessionmaker(bind=engine)
    Session = Session()
    Session.add(novo_log)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Log criado com sucesso!'}), 201

@app.route('/logs/<int:id>', methods=['GET'])
def get_log_by_id(id):
    Session = Sessionmaker(bind=engine)
    Session = Session()
    log = Session.query(Logs).filter_by(id=id).first()
    Session.close()
    return jsonify(log.__dict__)

@app.route('/logs/<int:id>', methods=['PUT'])
def update_log(id):
    data = request.get_json()
    Session = Sessionmaker(bind=engine)
    Session = Session()
    log = Session.query(Logs).filter_by(id=id).first()
    for key, value in data.items():
        setattr(log, key, value)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Log atualizado com sucesso!'})

@app.route('/logs/<int:id>', methods=['DELETE'])
def delete_log(id):
    Session = Sessionmaker(bind=engine)
    Session = Session()
    log = Session.query(Logs).filter_by(id=id).first()
    Session.delete(log)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Log excluído com sucesso!'})


######## PERMISSOES ##########


@app.route('/permissoes', methods=['GET'])
def get_permissoes():
    Session = Sessionmaker(bind=engine)
    Session = Session()
    permissoes = Session.query(Permissoes).all()
    Session.close()
    return jsonify([p.__dict__ for p in permissoes])

@app.route('/permissoes', methods=['POST'])
def create_permissao():
    data = request.get_json()
    nova_permissao = Permissoes(**data)
    Session = Sessionmaker(bind=engine)
    Session = Session()
    Session.add(nova_permissao)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Permissão criada com sucesso!'}), 201

@app.route('/permissoes/<int:id>', methods=['GET'])
def get_permissao_by_id(id):
    Session = Sessionmaker(bind=engine)
    Session = Session()
    permissao = Session.query(Permissoes).filter_by(id=id).first()
    Session.close()
    return jsonify(permissao.__dict__)

@app.route('/permissoes/<int:id>', methods=['PUT'])
def update_permissao(id):
    data = request.get_json()
    Session = Sessionmaker(bind=engine)
    Session = Session()
    permissao = Session.query(Permissoes).filter_by(id=id).first()
    for key, value in data.items():
        setattr(permissao, key, value)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Permissão atualizada com sucesso!'})

@app.route('/permissoes/<int:id>', methods=['DELETE'])
def delete_permissao(id):
    Session = Sessionmaker(bind=engine)
    Session = Session()
    permissao = Session.query(Permissoes).filter_by(id=id).first()
    Session.delete(permissao)
    Session.commit()
    Session.close()
    return jsonify({'message': 'Permissão excluída com sucesso!'})


######## USUARIO ##########


@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()
    output = []
    for usuario in usuarios:
        usuario_data = {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'senha': usuario.senha,
            'permissao': usuario.permissao,
            'id_permissoes': usuario.id_permissoes,
            'id_logs': usuario.id_logs
        }
        output.append(usuario_data)
    return jsonify({'usuarios': output})

@app.route('/usuarios/<id>', methods=['GET'])
def get_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'})
    usuario_data = {
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email,
        'senha': usuario.senha,
        'permissao': usuario.permissao,
        'id_permissoes': usuario.id_permissoes,
        'id_logs': usuario.id_logs
    }
    return jsonify({'usuario': usuario_data})

@app.route('/usuarios', methods=['POST'])
def add_usuario():
    data = request.get_json()
    new_usuario = Usuario(
        nome=data['nome'],
        email=data['email'],
        senha=data['senha'],
        permissao=data['permissao'],
        id_permissoes=data['id_permissoes'],
        id_logs=data['id_logs']
    )
    Session.add(new_usuario)
    Session.commit()
    return jsonify({'message': 'Usuário criado com sucesso'})

@app.route('/usuarios/<id>', methods=['PUT'])
def update_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'})
    data = request.get_json()
    usuario.nome = data['nome']
    usuario.email = data['email']
    usuario.senha = data['senha']
    usuario.permissao = data['permissao']
    usuario.id_permissoes = data['id_permissoes']
    usuario.id_logs = data['id_logs']
    Session.commit()
    return jsonify({'message': 'Usuário atualizado com sucesso'})

@app.route('/usuarios/<id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'})
    Session.delete(usuario)
    Session.commit()
    return jsonify({'message': 'Usuário excluído com sucesso'})


############## RELAÇÃO ###############

@app.route('/relacao', methods=['GET'])
def get_relacao():
    relacao = Relacao.query.all()
    output = []
    for item in relacao:
        relacao_data = {
            'id': item.id,
            'id_sala': item.id_sala,
            'id_equipamento': item.id_equipamento
        }
        output.append(relacao_data)
    return jsonify({'relacao': output})

@app.route('/relacao/<id>', methods=['GET'])
def get_relacao_by_id(id):
    item = Relacao.query.get(id)
    if not item:
        return jsonify({'message': 'Relação não encontrada'})
    
    relacao_data = {
        'id': item.id,
        'id_sala': item.id_sala,
        'id_equipamento': item.id_equipamento
    }
    return jsonify({'relacao': relacao_data})

@app.route('/relacao', methods=['POST'])
def add_relacao():
    data = request.get_json()
    new_item = Relacao(
        id_sala=data['id_sala'],
        id_equipamento=data['id_equipamento']
    )
    Session.add(new_item)
    Session.commit()
    return jsonify({'message': 'Relação criada com sucesso'})

@app.route('/relacao/<id>', methods=['PUT'])
def update_relacao(id):
    item = Relacao.query.get(id)
    if not item:
        return jsonify({'message': 'Relação não encontrada'})
    data = request.get_json()
    item.id_sala = data['id_sala']
    item.id_equipamento = data['id_equipamento']
    Session.commit()
    return jsonify({'message': 'Relação atualizada com sucesso'})

@app.route('/relacao/<id>', methods=['DELETE'])
def delete_relacao(id):
    item = Relacao.query.get(id)
    if not item:
        return jsonify({'message': 'Relação não encontrada'})
    Session.delete(item)
    Session.commit()
    return jsonify({'message': 'Relação excluída com sucesso'})


##################### PROTOCOLO ######################


@app.route('/protocolo', methods=['GET'])
def get_protocolo():
    protocolos = Protocolo.query.all()
    output = []
    for protocolo in protocolos:
        protocolo_data = {
            'id': protocolo.id,
            'descricao': protocolo.descricao,
            'id_comando': protocolo.id_comando
        }
        output.append(protocolo_data)
    return jsonify({'protocolos': output})

@app.route('/protocolo/<id>', methods=['GET'])
def get_protocolo_by_id(id):
    protocolo = Protocolo.query.get(id)
    if not protocolo:
        return jsonify({'message': 'Protocolo não encontrado'})
    
    protocolo_data = {
        'id': protocolo.id,
        'descricao': protocolo.descricao,
        'id_comando': protocolo.id_comando
    }
    return jsonify({'protocolo': protocolo_data})

@app.route('/protocolo', methods=['POST'])
def add_protocolo():
    data = request.get_json()
    new_protocolo = Protocolo(
        descricao=data['descricao'],
        id_comando=data['id_comando']
    )
    Session.add(new_protocolo)
    Session.commit()
    return jsonify({'message': 'Protocolo criado com sucesso'})

@app.route('/protocolo/<id>', methods=['PUT'])
def update_protocolo(id):
    protocolo = Protocolo.query.get(id)
    if not protocolo:
        return jsonify({'message': 'Protocolo não encontrado'})
    data = request.get_json()
    protocolo.descricao = data['descricao']
    protocolo.id_comando = data['id_comando']
    Session.commit()
    return jsonify({'message': 'Protocolo atualizado com sucesso'})

@app.route('/protocolo/<id>', methods=['DELETE'])
def delete_protocolo(id):
    protocolo = Protocolo.query.get(id)
    if not protocolo:
        return jsonify({'message': 'Protocolo não encontrado'})
    Session.delete(protocolo)
    Session.commit()
    return jsonify({'message': 'Protocolo excluído com sucesso'})





if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0')
