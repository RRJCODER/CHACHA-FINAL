from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3
import threading
import webbrowser
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / "control_horario.db"
BACKUP_DIR = BASE_DIR / "backups"
PID_FILE = BASE_DIR / "app.pid"
BACKUP_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = "chacha-control-horario-local"


def registrar_pid():
    try:
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    except OSError:
        pass


def borrar_pid():
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except OSError:
        pass


def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA synchronous = FULL")
    return con


def crear_backup(motivo="manual"):
    """Crea una copia segura de la base de datos sin interrumpir la aplicacion."""
    BACKUP_DIR.mkdir(exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"control_horario_{motivo}_{marca}.db"

    origen = sqlite3.connect(DB)
    copia = sqlite3.connect(destino)
    try:
        origen.backup(copia)
    finally:
        copia.close()
        origen.close()

    limpiar_backups(max_copias=60)
    return destino


def limpiar_backups(max_copias=60):
    copias = sorted(BACKUP_DIR.glob("control_horario_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for copia in copias[max_copias:]:
        try:
            copia.unlink()
        except OSError:
            pass


def guardar_y_redirigir(endpoint, **kwargs):
    copia = crear_backup("auto")
    flash(f"Cambios guardados. Copia de seguridad creada: {copia.name}", "ok")
    return redirect(url_for(endpoint, **kwargs))


def numero_formulario(nombre, defecto=0.0):
    valor = request.form.get(nombre, str(defecto)).replace(",", ".").strip()
    try:
        return float(valor)
    except ValueError:
        return defecto


def columna_existe(tabla, columna):
    con = conectar()
    cur = con.cursor()
    cur.execute(f"PRAGMA table_info({tabla})")
    columnas = [fila["name"] for fila in cur.fetchall()]
    con.close()
    return columna in columnas


def crear_tablas():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trabajadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            precio_hora REAL DEFAULT 0,
            activo INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT,
            cliente TEXT,
            activo INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS horas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            trabajador_id INTEGER NOT NULL,
            obra_id INTEGER NOT NULL,
            horas REAL NOT NULL,
            horas_extra REAL DEFAULT 0,
            dinero_adelantado REAL DEFAULT 0,
            liquidado INTEGER DEFAULT 0,
            fecha_liquidacion TEXT,
            observaciones TEXT,
            FOREIGN KEY (trabajador_id) REFERENCES trabajadores(id),
            FOREIGN KEY (obra_id) REFERENCES obras(id)
        )
    """)

    con.commit()
    con.close()


def actualizar_bd():
    con = conectar()
    cur = con.cursor()

    if not columna_existe("trabajadores", "precio_hora"):
        cur.execute("ALTER TABLE trabajadores ADD COLUMN precio_hora REAL DEFAULT 0")

    if not columna_existe("trabajadores", "activo"):
        cur.execute("ALTER TABLE trabajadores ADD COLUMN activo INTEGER DEFAULT 1")

    if not columna_existe("obras", "cliente"):
        cur.execute("ALTER TABLE obras ADD COLUMN cliente TEXT")

    if not columna_existe("obras", "activo"):
        cur.execute("ALTER TABLE obras ADD COLUMN activo INTEGER DEFAULT 1")

    if not columna_existe("horas", "horas_extra"):
        cur.execute("ALTER TABLE horas ADD COLUMN horas_extra REAL DEFAULT 0")

    if not columna_existe("horas", "dinero_adelantado"):
        cur.execute("ALTER TABLE horas ADD COLUMN dinero_adelantado REAL DEFAULT 0")

    if not columna_existe("horas", "observaciones"):
        cur.execute("ALTER TABLE horas ADD COLUMN observaciones TEXT")

    if not columna_existe("horas", "liquidado"):
        cur.execute("ALTER TABLE horas ADD COLUMN liquidado INTEGER DEFAULT 0")

    if not columna_existe("horas", "fecha_liquidacion"):
        cur.execute("ALTER TABLE horas ADD COLUMN fecha_liquidacion TEXT")

    # En esta version las horas extra son manuales. No se calculan ni se modifican automaticamente.
    cur.execute("UPDATE horas SET horas_extra = 0 WHERE horas_extra IS NULL")
    cur.execute("UPDATE horas SET dinero_adelantado = 0 WHERE dinero_adelantado IS NULL")
    cur.execute("UPDATE horas SET liquidado = 0 WHERE liquidado IS NULL")

    con.commit()
    con.close()


@app.route("/guardar_backup")
def guardar_backup():
    copia = crear_backup("manual")
    flash(f"Copia de seguridad creada correctamente: {copia.name}", "ok")
    volver = request.referrer or url_for("index")
    return redirect(volver)


@app.route("/salir")
def salir():
    copia = crear_backup("salida")

    def apagar_completo():
        # Da tiempo a que el navegador reciba la pagina de salida y despues mata este proceso.
        borrar_pid()
        os._exit(0)

    threading.Timer(1.2, apagar_completo).start()
    return render_template("salir.html", copia=copia.name)


@app.route("/")
def index():
    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM trabajadores WHERE activo = 1")
    total_trabajadores = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM obras WHERE activo = 1")
    total_obras = cur.fetchone()["total"]

    cur.execute("SELECT IFNULL(SUM(horas), 0) AS total FROM horas")
    total_horas = cur.fetchone()["total"]

    cur.execute("SELECT IFNULL(SUM(horas_extra), 0) AS total FROM horas")
    total_horas_extra = cur.fetchone()["total"]

    cur.execute("SELECT IFNULL(SUM(dinero_adelantado), 0) AS total FROM horas")
    total_adelantos = cur.fetchone()["total"]

    cur.execute("""
        SELECT IFNULL(SUM(h.horas_extra * t.precio_hora), 0) AS total
        FROM horas h
        JOIN trabajadores t ON t.id = h.trabajador_id
    """)
    total_extras = cur.fetchone()["total"]

    cur.execute("""
        SELECT IFNULL(SUM(
            CASE
                WHEN IFNULL(h.liquidado, 0) = 1 THEN 0
                WHEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) > 0
                    THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado)
                ELSE 0
            END
        ), 0) AS total
        FROM horas h
        JOIN trabajadores t ON t.id = h.trabajador_id
    """)
    total_pendiente = cur.fetchone()["total"]

    cur.execute("""
        SELECT h.fecha, t.nombre AS trabajador, o.nombre AS obra, h.horas,
               h.horas_extra, h.dinero_adelantado, h.liquidado, h.fecha_liquidacion,
               h.horas_extra * t.precio_hora AS importe_extra
        FROM horas h
        JOIN trabajadores t ON t.id = h.trabajador_id
        JOIN obras o ON o.id = h.obra_id
        ORDER BY h.fecha DESC, h.id DESC
        LIMIT 8
    """)
    ultimos_registros = cur.fetchall()

    cur.execute("""
        SELECT t.nombre,
               IFNULL(SUM(h.horas), 0) AS horas,
               IFNULL(SUM(h.horas_extra), 0) AS horas_extra,
               IFNULL(SUM(h.horas_extra * t.precio_hora), 0) AS extras,
               IFNULL(SUM(h.dinero_adelantado), 0) AS adelantado,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS liquidado_importe,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN 0 WHEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) > 0 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS pendiente
        FROM trabajadores t
        LEFT JOIN horas h ON h.trabajador_id = t.id
        WHERE t.activo = 1
        GROUP BY t.id
        ORDER BY horas_extra DESC, t.nombre
        LIMIT 8
    """)
    resumen_trabajadores = cur.fetchall()
    con.close()

    return render_template(
        "index.html",
        total_trabajadores=total_trabajadores,
        total_obras=total_obras,
        total_horas=total_horas,
        total_horas_extra=total_horas_extra,
        total_adelantos=total_adelantos,
        total_extras=total_extras,
        total_pendiente=total_pendiente,
        ultimos_registros=ultimos_registros,
        resumen_trabajadores=resumen_trabajadores,
    )


@app.route("/trabajadores", methods=["GET", "POST"])
def trabajadores():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        precio_hora_extra = numero_formulario("precio_hora", 0)
        if nombre:
            cur.execute("""
                INSERT INTO trabajadores (nombre, telefono, precio_hora, activo)
                VALUES (?, ?, ?, 1)
            """, (nombre, telefono, precio_hora_extra))
            con.commit()
        con.close()
        return guardar_y_redirigir("trabajadores")

    cur.execute("""
        SELECT t.*,
               IFNULL(SUM(h.horas), 0) AS total_horas,
               IFNULL(SUM(h.horas_extra), 0) AS horas_extra,
               IFNULL(SUM(h.horas_extra * t.precio_hora), 0) AS extras,
               IFNULL(SUM(h.dinero_adelantado), 0) AS adelantado,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS liquidado_importe,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN 0 WHEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) > 0 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS pendiente
        FROM trabajadores t
        LEFT JOIN horas h ON h.trabajador_id = t.id
        WHERE t.activo = 1
        GROUP BY t.id
        ORDER BY t.nombre
    """)
    lista = cur.fetchall()
    con.close()
    return render_template("trabajadores.html", trabajadores=lista)


@app.route("/trabajadores/editar/<int:id>", methods=["GET", "POST"])
def editar_trabajador(id):
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        precio_hora_extra = numero_formulario("precio_hora", 0)
        if nombre:
            cur.execute("""
                UPDATE trabajadores SET nombre = ?, telefono = ?, precio_hora = ? WHERE id = ?
            """, (nombre, telefono, precio_hora_extra, id))
            con.commit()
        con.close()
        return guardar_y_redirigir("trabajadores")

    cur.execute("SELECT * FROM trabajadores WHERE id = ?", (id,))
    trabajador = cur.fetchone()
    con.close()
    return render_template("editar_trabajador.html", trabajador=trabajador)


@app.route("/trabajadores/borrar/<int:id>")
def borrar_trabajador(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("UPDATE trabajadores SET activo = 0 WHERE id = ?", (id,))
    con.commit()
    con.close()
    return guardar_y_redirigir("trabajadores")


@app.route("/obras", methods=["GET", "POST"])
def obras():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        cliente = request.form.get("cliente", "").strip()
        direccion = request.form.get("direccion", "").strip()
        if nombre:
            cur.execute("""
                INSERT INTO obras (nombre, cliente, direccion, activo)
                VALUES (?, ?, ?, 1)
            """, (nombre, cliente, direccion))
            con.commit()
        con.close()
        return guardar_y_redirigir("obras")

    cur.execute("""
        SELECT o.*,
               IFNULL(SUM(h.horas), 0) AS total_horas,
               IFNULL(SUM(h.horas_extra), 0) AS horas_extra,
               IFNULL(SUM(h.dinero_adelantado), 0) AS adelantado,
               IFNULL(SUM(h.horas_extra * t.precio_hora), 0) AS extras
        FROM obras o
        LEFT JOIN horas h ON h.obra_id = o.id
        LEFT JOIN trabajadores t ON t.id = h.trabajador_id
        WHERE o.activo = 1
        GROUP BY o.id
        ORDER BY o.nombre
    """)
    lista = cur.fetchall()
    con.close()
    return render_template("obras.html", obras=lista)


@app.route("/obras/editar/<int:id>", methods=["GET", "POST"])
def editar_obra(id):
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        cliente = request.form.get("cliente", "").strip()
        direccion = request.form.get("direccion", "").strip()
        if nombre:
            cur.execute("""
                UPDATE obras SET nombre = ?, cliente = ?, direccion = ? WHERE id = ?
            """, (nombre, cliente, direccion, id))
            con.commit()
        con.close()
        return guardar_y_redirigir("obras")

    cur.execute("SELECT * FROM obras WHERE id = ?", (id,))
    obra = cur.fetchone()
    con.close()
    return render_template("editar_obra.html", obra=obra)


@app.route("/obras/borrar/<int:id>")
def borrar_obra(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("UPDATE obras SET activo = 0 WHERE id = ?", (id,))
    con.commit()
    con.close()
    return guardar_y_redirigir("obras")


@app.route("/horas", methods=["GET", "POST"])
def horas():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        fecha = request.form.get("fecha", "").strip()
        trabajador_id = request.form.get("trabajador_id")
        obra_id = request.form.get("obra_id")
        horas_val = numero_formulario("horas", 0)
        horas_extra = numero_formulario("horas_extra", 0)
        dinero_adelantado = numero_formulario("dinero_adelantado", 0)
        observaciones = request.form.get("observaciones", "").strip()

        if fecha and trabajador_id and obra_id and horas_val >= 0 and horas_extra >= 0:
            cur.execute("""
                INSERT INTO horas (
                    fecha, trabajador_id, obra_id, horas, horas_extra, dinero_adelantado, liquidado, fecha_liquidacion, observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, 0, NULL, ?)
            """, (
                fecha, trabajador_id, obra_id, horas_val, horas_extra, dinero_adelantado, observaciones,
            ))
            con.commit()
        con.close()
        return guardar_y_redirigir("horas")

    cur.execute("SELECT * FROM trabajadores WHERE activo = 1 ORDER BY nombre")
    trabajadores_lista = cur.fetchall()
    cur.execute("SELECT * FROM obras WHERE activo = 1 ORDER BY nombre")
    obras_lista = cur.fetchall()
    cur.execute("""
        SELECT h.id, h.fecha, t.nombre AS trabajador, o.nombre AS obra, h.horas,
               h.horas_extra, h.dinero_adelantado, h.liquidado, h.fecha_liquidacion, h.observaciones, t.precio_hora,
               h.horas_extra * t.precio_hora AS importe_extra,
               CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN 0 WHEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) > 0 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END AS pendiente
        FROM horas h
        JOIN trabajadores t ON t.id = h.trabajador_id
        JOIN obras o ON o.id = h.obra_id
        ORDER BY h.fecha DESC, h.id DESC
    """)
    registros = cur.fetchall()
    con.close()
    return render_template(
        "horas.html",
        trabajadores=trabajadores_lista,
        obras=obras_lista,
        registros=registros,
        hoy=date.today().isoformat(),
    )


@app.route("/horas/borrar/<int:id>")
def borrar_hora(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM horas WHERE id = ?", (id,))
    con.commit()
    con.close()
    return guardar_y_redirigir("horas")


@app.route("/horas/liquidar/<int:id>", methods=["POST"])
def liquidar_hora(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("UPDATE horas SET liquidado = 1, fecha_liquidacion = ? WHERE id = ?", (date.today().isoformat(), id))
    con.commit()
    con.close()
    return guardar_y_redirigir("horas")


@app.route("/horas/desliquidar/<int:id>", methods=["POST"])
def desliquidar_hora(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("UPDATE horas SET liquidado = 0, fecha_liquidacion = NULL WHERE id = ?", (id,))
    con.commit()
    con.close()
    return guardar_y_redirigir("horas")


def condiciones_resumen_desde_request():
    condiciones = []
    parametros = []
    trabajador_id = request.form.get("trabajador_id", "") or request.args.get("trabajador_id", "")
    obra_id = request.form.get("obra_id", "") or request.args.get("obra_id", "")
    fecha = request.form.get("fecha", "") or request.args.get("fecha", "")
    mes = request.form.get("mes", "") or request.args.get("mes", "")
    anio = request.form.get("anio", "") or request.args.get("anio", "")
    if trabajador_id:
        condiciones.append("trabajador_id = ?")
        parametros.append(trabajador_id)
    if obra_id:
        condiciones.append("obra_id = ?")
        parametros.append(obra_id)
    if fecha:
        condiciones.append("fecha = ?")
        parametros.append(fecha)
    if mes:
        condiciones.append("strftime('%m', fecha) = ?")
        parametros.append(mes.zfill(2))
    if anio:
        condiciones.append("strftime('%Y', fecha) = ?")
        parametros.append(anio)
    return condiciones, parametros, {"trabajador_id": trabajador_id, "obra_id": obra_id, "fecha": fecha, "mes": mes, "anio": anio}


@app.route("/resumen/liquidar_trabajador/<int:id>", methods=["POST"])
def liquidar_trabajador(id):
    condiciones, parametros, filtros = condiciones_resumen_desde_request()
    condiciones.append("trabajador_id = ?")
    parametros.append(id)
    condiciones.append("IFNULL(liquidado, 0) = 0")
    where = " AND ".join(condiciones)

    con = conectar()
    cur = con.cursor()
    cur.execute(f"UPDATE horas SET liquidado = 1, fecha_liquidacion = ? WHERE {where}", [date.today().isoformat(), *parametros])
    con.commit()
    con.close()
    flash("Extras marcados como liquidados para ese trabajador en los filtros seleccionados.", "ok")
    return redirect(url_for("resumen", **filtros))


@app.route("/resumen/liquidar_registro/<int:id>", methods=["POST"])
def liquidar_registro_resumen(id):
    _, _, filtros = condiciones_resumen_desde_request()
    con = conectar()
    cur = con.cursor()
    cur.execute("UPDATE horas SET liquidado = 1, fecha_liquidacion = ? WHERE id = ?", (date.today().isoformat(), id))
    con.commit()
    con.close()
    flash("Registro marcado como pagado/liquidado.", "ok")
    return redirect(url_for("resumen", **filtros))


@app.route("/resumen/desliquidar_registro/<int:id>", methods=["POST"])
def desliquidar_registro_resumen(id):
    _, _, filtros = condiciones_resumen_desde_request()
    con = conectar()
    cur = con.cursor()
    cur.execute("UPDATE horas SET liquidado = 0, fecha_liquidacion = NULL WHERE id = ?", (id,))
    con.commit()
    con.close()
    flash("Registro devuelto a pendiente.", "ok")
    return redirect(url_for("resumen", **filtros))


@app.route("/resumen")
def resumen():
    con = conectar()
    cur = con.cursor()

    trabajador_id = request.args.get("trabajador_id", "")
    obra_id = request.args.get("obra_id", "")
    fecha = request.args.get("fecha", "")
    mes = request.args.get("mes", "")
    anio = request.args.get("anio", "")

    condiciones = []
    parametros = []
    if trabajador_id:
        condiciones.append("h.trabajador_id = ?")
        parametros.append(trabajador_id)
    if obra_id:
        condiciones.append("h.obra_id = ?")
        parametros.append(obra_id)
    if fecha:
        condiciones.append("h.fecha = ?")
        parametros.append(fecha)
    if mes:
        condiciones.append("strftime('%m', h.fecha) = ?")
        parametros.append(mes.zfill(2))
    if anio:
        condiciones.append("strftime('%Y', h.fecha) = ?")
        parametros.append(anio)

    where_horas = "WHERE " + " AND ".join(condiciones) if condiciones else ""

    cur.execute("SELECT * FROM trabajadores WHERE activo = 1 ORDER BY nombre")
    lista_trabajadores = cur.fetchall()
    cur.execute("SELECT * FROM obras WHERE activo = 1 ORDER BY nombre")
    lista_obras = cur.fetchall()

    cur.execute(f"""
        SELECT IFNULL(SUM(h.horas), 0) AS total_horas,
               IFNULL(SUM(h.horas_extra), 0) AS total_horas_extra,
               IFNULL(SUM(h.horas_extra * t.precio_hora), 0) AS total_extras,
               IFNULL(SUM(h.dinero_adelantado), 0) AS total_adelantado,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS total_liquidado,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN 0 WHEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) > 0 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS total_pendiente,
               COUNT(h.id) AS total_registros
        FROM horas h
        JOIN trabajadores t ON t.id = h.trabajador_id
        JOIN obras o ON o.id = h.obra_id
        {where_horas}
    """, parametros)
    totales = cur.fetchone()

    cur.execute(f"""
        SELECT t.id AS trabajador_id, t.nombre AS trabajador,
               IFNULL(SUM(h.horas), 0) AS horas,
               IFNULL(SUM(h.horas_extra), 0) AS horas_extra,
               t.precio_hora,
               IFNULL(SUM(h.horas_extra * t.precio_hora), 0) AS extras,
               IFNULL(SUM(h.dinero_adelantado), 0) AS adelantado,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS liquidado_importe,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN 0 WHEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) > 0 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS pendiente
        FROM horas h
        JOIN trabajadores t ON t.id = h.trabajador_id
        JOIN obras o ON o.id = h.obra_id
        {where_horas}
        GROUP BY t.id
        ORDER BY horas_extra DESC, t.nombre
    """, parametros)
    trabajadores_resumen = cur.fetchall()

    cur.execute(f"""
        SELECT o.nombre AS obra, o.cliente,
               IFNULL(SUM(h.horas), 0) AS horas,
               IFNULL(SUM(h.horas_extra), 0) AS horas_extra,
               IFNULL(SUM(h.dinero_adelantado), 0) AS adelantado,
               IFNULL(SUM(h.horas_extra * t.precio_hora), 0) AS extras,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS liquidado_importe,
               IFNULL(SUM(CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN 0 WHEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) > 0 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END), 0) AS pendiente
        FROM horas h
        JOIN trabajadores t ON t.id = h.trabajador_id
        JOIN obras o ON o.id = h.obra_id
        {where_horas}
        GROUP BY o.id
        ORDER BY o.nombre
    """, parametros)
    obras_resumen = cur.fetchall()

    cur.execute(f"""
        SELECT h.id, h.fecha, t.nombre AS trabajador, o.nombre AS obra, o.cliente,
               h.horas, h.horas_extra, h.liquidado, h.fecha_liquidacion,
               t.precio_hora, h.horas_extra * t.precio_hora AS importe_extra,
               h.dinero_adelantado,
               CASE WHEN IFNULL(h.liquidado, 0) = 1 THEN 0 WHEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) > 0 THEN (h.horas_extra * t.precio_hora - h.dinero_adelantado) ELSE 0 END AS pendiente,
               h.observaciones
        FROM horas h
        JOIN trabajadores t ON t.id = h.trabajador_id
        JOIN obras o ON o.id = h.obra_id
        {where_horas}
        ORDER BY h.fecha DESC, h.id DESC
    """, parametros)
    registros = cur.fetchall()

    filtros = {"trabajador_id": trabajador_id, "obra_id": obra_id, "fecha": fecha, "mes": mes, "anio": anio}
    con.close()
    return render_template(
        "resumen.html",
        trabajadores=trabajadores_resumen,
        obras=obras_resumen,
        registros=registros,
        lista_trabajadores=lista_trabajadores,
        lista_obras=lista_obras,
        totales=totales,
        filtros=filtros,
    )


def abrir_navegador():
    webbrowser.open_new("http://127.0.0.1:8000")


if __name__ == "__main__":
    registrar_pid()
    crear_tablas()
    actualizar_bd()
    crear_backup("inicio")
    # El portal principal abre el navegador; se evita abrir esta app por separado.
    # threading.Timer(1.0, abrir_navegador).start()
    try:
        app.run(host="127.0.0.1", port=8000, debug=False, use_reloader=False)
    finally:
        borrar_pid()
