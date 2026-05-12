from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
import sqlite3
from datetime import datetime
import csv
import io

app = Flask(__name__)
app.secret_key = '123456'


def get_db():
    conn = sqlite3.connect('demandas.db')
    conn.row_factory = sqlite3.Row
    return conn

def atualizar_prioridades_atrasadas():
    conn = get_db()
    cursor = conn.cursor()
    demandas = cursor.execute("SELECT id, prazo FROM demandas WHERE nivel_prioridade = 'Alta' AND status NOT IN ('Concluída', 'Cancelada') AND prazo IS NOT NULL").fetchall()
    
    agora = datetime.now()
    ids_to_update = []
    
    for d in demandas:
        try:
            prazo_dt = datetime.strptime(d['prazo'], '%Y-%m-%d %H:%M:%S')
            if agora > prazo_dt:
                ids_to_update.append(d['id'])
        except ValueError:
            pass
            
    if ids_to_update:
        placeholders = ','.join(['?'] * len(ids_to_update))
        cursor.execute(f"UPDATE demandas SET nivel_prioridade = 'Crítica' WHERE id IN ({placeholders})", ids_to_update)
        conn.commit()
        
    conn.close()


@app.route('/')
def index():
    atualizar_prioridades_atrasadas()
    # pega múltiplas prioridades selecionadas (checkbox)
    prioridades = request.args.getlist('prioridade[]')

    # pega tipo de ordenação (asc ou desc)
    ordem = request.args.get('ordem', 'asc')

    # normaliza (evita erro com Alta / alta / ALTA)
    prioridades = [p.lower() for p in prioridades]

    conn = get_db()
    cursor = conn.cursor()

    # query base
    query = "SELECT * FROM demandas"
    params = []

    # filtro por múltiplas prioridades
    if prioridades:
        placeholders = ','.join(['?'] * len(prioridades))
        query += f' WHERE LOWER(nivel_prioridade) IN ({placeholders})'
        params.extend(prioridades)

    # define ordem correta (Crítica → Alta → Média → Baixa)
    order_clause = '''
        CASE 
            WHEN LOWER(nivel_prioridade) IN ("crítica", "critica") THEN 1
            WHEN LOWER(nivel_prioridade) = "alta" THEN 2
            WHEN LOWER(nivel_prioridade) IN ("média","media") THEN 3
            WHEN LOWER(nivel_prioridade) = "baixa" THEN 4
            ELSE 5
        END
    '''

    # aplica ordenação
    if ordem == 'desc':
        query += f' ORDER BY {order_clause} DESC, data_criacao DESC'
    else:
        query += f' ORDER BY {order_clause} ASC, data_criacao DESC'

    # executa a query
    demandas = cursor.execute(query, params).fetchall()

    conn.close()

    return render_template(
        'index.html',
        demandas=demandas,
        prioridades_selecionadas=request.args.getlist('prioridade[]'),
        ordem=ordem
    )


