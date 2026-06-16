import sqlite3

conn = sqlite3.connect('demandas.db')
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS demandas")
cursor.execute("DROP TABLE IF EXISTS comentarios")
cursor.execute("DROP TABLE IF EXISTS solicitantes")
cursor.execute("DROP TABLE IF EXISTS api_keys")

cursor.execute('''
CREATE TABLE demandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    descricao TEXT,
    solicitante TEXT,
    data_criacao TEXT,
    nivel_prioridade TEXT,
    status TEXT,
    responsavel TEXT,
    data_conclusao TEXT,
    prazo TEXT
)
''')

cursor.execute('''
CREATE TABLE comentarios (
    id INTEGER,
    demanda_id INTEGER,
    comentario TEXT,
    autor TEXT,
    data TEXT
)
''')

cursor.execute('''
CREATE TABLE solicitantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    senha TEXT
)
''')

cursor.execute('''
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    data_criacao TEXT NOT NULL
)
''')

cursor.execute("INSERT INTO api_keys (nome, token, data_criacao) VALUES (?, ?, ?)", ('Chave de Teste', 'sgdi_mock_key_2026', '2026-06-15 08:00:00'))

# Mock data for Sprint Emergencial
mock_demandas = [
    ('Corrigir bug no login', 'Usuários não conseguem fazer login', 'João Silva', '2024-01-15 10:30:00', 'Alta', 'Aberta', 'Ana Dev', None, '2024-01-20 10:30:00'),
    ('Implementar relatório de vendas', 'Precisamos de um relatório mensal', 'Maria Santos', '2024-01-16 14:20:00', 'Média', 'Concluída', 'Carlos TI', '2024-01-22 10:00:00', '2024-01-25 14:20:00'),
    ('Melhorar performance', 'Sistema está lento', 'Pedro Costa', '2024-01-17 09:15:00', 'Baixa', 'Aberta', 'Roberto', None, '2024-01-30 09:15:00'),
    ('Adicionar filtros', 'Usuários querem filtrar demandas', 'Ana Lima', '2024-01-18 11:00:00', 'Média', 'Cancelada', 'Carlos TI', '2024-01-19 10:00:00', '2024-01-25 11:00:00'),
    
    # Surpresa: Demanda crítica atrasada
    ('Queda de servidor em Produção', 'Sistema totalmente fora do ar', 'Diretor', '2024-01-10 08:00:00', 'Crítica', 'Aberta', 'Ana Dev', None, '2024-01-11 08:00:00'),
    
    # Surpresa: Demanda crítica atrasada 2
    ('Vazamento de dados', 'Dados de clientes expostos', 'Segurança', '2024-01-05 10:00:00', 'Crítica', 'Aberta', 'Roberto', None, '2024-01-06 10:00:00'),
    
    # Surpresa: Demanda sem status
    ('Trocar cor do botão', 'Botão deve ser azul', 'Marketing', '2024-01-20 15:00:00', 'Baixa', None, 'Ana Dev', None, '2024-01-25 15:00:00'),
    
    # Surpresa: Datas inválidas
    ('Atualizar dependências', 'Atualizar pacotes NPM', 'Dev Team', 'data-invalida', 'Média', 'Concluída', 'Carlos TI', '2024-01-25 10:00:00', 'outra-data-invalida'),
    
    # Surpresa: Responsável deletado (Simulado como None/Sem responsável, ou ID que não existe na tabela, mas como é texto, usaremos None e fora do SLA)
    ('Configurar backup', 'Rotina de backup falhando', 'Infra', '2024-01-01 10:00:00', 'Alta', 'Aberta', None, None, '2024-01-05 10:00:00'),
]

cursor.executemany("""
INSERT INTO demandas (titulo, descricao, solicitante, data_criacao, nivel_prioridade, status, responsavel, data_conclusao, prazo)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", mock_demandas)

cursor.execute("INSERT INTO comentarios VALUES (1, 1, 'Vou investigar esse bug', 'Tech Team', '2024-01-15 11:00:00')")
cursor.execute("INSERT INTO comentarios VALUES (2, 1, 'Bug corrigido na branch develop', 'Desenvolvedor', '2024-01-15 16:30:00')")
cursor.execute("INSERT INTO comentarios VALUES (3, 99, 'Este comentário está órfão', 'Usuário', '2024-01-16 10:00:00')")

conn.commit()
conn.close()

print("Banco de dados atualizado para a Sprint Emergencial com sucesso!")
