from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"  # Clave para mensajes flash

DATABASE = 'database.db'

# Conectar a la base de datos
def conectar_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clientes')
def clientes():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/agregar_cliente', methods=['POST'])
def agregar_cliente():
    nombre = request.form['nombre']
    email = request.form['email']
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nombre, email) VALUES (?, ?)", (nombre, email))
    conn.commit()
    conn.close()
    flash("Cliente agregado exitosamente", "success")
    return redirect(url_for('clientes'))

@app.route('/ventas')
def ventas():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT ventas.id, clientes.nombre AS cliente, ventas.monto FROM ventas JOIN clientes ON ventas.cliente_id = clientes.id")
    ventas = cur.fetchall()
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    conn.close()
    return render_template('ventas.html', ventas=ventas, clientes=clientes)

@app.route('/registrar_venta', methods=['POST'])
def registrar_venta():
    cliente_id = request.form['cliente_id']
    monto = request.form['monto']
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO ventas (cliente_id, monto) VALUES (?, ?)", (cliente_id, monto))
    conn.commit()
    conn.close()
    flash("Venta registrada exitosamente", "success")
    return redirect(url_for('ventas'))

@app.route('/reporte')
def reporte():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT clientes.nombre, SUM(ventas.monto) AS total FROM ventas JOIN clientes ON ventas.cliente_id = clientes.id GROUP BY clientes.id")
    reporte = cur.fetchall()
    conn.close()
    return render_template('reporte.html', reporte=reporte)

if __name__ == '__main__':
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ventas (id INTEGER PRIMARY KEY, cliente_id INTEGER, monto REAL, FOREIGN KEY(cliente_id) REFERENCES clientes(id))")
    conn.close()
    app.run(debug=True)