@app.route('/nova_demanda', methods=['GET', 'POST'])
def nova_demanda():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante = request.form['solicitante']
        prioridade = request.form.get('prioridade')

        # padroniza prioridade
        if prioridade:
            prioridade = prioridade.capitalize()

        status = request.form.get('status', 'Aberta')
        responsavel = request.form.get('responsavel') or None
        prazo = request.form.get('prazo') or None
        if prazo:
            prazo += " 23:59:59" # Adicionar hora no final do dia se vier só a data
            
        data_conclusao = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status == 'Concluída' else None

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            '''
            INSERT INTO demandas (titulo, descricao, solicitante, data_criacao, nivel_prioridade, status, responsavel, prazo, data_conclusao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (titulo, descricao, solicitante, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), prioridade, status, responsavel, prazo, data_conclusao)
        )

        conn.commit()
        conn.close()

        flash('Demanda salva!')
        return redirect(url_for('index'))

    conn = get_db()
    solicitantes = conn.cursor().execute('SELECT nome FROM solicitantes ORDER BY nome').fetchall()
    conn.close()
    return render_template('nova_demanda.html', solicitantes=solicitantes)


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante = request.form['solicitante']
        prioridade = request.form.get('prioridade')

        if prioridade:
            prioridade = prioridade.capitalize()

        status = request.form.get('status', 'Aberta')
        responsavel = request.form.get('responsavel') or None
        prazo = request.form.get('prazo') or None
        if prazo and len(prazo) <= 10:
            prazo += " 23:59:59"
            
        data_conclusao = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status == 'Concluída' else None

        cursor.execute(
            '''
            UPDATE demandas 
            SET titulo=?, descricao=?, solicitante=?, nivel_prioridade=?, status=?, responsavel=?, prazo=?, data_conclusao=?
            WHERE id=?
            ''',
            (titulo, descricao, solicitante, prioridade, status, responsavel, prazo, data_conclusao, id)
        )

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    demanda = cursor.execute(
        'SELECT * FROM demandas WHERE id=?', (id,)
    ).fetchone()

    solicitantes = cursor.execute('SELECT nome FROM solicitantes ORDER BY nome').fetchall()

    conn.close()
    return render_template('editar.html', demanda=demanda, solicitantes=solicitantes)


@app.route('/deletar/<int:id>')
def deletar(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM demandas WHERE id=?', (id,))
    conn.commit()
    conn.close()

    flash('Deletado!')
    return redirect(url_for('index'))


@app.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_db()
    cursor = conn.cursor()

    demanda = cursor.execute(
        'SELECT * FROM demandas WHERE id=?', (id,)
    ).fetchone()

    comentarios = cursor.execute(
        'SELECT * FROM comentarios WHERE demanda_id=?',
        (id,)
    ).fetchall()

    conn.close()

    return render_template('detalhes.html', demanda=demanda, comentarios=comentarios)


@app.route('/adicionar_comentario/<int:demanda_id>', methods=['POST'])
def adicionar_comentario(demanda_id):
    comentario = request.form['comentario']
    autor = request.form['autor']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO comentarios (demanda_id, comentario, autor, data)
        VALUES (?, ?, ?, ?)
        ''',
        (demanda_id, comentario, autor, datetime.now())
    )

    conn.commit()
    conn.close()

    return redirect(url_for('detalhes', id=demanda_id))


@app.route('/solicitantes')
def solicitantes():
    conn = get_db()
    cursor = conn.cursor()
    solicitantes = cursor.execute('SELECT * FROM solicitantes').fetchall()
    conn.close()
    return render_template('solicitantes.html', solicitantes=solicitantes)


@app.route('/novo_solicitante', methods=['GET', 'POST'])
def novo_solicitante():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO solicitantes (nome, senha) VALUES (?, ?)',
            (nome, senha)
        )
        conn.commit()
        conn.close()

        flash('Solicitante cadastrado com sucesso!')
        return redirect(url_for('solicitantes'))

    return render_template('novo_solicitante.html')

