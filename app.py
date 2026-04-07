from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = '123456'


def get_db():
    conn = sqlite3.connect('demandas.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
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

    # define ordem correta (Alta → Média → Baixa)
    order_clause = '''
        CASE 
            WHEN LOWER(nivel_prioridade) = "alta" THEN 1
            WHEN LOWER(nivel_prioridade) IN ("média","media") THEN 2
            WHEN LOWER(nivel_prioridade) = "baixa" THEN 3
            ELSE 4
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

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            '''
            INSERT INTO demandas (titulo, descricao, solicitante, data_criacao, nivel_prioridade)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (titulo, descricao, solicitante, datetime.now(), prioridade)
        )

        conn.commit()
        conn.close()

        flash('Demanda salva!')
        return redirect(url_for('index'))

    return render_template('nova_demanda.html')


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

        cursor.execute(
            '''
            UPDATE demandas 
            SET titulo=?, descricao=?, solicitante=?, nivel_prioridade=?
            WHERE id=?
            ''',
            (titulo, descricao, solicitante, prioridade, id)
        )

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    demanda = cursor.execute(
        'SELECT * FROM demandas WHERE id=?', (id,)
    ).fetchone()

    conn.close()
    return render_template('editar.html', demanda=demanda)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)