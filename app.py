import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for

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
            FOREIGN KEY (jugador_id) REFERENCES jugadores (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def calcular_acwr(jugador_id, fecha_ref_str=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if fecha_ref_str:
        fecha_ref = datetime.strptime(fecha_ref_str, '%Y-%m-%d').date()
    else:
        fecha_ref = datetime.now().date()
        
    hace_7d = fecha_ref - timedelta(days=6)
    hace_28d = fecha_ref - timedelta(days=27)
    
    # Carga Aguda (7 días hasta la fecha de referencia)
    cursor.execute('''
        SELECT SUM(carga_total) FROM cargas 
        WHERE jugador_id = ? AND fecha >= ? AND fecha <= ?
    ''', (jugador_id, hace_7d, fecha_ref))
    carga_aguda = cursor.fetchone()[0] or 0.0
    
    # Carga Crónica (28 días promedio semanal)
    cursor.execute('''
        SELECT SUM(carga_total) FROM cargas 
        WHERE jugador_id = ? AND fecha >= ? AND fecha <= ?
    ''', (jugador_id, hace_28d, fecha_ref))
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
    fecha_sel = request.args.get('fecha') or datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT nombre FROM equipos WHERE id = ?', (equipo_id,))
    equipo_row = cursor.fetchone()
    equipo_nombre = equipo_row[0] if equipo_row else "Equipo"
    
    cursor.execute('SELECT id, nombre FROM jugadores WHERE equipo_id = ?', (equipo_id,))
    jugadores_raw = cursor.fetchall()
    
    jugadores = []
    for j_id, j_nombre in jugadores_raw:
        aguda, cronica, acwr = calcular_acwr(j_id, fecha_sel)
        
        # Cargar registro previo si ya existe para esa fecha
        cursor.execute('''
            SELECT minutos, rpe, carga_total FROM cargas 
            WHERE jugador_id = ? AND fecha = ?
        ''', (j_id, fecha_sel))
        reg = cursor.fetchone()
        
        min_reg = reg[0] if reg else ""
        rpe_reg = reg[1] if reg else ""
        carga_dia = reg[2] if reg else 0.0
        
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
            'color': color,
            'minutos': min_reg,
            'rpe': rpe_reg,
            'carga_dia': carga_dia
        })
        
    conn.close()
    return render_template('equipo.html', equipo_nombre=equipo_nombre, equipo_id=equipo_id, jugadores=jugadores, fecha_sel=fecha_sel)

@app.route('/anadir-jugador/<int:equipo_id>', methods=['POST'])
def anadir_jugador(equipo_id):
    nombre = request.form.get('nombre')
    fecha_sel = request.form.get('fecha_sel') or datetime.now().strftime('%Y-%m-%d')
    if nombre:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO jugadores (nombre, equipo_id) VALUES (?, ?)', (nombre, equipo_id))
        conn.commit()
        conn.close()
    return redirect(url_for('ver_equipo', equipo_id=equipo_id, fecha=fecha_sel))

@app.route('/registrar-carga/<int:equipo_id>', methods=['POST'])
def registrar_carga(equipo_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    fecha = request.form.get('fecha') or datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('SELECT id FROM jugadores WHERE equipo_id = ?', (equipo_id,))
    jugadores_ids = cursor.fetchall()
    
    for (j_id,) in jugadores_ids:
        rpe_str = request.form.get(f'rpe_{j_id}')
        min_str = request.form.get(f'min_{j_id}')
        
        # Elimina el registro anterior si se vuelve a guardar para el mismo día
        cursor.execute('DELETE FROM cargas WHERE jugador_id = ? AND fecha = ?', (j_id, fecha))
        
        if rpe_str and min_str and float(rpe_str) > 0 and float(min_str) > 0:
            rpe_val = float(rpe_str)
            min_val = float(min_str)
            carga_total = min_val * rpe_val
            cursor.execute('''
                INSERT INTO cargas (jugador_id, fecha, minutos, rpe, carga_total)
                VALUES (?, ?, ?, ?, ?)
            ''', (j_id, fecha, min_val, rpe_val, carga_total))
            
    conn.commit()
    conn.close()
    return redirect(url_for('ver_equipo', equipo_id=equipo_id, fecha=fecha))

if __name__ == '__main__':
    app.run(debug=True)