@app.route('/deletar_solicitante/<int:id>')
def deletar_solicitante(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM solicitantes WHERE id=?', (id,))
    conn.commit()
    conn.close()

    flash('Solicitante deletado!')
    return redirect(url_for('solicitantes'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/dashboard_data')
def dashboard_data():
    atualizar_prioridades_atrasadas()
    conn = get_db()
    cursor = conn.cursor()
    
    # Filtros
    periodo_inicio = request.args.get('inicio')
    periodo_fim = request.args.get('fim')
    responsavel = request.args.get('responsavel')
    prioridade = request.args.get('prioridade')
    status = request.args.get('status')
    somente_criticas_atrasadas = request.args.get('criticas_atrasadas', 'false').lower() == 'true'

    query = "SELECT * FROM demandas WHERE 1=1"
    params = []

    if responsavel:
        query += " AND responsavel = ?"
        params.append(responsavel)
    if prioridade:
        query += " AND nivel_prioridade = ?"
        params.append(prioridade)
    if status:
        query += " AND status = ?"
        params.append(status)

    demandas_db = cursor.execute(query, params).fetchall()
    conn.close()

    demandas = []
    total = 0
    abertas = 0
    concluidas = 0
    atrasadas = 0
    criticas = 0
    soma_dias_resolucao = 0
    peso_total_resolucao = 0
    
    agora = datetime.now()

    for d in demandas_db:
        # Converter sqlite.Row para dict para poder manipular/adicionar campos
        dem = dict(d)
        
        if dem['status'] is None:
            dem['status'] = 'Indefinido'
        if dem['responsavel'] is None:
            dem['responsavel'] = 'Sem responsável'
            
        # Tentar fazer parse das datas
        criacao_dt = None
        conclusao_dt = None
        prazo_dt = None
        
        try:
            if dem['data_criacao']:
                criacao_dt = datetime.strptime(dem['data_criacao'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass # Data inválida
            
        try:
            if dem['data_conclusao']:
                conclusao_dt = datetime.strptime(dem['data_conclusao'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
            
        try:
            if dem['prazo']:
                prazo_dt = datetime.strptime(dem['prazo'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass

        # Regra: Atrasadas aparecem em vermelho
        is_atrasada = False
        if prazo_dt:
            if dem['status'] != 'Concluída' and dem['status'] != 'Cancelada':
                if agora > prazo_dt:
                    is_atrasada = True
            elif conclusao_dt and conclusao_dt > prazo_dt:
                is_atrasada = True
        
        dem['is_atrasada'] = is_atrasada
        
        # Regra: Sem responsável fora do SLA
        is_sem_resp_fora_sla = (dem['responsavel'] == 'Sem responsável' and is_atrasada)
        dem['is_sem_resp_fora_sla'] = is_sem_resp_fora_sla

        # Regra: Críticas
        is_critica = (dem['nivel_prioridade'] == 'Crítica')
        
        # Filtro Surpresa: Críticas Atrasadas
        if somente_criticas_atrasadas:
            if not (is_critica and is_atrasada):
                continue

        # Filtro de Período (aplicar no python para evitar problemas com formato de data no sqlite se for invalido)
        if periodo_inicio and criacao_dt:
            inicio_dt = datetime.strptime(periodo_inicio, '%Y-%m-%d')
            if criacao_dt < inicio_dt: continue
        if periodo_fim and criacao_dt:
            fim_dt = datetime.strptime(periodo_fim, '%Y-%m-%d')
            # ajustar fim para final do dia
            fim_dt = fim_dt.replace(hour=23, minute=59, second=59)
            if criacao_dt > fim_dt: continue

        demandas.append(dem)
        total += 1
        
        if dem['status'] == 'Aberta' or dem['status'] == 'Indefinido':
            abertas += 1
        elif dem['status'] == 'Concluída':
            concluidas += 1
            
        if is_atrasada:
            atrasadas += 1
            
        if is_critica:
            criticas += 1
            
        # Tempo médio de resolução (canceladas ficam fora)
        if dem['status'] == 'Concluída' and criacao_dt and conclusao_dt:
            dias = (conclusao_dt - criacao_dt).total_seconds() / 86400.0
            peso = 2.0 if is_critica else 1.0
            soma_dias_resolucao += (dias * peso)
            peso_total_resolucao += peso

    tempo_medio = round(soma_dias_resolucao / peso_total_resolucao, 1) if peso_total_resolucao > 0 else 0
    
    # KPIs Agrupados
    kpis = {
        'total': total,
        'abertas': abertas,
        'abertas_pct': round((abertas/total)*100, 1) if total > 0 else 0,
        'concluidas': concluidas,
        'concluidas_pct': round((concluidas/total)*100, 1) if total > 0 else 0,
        'atrasadas': atrasadas,
        'atrasadas_pct': round((atrasadas/total)*100, 1) if total > 0 else 0,
        'criticas': criticas,
        'tempo_medio_dias': tempo_medio
    }

    # Gráfico por Status
    status_counts = {}
    prioridade_counts = {}
    responsavel_counts = {}
    evolucao = {} # yyyy-mm-dd -> count
    
    for dem in demandas:
        st = dem['status']
        status_counts[st] = status_counts.get(st, 0) + 1
        
        pr = dem['nivel_prioridade'] or 'Indefinida'
        prioridade_counts[pr] = prioridade_counts.get(pr, 0) + 1
        
        resp = dem['responsavel']
        responsavel_counts[resp] = responsavel_counts.get(resp, 0) + 1
        
        # Evolução temporal baseada na criação (ignorando datas invalidas tratadas anteriormente)
        date_str = dem['data_criacao'][:10] if (dem['data_criacao'] and len(dem['data_criacao']) >= 10 and '-' in dem['data_criacao']) else 'Data Inválida'
        if date_str != 'Data Inválida':
            evolucao[date_str] = evolucao.get(date_str, 0) + 1

    # Ordenar evolução cronologicamente
    evolucao_sorted = dict(sorted(evolucao.items()))

    graficos = {
        'status': status_counts,
        'prioridade': prioridade_counts,
        'evolucao': evolucao_sorted
    }

    # Criticas list
    demandas_criticas = [d for d in demandas if d['nivel_prioridade'] == 'Crítica']

    return jsonify({
        'kpis': kpis,
        'graficos': graficos,
        'responsaveis': responsavel_counts,
        'demandas': demandas,
        'demandas_criticas': demandas_criticas
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)