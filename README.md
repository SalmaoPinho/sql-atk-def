# 🔐 SQL Injection: Ataque e Defesa

Aplicação educacional em Flask/SQLite para demonstrar vulnerabilidades de SQL Injection e suas contramedidas.

> ⚠️ **Aviso:** Este projeto é exclusivamente para fins educacionais, em ambiente controlado. Não utilize estas técnicas em sistemas reais sem autorização.

---

## 📋 Sobre o Projeto

Este projeto faz parte da **Atividade 01 — SQL Injection: Ataque e Defesa**, com o objetivo de demonstrar na prática:

- Como ataques de SQL Injection funcionam (**Red Team**)
- Como proteger aplicações contra esses ataques (**Blue Team**)

---

## 🛠️ Requisitos

- Python 3.x
- Flask

### Instalação

```bash
pip install flask
```

---

## 🚀 Como Executar

```bash
python app_sql_injection.py
```

Acesse no navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🗄️ Banco de Dados

A aplicação usa **SQLite em memória** com os seguintes usuários:

| Usuário | Senha            |
|---------|------------------|
| admin   | Sup3rS3cr3t@!    |
| rafa    | prof_rafa_123    |
| aluno   | 123456           |

---

## 🔴 Red Team — Ataques Demonstrados

### Parte 1: Bypass de Autenticação

A rota `/` possui uma query vulnerável por **concatenação direta de strings**:

```python
# ❌ VULNERÁVEL
sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

**Payload de ataque:**

| Campo    | Valor      |
|----------|------------|
| Usuário  | `admin'--` |
| Senha    | *(vazio)*  |

**Query resultante:**
```sql
SELECT * FROM users WHERE username = 'admin'--' AND password = ''
-- Tudo após -- é comentado → verificação de senha ignorada!
```

---

## 🔵 Blue Team — Defesas

A rota `/fix` implementa a versão segura usando **Prepared Statements (queries parametrizadas)**:

```python
# ✅ SEGURO
cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
```

Com queries parametrizadas, o banco de dados **separa código de dados**, tornando a injeção impossível.

---

## 📁 Estrutura do Projeto

```
sql-atk-def/
├── app_sql_injection.py   # Aplicação Flask (vulnerável + segura)
├── README.md              # Este arquivo
└── LICENSE
```

---

## 📚 Referências

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security/sql-injection)
- [Python SQLite3 — Parâmetros seguros](https://docs.python.org/3/library/sqlite3.html)
