import sqlite3


conn = sqlite3.connect('demandas.db')
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS demandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    descricao TEXT,
    solicitante TEXT,
    data_criacao TEXT,
    nivel_prioridade TEXT
)
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER,
    demanda_id INTEGER,
    comentario TEXT,
    autor TEXT,
    data TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS solicitantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL
)
''')

cursor.execute("DELETE FROM demandas")
cursor.execute("DELETE FROM comentarios")
cursor.execute("DELETE FROM solicitantes")


cursor.execute("INSERT INTO solicitantes (nome, senha) VALUES ('Admin', 'admin')")


cursor.execute("""
INSERT INTO demandas (titulo, descricao, solicitante, data_criacao, nivel_prioridade)
VALUES (?, ?, ?, ?, ?)
""", ('Corrigir bug no login', 'Usuários não conseguem fazer login', 'João Silva', '2024-01-15 10:30:00', 'Alta'))

cursor.execute("""
INSERT INTO demandas (titulo, descricao, solicitante, data_criacao, nivel_prioridade)
VALUES (?, ?, ?, ?, ?)
""", ('Implementar relatório de vendas', 'Precisamos de um relatório mensal', 'Maria Santos', '2024-01-16 14:20:00', 'Média '))

cursor.execute("""
INSERT INTO demandas (titulo, descricao, solicitante, data_criacao, nivel_prioridade)
VALUES (?, ?, ?, ?, ?)
""", ('Melhorar performance', 'Sistema está lento', 'Pedro Costa', '2024-01-17 09:15:00', 'Baixa'))

cursor.execute("""
INSERT INTO demandas (titulo, descricao, solicitante, data_criacao, nivel_prioridade)
VALUES (?, ?, ?, ?, ?)
""", ('Adicionar filtros', 'Usuários querem filtrar demandas', 'Ana Lima', '2024-01-18 11:00:00', 'Média'))

cursor.execute("INSERT INTO comentarios VALUES (1, 1, 'Vou investigar esse bug', 'Tech Team', '2024-01-15 11:00:00')")
cursor.execute("INSERT INTO comentarios VALUES (2, 1, 'Bug corrigido na branch develop', 'Desenvolvedor', '2024-01-15 16:30:00')")
cursor.execute("INSERT INTO comentarios VALUES (3, 99, 'Este comentário está órfão', 'Usuário', '2024-01-16 10:00:00')")

conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")
