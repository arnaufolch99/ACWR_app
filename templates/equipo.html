import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)
DB_NAME = "acwr_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            equipo_id INTEGER,
            FOREIGN KEY (equipo_id) REFERENCES equipos (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cargas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jugador_id INTEGER,
            fecha DATE NOT NULL,
            minutos INTEGER NOT NULL,
            rpe REAL NOT NULL,
            carga_total REAL NOT NULL,
            accel_alta INTEGER DEFAULT 0,
            accel_baja INTEGER DEFAULT 0,
            decel_baja INTEGER DEFAULT 0,
            decel_alta INTEGER DEFAULT 0,
            FOREIGN KEY (jugador_id) REFERENCES jugadores (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def calcular_acwr(jugador_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    hoy = datetime.now().date()
    hace_7d = hoy - timedelta(days=7)
    hace_28d = hoy - timedelta(days=28)
    
    cursor.execute('''
        SELECT SUM(carga_total) FROM cargas 
        WHERE jugador_id = ? AND fecha >= ?
    ''', (jugador_id, hace_7d))
    carga_aguda = cursor.fetchone()[0] or 0.0
    
    cursor.execute('''
        SELECT SUM(carga_total) FROM cargas 
        WHERE jugador_id = ? AND fecha >= ?
    ''', (jugador_id, hace_28d))
    carga_28d_total = cursor.fetchone()[0] or 0.0
    carga_cronica = carga_28d_total / 4.0
    
    if carga_cronica > 0:
        acwr = round(carga_aguda / carga_cronica, 2)
    else:
        acwr = 0.0
        
    conn.close()
    return round(carga_aguda, 1), round(carga_cronica, 1), acwr

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipos')
    equipos = cursor.fetchall()
    conn.close()
    return render_template('index.html', equipos=equipos)

@app.route('/crear-equipo', methods=['POST'])
def crear_equipo():
    nombre = request.form.get('nombre')
    if nombre:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO equipos (nombre) VALUES (?)', (nombre,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/equipo/<int:equipo_id>')
def ver_equipo(equipo_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT nombre FROM equipos WHERE id = ?', (equipo_id,))
    equipo_row = cursor.fetchone()
    equipo_nombre = equipo_row[0] if equipo_row else "Equipo"
    
    cursor.execute('SELECT id, nombre FROM jugadores WHERE equipo_id = ?', (equipo_id,))
    jugadores_raw = cursor.fetchall()
    
    jugadores = []
    for j_id, j_nombre in jugadores_raw:
        aguda, cronica, acwr = calcular_acwr(j_id)
        
        if acwr == 0:
            estado, color = "Sin datos", "#718096"
        elif acwr < 0.8:
            estado, color = "Desentrenamiento", "#3182ce"
        elif 0.8 <= acwr <= 1.3:
            estado, color = "Sweet Spot", "#38a169"
        elif 1.3 < acwr < 1.5:
            estado, color = "Advertencia", "#dd6b20"
        else:
            estado, color = "Peligro (Spike)", "#e53e3e"
            
        jugadores.append({
            'id': j_id,
            'nombre': j_nombre,
            'aguda': aguda,
            'cronica': cronica,
            'acwr': acwr,
            'estado': estado,
            'color': color
        })
        
    conn.close()
    return render_template('equipo.html', equipo_nombre=equipo_nombre, equipo_id=equipo_id, jugadores=jugadores)

@app.route('/anadir-jugador/<int:equipo_id>', methods=['POST'])
def anadir_jugador(equipo_id):
    nombre = request.form.get('nombre')
    if nombre:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO jugadores (nombre, equipo_id) VALUES (?, ?)', (nombre, equipo_id))
        conn.commit()
        conn.close()
    return redirect(url_for('ver_equipo', equipo_id=equipo_id))

@app.route('/registrar-carga/<int:equipo_id>', methods=['POST'])
def registrar_carga(equipo_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    fecha = request.form.get('fecha') or datetime.now().strftime('%Y-%m-%d')
    minutos = float(request.form.get('minutos', 0))
    
    cursor.execute('SELECT id FROM jugadores WHERE equipo_id = ?', (equipo_id,))
    jugadores_ids = cursor.fetchall()
    
    for (j_id,) in jugadores_ids:
        rpe = request.form.get(f'rpe_{j_id}')
        if rpe and float(rpe) > 0:
            rpe_val = float(rpe)
            carga_total = minutos * rpe_val
            
            accel_alta = int(request.form.get(f'accel_alta_{j_id}', 0) or 0)
            accel_baja = int(request.form.get(f'accel_baja_{j_id}', 0) or 0)
            decel_baja = int(request.form.get(f'decel_baja_{j_id}', 0) or 0)
            decel_alta = int(request.form.get(f'decel_alta_{j_id}', 0) or 0)

            cursor.execute('''
                INSERT INTO cargas (jugador_id, fecha, minutos, rpe, carga_total, accel_alta, accel_baja, decel_baja, decel_alta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (j_id, fecha, minutos, rpe_val, carga_total, accel_alta, accel_baja, decel_baja, decel_alta))
            
    conn.commit()
    conn.close()
    return redirect(url_for('ver_equipo', equipo_id=equipo_id))

@app.route('/jugador/<int:jugador_id>')
def ver_jugador(jugador_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT nombre, equipo_id FROM jugadores WHERE id = ?', (jugador_id,))
    jugador = cursor.fetchone()
    
    cursor.execute('''
        SELECT SUM(accel_alta), SUM(accel_baja), SUM(decel_baja), SUM(decel_alta)
        FROM cargas WHERE jugador_id = ?
    ''', (jugador_id,))
    datos_gps = cursor.fetchone()
    conn.close()

    datos_gps = [d if d is not None else 0 for d in datos_gps]

    return render_template('jugador.html', 
                           jugador_nombre=jugador[0], 
                           equipo_id=jugador[1],
                           datos_gps=json.dumps(datos_gps))

if __name__ == '__main__':
    app.run(debug=True)
