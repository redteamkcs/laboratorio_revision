# main.py - Proyecto de práctica para revisión de código
# ADVERTENCIA: Este código contiene vulnerabilidades intencionales para fines educativos
# NO USAR EN PRODUCCIÓN

import hashlib
import sqlite3
import subprocess
import pickle
import base64
import os
from flask import Flask, request, render_template_string, session, redirect

app = Flask(__name__)
app.secret_key = "clave_secreta_fija_123"  # Vulnerabilidad 1: Clave secreta hardcodeada

# Base de datos simulada
conn = sqlite3.connect('usuarios.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                  (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
conn.commit()

# HTML template vulnerable
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<body>
    <h2>Login</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Usuario">
        <input type="password" name="password" placeholder="Contraseña">
        <input type="submit" value="Login">
    </form>
    <div>{{ mensaje|safe }}</div>  <!-- Vulnerabilidad 2: XSS potencial -->
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(LOGIN_TEMPLATE, mensaje="Bienvenido")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Vulnerabilidad 3: SQL Injection
    query = f"SELECT * FROM usuarios WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        session['user'] = username
        return redirect('/dashboard')
    else:
        mensaje = f"Error: Usuario {username} no encontrado"  # Vulnerabilidad 4: Exposición de información
        return render_template_string(LOGIN_TEMPLATE, mensaje=mensaje)

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Bienvenido {session['user']}"
    return redirect('/')

@app.route('/procesar', methods=['POST'])
def procesar():
    # Vulnerabilidad 5: Insecure Deserialization
    data = request.form.get('data', '')
    try:
        obj = pickle.loads(base64.b64decode(data))
        resultado = subprocess.run(obj['cmd'], shell=True, capture_output=True)  # Vulnerabilidad 6: Command Injection
        return resultado.stdout
    except:
        return "Error procesando datos"

@app.route('/admin')
def admin():
    # Vulnerabilidad 7: Broken Access Control
    if request.args.get('admin') == 'true':
        return "Panel de administración - Datos sensibles"
    return "Acceso denegado"

@app.route('/buscar')
def buscar():
    # Vulnerabilidad 8: Path Traversal
    filename = request.args.get('file', '')
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return content
    except:
        return "Archivo no encontrado"

@app.route('/hash')
def hash_password():
    # Vulnerabilidad 9: Weak Hashing
    password = request.args.get('pass', '')
    # Usando MD5 que es considerado inseguro
    hashed = hashlib.md5(password.encode()).hexdigest()
    return f"Hash MD5: {hashed}"

@app.route('/debug')
def debug():
    # Vulnerabilidad 10: Debug mode enabled in production
    import pdb; pdb.set_trace()
    return "Modo debug"

if __name__ == '__main__':
    # Vulnerabilidad 11: Debug mode en producción
    app.run(debug=True, host='0.0.0.0', port=5000)