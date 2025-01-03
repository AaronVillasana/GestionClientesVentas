import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clave secreta para sesiones

DATABASE = 'database.db'

# Función para conectar a la base de datos
def conectar_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Ruta principal
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

# Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('index'))
        flash("Credenciales incorrectas", "danger")
    return render_template('login.html')

# Registro de usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        conn.close()
        flash("Registro exitoso, por favor inicia sesión", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('login'))

# Gestión de clientes
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = conectar_db()
    cur = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        cur.execute("INSERT INTO clientes (nombre, email) VALUES (?, ?)", (nombre, email))
        conn.commit()
        flash("Cliente agregado exitosamente", "success")
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

# Gestión de ventas
@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        monto = request.form['monto']
        cur.execute("INSERT INTO ventas (cliente_id, monto) VALUES (?, ?)", (cliente_id, monto))
        conn.commit()
        flash("Venta registrada exitosamente", "success")
    cur.execute("SELECT ventas.id, clientes.nombre AS cliente, ventas.monto FROM ventas JOIN clientes ON ventas.cliente_id = clientes.id")
    ventas = cur.fetchall()
    conn.close()
    return render_template('ventas.html', ventas=ventas, clientes=clientes)

# Reportes
@app.route('/reporte')
def reporte():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT clientes.nombre, SUM(ventas.monto) AS total FROM ventas JOIN clientes ON ventas.cliente_id = clientes.id GROUP BY clientes.id")
    reporte = cur.fetchall()
    conn.close()
    return render_template('reporte.html', reporte=reporte)

# Gráficos
@app.route('/graficos')
def graficos():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT clientes.nombre, SUM(ventas.monto) AS total FROM ventas JOIN clientes ON ventas.cliente_id = clientes.id GROUP BY clientes.id")
    data = cur.fetchall()
    conn.close()
    return render_template('graficos.html', data=data)

# Exportar clientes a Excel
@app.route('/exportar_clientes')
def exportar_clientes():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    data = cur.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['ID', 'Nombre', 'Email'])
    filename = 'clientes.xlsx'
    df.to_excel(filename, index=False)
    return send_file(filename, as_attachment=True)

# Inicialización de la base de datos
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)")
        cur.execute("CREATE TABLE clientes (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT)")
        cur.execute("CREATE TABLE ventas (id INTEGER PRIMARY KEY, cliente_id INTEGER, monto REAL, FOREIGN KEY(cliente_id) REFERENCES clientes(id))")
        conn.close()
    print("Servidor Flask iniciando...")
    app.run(debug=True)
