import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Configuração do Banco (SQLite em memória)
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    c = conn.cursor()
    # Tabela com 3 colunas: id, username, password
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT INTO users (username, password) VALUES ('admin', 'Sup3rS3cr3t@!')")
    c.execute("INSERT INTO users (username, password) VALUES ('rafa', 'prof_rafa_123')")
    c.execute("INSERT INTO users (username, password) VALUES ('aluno', '123456')")
    conn.commit()
    return conn

db_conn = init_db()

HTML_TEMPLATE = """
<!doctype html>
<style>body { font-family: sans-serif; max-width: 800px; margin: auto; padding: 20px; }</style>
<html>
<body>
    <h2>🔐 Sistema de Login Vulnerável</h2>
    <div style="background: #f0f0f0; padding: 15px; border-radius: 5px;">
        <form method="post">
            Usuário: <input type="text" name="username" style="width: 200px;"><br><br>
            Senha: <input type="password" name="password" style="width: 200px;"><br><br>
            <input type="submit" value="Entrar">
        </form>
    </div>
    <hr>
    <h3>Resultado:</h3>
    <div style="border: 1px solid #ddd; padding: 10px; background: #fff;">
        {{ result|safe }}
    </div>
    <p style="color: #666; font-size: 0.9em;">Query Executada (Debug): <code>{{ query }}</code></p>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login_vulnerable():
    result = "Aguardando login..."
    query_log = ""
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 🚩 VULNERABILIDADE AQUI: Concatenação direta
        sql_query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        query_log = sql_query
        
        try:
            cursor = db_conn.cursor()
            cursor.execute(sql_query) # Executa a string montada
            user = cursor.fetchone() # Pega apenas o primeiro resultado
            
            if user:
                # user[0]=id, user[1]=username, user[2]=password
                result = f"<b style='color:green'>ACESSO PERMITIDO!</b> Bem-vindo, {user[1]}."
            else:
                result = "<b style='color:red'>ACESSO NEGADO.</b>"
        except Exception as e:
            result = f"Erro de Banco de Dados: {e}"

    return render_template_string(HTML_TEMPLATE, result=result, query=query_log)

# 🛠️ MISSÃO: Implemente a rota segura aqui depois
# @app.route('/fix', methods=['GET', 'POST'])
# def login_secure():
#     ...

if __name__ == '__main__':
    app.run(debug=True)