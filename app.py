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
    conn = sqlite3.connect('demandas.db')
    cursor = conn.cursor()
    demandas = cursor.execute(
        'SELECT * FROM demandas ORDER BY CASE nivel_prioridade WHEN "Alta" THEN 1 WHEN "Média" THEN 2 WHEN "Baixa" THEN 3 END, data_criacao DESC'
    ).fetchall()
    conn.close()
    return render_template('index.html', demandas=demandas)


@app.route('/nova_demanda', methods=['GET', 'POST'])
def nova_demanda():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante = request.form['solicitante']
        prioridade = request.form.get('prioridade')


        conn = sqlite3.connect('demandas.db')
        cursor = conn.cursor()

        cursor.execute(
            f"INSERT INTO demandas (titulo, descricao, solicitante, data_criacao, nivel_prioridade) VALUES ('{titulo}', '{descricao}', '{solicitante}', '{datetime.now()}', '{prioridade}')")
        conn.commit()
        conn.close()

        flash('Salvo!')
        return redirect('/')

    return render_template('nova_demanda.html')


@app.route('/editar/<id>', methods=['GET', 'POST'])
def editar(id):
    conn = sqlite3.connect('demandas.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante = request.form['solicitante']
        prioridade = request.form.get('prioridade')    

        cursor.execute(
            f"UPDATE demandas SET titulo='{titulo}', descricao='{descricao}', solicitante='{solicitante}', nivel_prioridade='{prioridade}' WHERE id={id}")
        conn.commit()
        conn.close()
        return redirect('/')

    demanda = cursor.execute(f'SELECT * FROM demandas WHERE id={id}').fetchone()
    conn.close()
    return render_template('editar.html', demanda=demanda)


@app.route('/deletar/<id>')
def deletar(id):
    conn = sqlite3.connect('demandas.db')
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM demandas WHERE id={id}')
    conn.commit()
    conn.close()
    flash('Deletado!')
    return redirect('/')


@app.route('/buscar')
def buscar():
    termo = request.args.get('q')
    conn = sqlite3.connect('demandas.db')
    cursor = conn.cursor()
    resultados = cursor.execute(f"SELECT * FROM demandas WHERE titulo LIKE '%{termo}%'").fetchall()
    conn.close()
    return render_template('index.html', demandas=resultados)


# @app.route('/admin')
# def admin():
#     return 'Área administrativa'

@app.route('/detalhes/<id>')
def detalhes(id):
    conn = sqlite3.connect('demandas.db')
    cursor = conn.cursor()
    demanda = cursor.execute(f'SELECT * FROM demandas WHERE id={id}').fetchone()

    comentarios = cursor.execute(f'SELECT * FROM comentarios WHERE demanda_id={id}').fetchall()
    conn.close()

    return render_template('detalhes.html', demanda=demanda, comentarios=comentarios)


@app.route('/adicionar_comentario/<demanda_id>', methods=['POST'])
def adicionar_comentario(demanda_id):
    comentario = request.form['comentario']
    autor = request.form['autor']

    conn = sqlite3.connect('demandas.db')
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO comentarios (demanda_id, comentario, autor, data) VALUES ({demanda_id}, '{comentario}', '{autor}', '{datetime.now()}')")
    conn.commit()
    conn.close()

    return redirect(f'/detalhes/{demanda_id}')


def calcular_prazo(data_inicio):
    return "30 dias"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)