# SGDI — Sistema de Gestão de Demandas Internas

Sistema web para gerenciamento de demandas internas, com controle de prioridade, responsável, prazo e acompanhamento por comentários.

---

## 🚀 Como rodar o projeto

**Pré-requisitos:** Python 3.8+ instalado.

```bash
# 1. Clone o repositório
git clone https://github.com/jeanlucas11/Projeto-Equipe-Cao.git
cd Projeto-Equipe-Cao

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicialize o banco de dados (apenas na primeira vez)
python init_db.py

# 4. Rode o servidor
python app.py
```

Acesse em: http://localhost:8000

---

## 📁 Estrutura de arquivos

```
Projeto-Equipe-Cao/
├── app.py              # Rotas e lógica principal (Flask)
├── init_db.py          # Criação do banco de dados SQLite
├── requirements.txt    # Dependências Python
├── templates/          # Templates HTML (Jinja2)
│   ├── index.html          # Lista de demandas com filtros
│   ├── nova_demanda.html   # Formulário de criação
│   ├── editar.html         # Formulário de edição
│   ├── detalhes.html       # Detalhes + comentários
│   ├── solicitantes.html   # Lista de solicitantes
│   ├── novo_solicitante.html
│   └── dashboard.html      # Dashboard com gráficos
├── static/             # CSS e assets estáticos
└── images/             # Imagens do projeto
```

---

## 📌 Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Criar demanda | Formulário com título, descrição, prioridade, prazo e responsável |
| Editar demanda | Atualiza todos os campos, inclusive status |
| Deletar demanda | Remove permanentemente |
| Ver detalhes | Exibe todos os dados + histórico de comentários |
| Comentários | Adicionar comentários por autor em qualquer demanda |
| Filtrar por prioridade | Checkboxes múltiplos (Baixa / Média / Alta / Crítica) |
| Ordenar por prioridade | Ordem crescente ou decrescente |
| Busca por texto | Filtra demandas por título ou descrição *(adicionado na Sprint 6)* |
| Prioridade automática | Demandas Alta com prazo vencido viram Crítica automaticamente |
| Dashboard | KPIs, gráficos por status/prioridade, evolução temporal |
| Solicitantes | CRUD de solicitantes cadastrados |

---

## 🗄️ Banco de dados

O banco é SQLite (arquivo `demandas.db` gerado pelo `init_db.py`).

**Tabelas principais:**

- `demandas` — campos: `id`, `titulo`, `descricao`, `solicitante`, `data_criacao`, `nivel_prioridade`, `status`, `responsavel`, `prazo`, `data_conclusao`
- `comentarios` — campos: `id`, `demanda_id`, `comentario`, `autor`, `data`
- `solicitantes` — campos: `id`, `nome`, `senha`

**Prioridades válidas:** `Baixa`, `Média`, `Alta`, `Crítica`

**Status válidos:** `Aberta`, `Em andamento`, `Concluída`, `Cancelada`

---

## 🧠 Tecnologias

- **Python + Flask** — backend e rotas
- **SQLite** — banco de dados local (sem configuração extra)
- **Jinja2** — templates HTML
- **HTML + CSS** — frontend sem frameworks externos

---

## 🔌 Principais rotas

| Método | Rota | O que faz |
|---|---|---|
| GET | `/` | Lista demandas (aceita `?busca=`, `?prioridade[]=`, `?ordem=`) |
| GET/POST | `/nova_demanda` | Cria nova demanda |
| GET/POST | `/editar/<id>` | Edita demanda existente |
| GET | `/deletar/<id>` | Deleta demanda |
| GET | `/detalhes/<id>` | Exibe detalhes e comentários |
| POST | `/adicionar_comentario/<id>` | Adiciona comentário |
| GET | `/solicitantes` | Lista solicitantes |
| GET/POST | `/novo_solicitante` | Cadastra solicitante |
| GET | `/dashboard` | Tela do dashboard |
| GET | `/api/dashboard_data` | API JSON com dados do dashboard |

---

## ➕ Como adicionar uma nova feature

1. Abra `app.py` e adicione uma nova rota com `@app.route('/sua-rota')`
2. Crie o template correspondente em `templates/` seguindo o padrão Jinja2 dos outros
3. Se precisar de nova tabela no banco, edite `init_db.py` e rode novamente
4. Siga o padrão de conexão com banco já existente: `conn = get_db()` → `cursor.execute()` → `conn.close()`

---

## 📌 TODO (melhorias planejadas)

- [ ] Sistema de usuários / autenticação
- [ ] Interface com Bootstrap
- [ ] Filtros combinados mais avançados no dashboard
- [ ] Exportação de relatórios em CSV

---

## 👨‍💻 Autores

Desenvolvido em 2026 — Equipe Cão
