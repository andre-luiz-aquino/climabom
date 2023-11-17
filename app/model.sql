CREATE TABLE IF NOT EXISTS salas (
    id SERIAL PRIMARY KEY,
    descricao TEXT,
    andar TEXT,
    bloco TEXT,
    ip TEXT
);

CREATE TABLE IF NOT EXISTS equipamento (
    id SERIAL PRIMARY KEY,
    modelo TEXT,
    descricao TEXT,
    marca TEXT,
    id_protocolo INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS comandos (
    id SERIAL PRIMARY KEY,
    comando TEXT,
    descricao TEXT,
    id_protocolo INTEGER,
    FOREIGN KEY (id_protocolo) REFERENCES equipamento(id_protocolo)
);

CREATE TABLE IF NOT EXISTS agenda (
    id SERIAL PRIMARY KEY,
    disciplina TEXT,
    datas TIMESTAMP,
    hora_inicio TIMESTAMP,
    hora_fim TIMESTAMP,
    id_sala INTEGER,
    FOREIGN KEY (id_sala) REFERENCES salas(id)
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    datas TIMESTAMP,
    hora TIMESTAMP,
    equipamento TEXT,
    id_equipamento INTEGER,
    usuario TEXT,
    sala TEXT,
    acao TEXT,
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id)
);

CREATE TABLE IF NOT EXISTS permissoes (
    id SERIAL PRIMARY KEY,
    descricao TEXT,
    acesso TEXT
);

CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    nome TEXT,
    email TEXT,
    senha TEXT,
    permissao TEXT,
    id_permissoes INTEGER,
    id_logs INTEGER,
    FOREIGN KEY (id_permissoes) REFERENCES permissoes(id),
    FOREIGN KEY (id_logs) REFERENCES logs(id)
);

CREATE TABLE IF NOT EXISTS relacao (
    id SERIAL PRIMARY KEY,
    id_sala INTEGER,
    id_equipamento INTEGER,
    FOREIGN KEY (id_sala) REFERENCES salas(id),
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id)
);

CREATE TABLE IF NOT EXISTS protocolo(
    id SERIAL PRIMARY KEY,
    descricao TEXT,
    id_comando INTEGER,
    FOREIGN KEY (id_comando) REFERENCES comandos(id)
);
