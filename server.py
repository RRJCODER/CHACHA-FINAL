"""
╔══════════════════════════════════════════════════════════════╗
║   CONSTRUCCIONES Y REFORMAS CHACHA S.L.                      ║
║   Servidor local Flask + SQLite  ·  v2.0                     ║
╚══════════════════════════════════════════════════════════════╝
  Uso:  python server.py
  Web:  http://localhost:5757
"""

import sqlite3, os, sys, json, zipfile, shutil, threading, webbrowser
from datetime import datetime, date, timedelta
from pathlib import Path
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, abort

# ── Rutas ─────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE = Path(sys.executable).parent
else:
    BASE = Path(__file__).parent

DB_PATH     = BASE / "chacha_obras.db"
BACKUP_DIR  = BASE / "backups"
STATIC_DIR  = BASE / "static"
BACKUP_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

PORT = 5757

# ══════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id TEXT PRIMARY KEY, nombre TEXT NOT NULL,
            nif TEXT, dir TEXT, cp TEXT, pob TEXT,
            prov TEXT, tel TEXT, email TEXT
        );
        CREATE TABLE IF NOT EXISTS productos (
            id TEXT PRIMARY KEY, desc TEXT NOT NULL,
            familia TEXT, ud TEXT DEFAULT 'UD',
            precio REAL DEFAULT 0, iva REAL DEFAULT 0.21
        );
        CREATE TABLE IF NOT EXISTS presupuestos (
            id TEXT PRIMARY KEY, fecha TEXT NOT NULL,
            id_cliente TEXT, validez_dias INTEGER DEFAULT 90,
            ref_obra TEXT, estado TEXT DEFAULT 'Borrador',
            notas TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS lineas_pres (
            n_doc TEXT, linea INTEGER, id_prod TEXT,
            desc TEXT, ud TEXT, cant REAL DEFAULT 1,
            precio REAL DEFAULT 0, iva REAL DEFAULT 0.21,
            PRIMARY KEY(n_doc, linea)
        );
        CREATE TABLE IF NOT EXISTS facturas (
            id TEXT PRIMARY KEY, fecha TEXT NOT NULL,
            id_cliente TEXT, venc_dias INTEGER DEFAULT 30,
            pres_ref TEXT, estado TEXT DEFAULT 'BORRADOR',
            notas TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS lineas_fac (
            n_doc TEXT, linea INTEGER, id_prod TEXT,
            desc TEXT, ud TEXT, cant REAL DEFAULT 1,
            precio REAL DEFAULT 0, iva REAL DEFAULT 0.21,
            PRIMARY KEY(n_doc, linea)
        );
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY, value TEXT
        );
        """)
        # Seed si está vacío
        if conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0] == 0:
            _seed(conn)

def _seed(conn):
    clientes = [
        ("CLI-0001","JORGE RUIZ DIAZ","26253609Y","CALLE HUERTOS 1","23713","GUADALEN","JAEN","666649394","jorgeruiz@prueba.com"),
        ("CLI-0002","SERGIO ROMERO REYES","26258547R","CALLE ROMERO MERCHAN 3","14840","CASTRO DEL RIO","CORDOBA","665874123","sergiorome@prueba.com"),
        ("CLI-0003","STELA ORDOÑEZ POYATO","29857412G","CALLE TORRECILLA 24","14850","BAENA","CORDOBA","698521478","stela@prueba.com"),
        ("CLI-0004","RAFA RUIZ","28745147T","CALLE BAENA 4","14850","BAENA","CORDOBA","632587741","rafa@prueba.com"),
        ("CLI-0005","PEDRO","25241478F","CALLE MARTOS 1","74541","GUADALEN","JAEN","458741154","pedpe@prueba.com"),
        ("CLI-0006","ANTONIO MOLINA SERRANO","29476183K","CALLE OLIVO 12","23710","BAILEN","JAEN","678452193","antoniomolina@prueba.com"),
        ("CLI-0007","MARIA LOPEZ AGUILERA","31854729L","AVENIDA ANDALUCIA 45","14850","BAENA","CORDOBA","654789321","marialopez@prueba.com"),
        ("CLI-0008","FRANCISCO JIMENEZ TORRES","26548971M","CALLE REAL 8","23700","LINARES","JAEN","689741256","franciscojimenez@prueba.com"),
        ("CLI-0009","CARMEN NAVARRO RUIZ","30258741N","CALLE SAN JOSE 19","23600","MARTOS","JAEN","617852963","carmennavarro@prueba.com"),
        ("CLI-0010","RAUL GARCIA MORENO","28574196P","PLAZA MAYOR 3","14003","CORDOBA","CORDOBA","699854123","raulgarcia@prueba.com"),
        ("CLI-0011","LUCIA RAMIREZ CAMPOS","32741859Q","CALLE LA FUENTE 27","14840","CASTRO DEL RIO","CORDOBA","632145879","luciaramirez@prueba.com"),
        ("CLI-0012","MANUEL ORTEGA PRIETO","25147896R","CALLE GRANADA 14","18001","GRANADA","GRANADA","687412536","manuelortega@prueba.com"),
        ("CLI-0013","ELENA SANCHEZ ROMERO","29751468S","AVENIDA JAEN 22","23713","GUADALEN","JAEN","645871239","elenasanchez@prueba.com"),
        ("CLI-0014","JUAN CARLOS VARGAS LEON","30587412T","CALLE CERVANTES 5","23001","JAEN","JAEN","666321987","juancarlosvargas@prueba.com"),
        ("CLI-0015","ISABEL MARTIN DELGADO","28475619V","CALLE SEVILLA 31","41004","SEVILLA","SEVILLA","674589632","isabelmartin@prueba.com"),
        ("CLI-0016","DAVID FERNANDEZ PEREZ","26985471W","CALLE ALAMOS 9","29012","MALAGA","MALAGA","631478526","davidfernandez@prueba.com"),
        ("CLI-0017","ANA BELEN CASTILLO MORA","31269854X","AVENIDA DEL PARQUE 17","23400","UBEDA","JAEN","698745123","anacastillo@prueba.com"),
        ("CLI-0018","MIGUEL ANGEL REYES CANO","27589641Y","CALLE NUEVA 6","14900","LUCENA","CORDOBA","652369874","miguelreyes@prueba.com"),
        ("CLI-0019","ROCIO HIDALGO FUENTES","30124578Z","CALLE VIRGEN DEL CARMEN 11","23740","ANDUJAR","JAEN","619874563","rociohidalgo@prueba.com"),
        ("CLI-0020","PABLO MEDINA GUTIERREZ","28693147A","CALLE SAN ANTONIO 25","14600","MONTORO","CORDOBA","675412398","pablomedina@prueba.com"),
    ]
    conn.executemany("INSERT INTO clientes VALUES(?,?,?,?,?,?,?,?,?)", clientes)

    productos = [
        ("PRO-0013","Enlucido de yeso en paredes","Albañilería","M2",18,0.21),
        ("PRO-0014","Enfoscado de mortero en paredes","Albañilería","M2",24,0.21),
        ("PRO-0015","Colocación de rodapié cerámico","Albañilería","M",9.5,0.21),
        ("PRO-0016","Colocación de gres porcelánico","Solería","M2",32,0.21),
        ("PRO-0017","Colocación de azulejo baño","Alicatados","M2",29,0.21),
        ("PRO-0018","Colocación de azulejo cocina","Alicatados","M2",28,0.21),
        ("PRO-0019","Demolición de tabique interior","Demoliciones","M2",16,0.21),
        ("PRO-0020","Retirada de escombros a contenedor","Demoliciones","M3",38,0.21),
        ("PRO-0021","Alquiler de contenedor de obra","Demoliciones","UD",185,0.21),
        ("PRO-0022","Instalación de punto de agua","Fontanería","UD",95,0.21),
        ("PRO-0023","Instalación de punto de desagüe","Fontanería","UD",85,0.21),
        ("PRO-0024","Sustitución de grifo monomando","Fontanería","UD",45,0.21),
        ("PRO-0025","Instalación de inodoro","Fontanería","UD",120,0.21),
        ("PRO-0026","Instalación de lavabo con mueble","Fontanería","UD",140,0.21),
        ("PRO-0027","Instalación de plato de ducha","Fontanería","UD",180,0.21),
        ("PRO-0028","Instalación de mampara de ducha","Fontanería","UD",150,0.21),
        ("PRO-0029","Punto de luz sencillo","Electricidad","UD",55,0.21),
        ("PRO-0030","Punto de enchufe","Electricidad","UD",60,0.21),
        ("PRO-0031","Instalación de interruptor","Electricidad","UD",35,0.21),
        ("PRO-0032","Instalación de cuadro eléctrico básico","Electricidad","UD",320,0.21),
        ("PRO-0033","Pintura plástica blanca en paredes","Pintura","M2",7.5,0.21),
        ("PRO-0034","Pintura plástica color en paredes","Pintura","M2",8.5,0.21),
        ("PRO-0035","Pintura de techos","Pintura","M2",8,0.21),
        ("PRO-0036","Reparación de grietas y desperfectos","Pintura","M2",12,0.21),
        ("PRO-0037","Colocación de puerta interior","Carpintería","UD",165,0.21),
        ("PRO-0038","Colocación de premarco de madera","Carpintería","UD",75,0.21),
        ("PRO-0039","Instalación de tarima flotante","Carpintería","M2",21,0.21),
        ("PRO-0040","Colocación de zócalo laminado","Carpintería","M",7.5,0.21),
        ("PRO-0041","Limpieza final de obra","Limpieza","HORAS",16,0.21),
        ("PRO-0042","Mano de obra oficial albañil","Mano de obra","HORAS",24,0.21),
    ]
    conn.executemany("INSERT INTO productos VALUES(?,?,?,?,?,?)", productos)

    conn.executemany("INSERT OR IGNORE INTO config VALUES(?,?)", [
        ("prox_pres","0"),("prox_fac","0"),
        ("iva_def","0.21"),("validez_dias","90"),
        ("venc_dias","30"),("max_backups","30"),
        ("auto_backup","1"),
    ])
    conn.commit()

# ══════════════════════════════════════════════════════════════
# FLASK APP
# ══════════════════════════════════════════════════════════════
app = Flask(__name__, static_folder=str(STATIC_DIR))

def rows_to_list(rows):
    return [dict(r) for r in rows]

def ok(data=None, **kw):
    return jsonify({"ok": True, "data": data, **kw})

def err(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code

# ── Servir frontend ──────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(str(STATIC_DIR / "js"), filename)

# ══════════════════════════════════════════════════════════════
# API: CLIENTES
# ══════════════════════════════════════════════════════════════
@app.route("/api/clientes", methods=["GET"])
def get_clientes():
    q = "%" + request.args.get("q", "").lower() + "%"
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM clientes WHERE lower(nombre) LIKE ? OR nif LIKE ? ORDER BY nombre",
            (q, q)).fetchall()
    return ok(rows_to_list(rows))

@app.route("/api/clientes", methods=["POST"])
def create_cliente():
    d = request.json
    if not d.get("nombre"):
        return err("nombre requerido")
    with get_db() as conn:
        # Generar ID
        row = conn.execute("SELECT id FROM clientes ORDER BY id DESC LIMIT 1").fetchone()
        n = int(row[0].split("-")[1]) + 1 if row else 1
        d["id"] = f"CLI-{n:04d}"
        conn.execute(
            "INSERT INTO clientes VALUES(:id,:nombre,:nif,:dir,:cp,:pob,:prov,:tel,:email)",
            {k: d.get(k, "") for k in ["id","nombre","nif","dir","cp","pob","prov","tel","email"]})
    return ok(d), 201

@app.route("/api/clientes/<id_>", methods=["PUT"])
def update_cliente(id_):
    d = request.json
    d["id"] = id_
    with get_db() as conn:
        conn.execute("""UPDATE clientes SET nombre=:nombre,nif=:nif,dir=:dir,
            cp=:cp,pob=:pob,prov=:prov,tel=:tel,email=:email WHERE id=:id""", d)
    return ok(d)

@app.route("/api/clientes/<id_>", methods=["DELETE"])
def delete_cliente(id_):
    with get_db() as conn:
        conn.execute("DELETE FROM clientes WHERE id=?", (id_,))
    return ok()

# ══════════════════════════════════════════════════════════════
# API: PRODUCTOS
# ══════════════════════════════════════════════════════════════
@app.route("/api/productos", methods=["GET"])
def get_productos():
    q = "%" + request.args.get("q", "").lower() + "%"
    fam = request.args.get("familia", "")
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM productos WHERE lower(desc) LIKE ? ORDER BY familia,desc", (q,)).fetchall()
    data = rows_to_list(rows)
    if fam:
        data = [r for r in data if r["familia"] == fam]
    return ok(data)

@app.route("/api/productos/familias", methods=["GET"])
def get_familias():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT familia FROM productos ORDER BY familia").fetchall()
    return ok([r[0] for r in rows])

@app.route("/api/productos", methods=["POST"])
def create_producto():
    d = request.json
    if not d.get("desc"):
        return err("desc requerido")
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM productos ORDER BY CAST(SUBSTR(id,5) AS INTEGER) DESC LIMIT 1").fetchone()
        n = int(row[0].split("-")[1]) + 1 if row else 13
        d["id"] = f"PRO-{n:04d}"
        conn.execute(
            "INSERT INTO productos VALUES(:id,:desc,:familia,:ud,:precio,:iva)",
            {k: d.get(k, 0 if k in ["precio","iva"] else "") for k in ["id","desc","familia","ud","precio","iva"]})
    return ok(d), 201

@app.route("/api/productos/<id_>", methods=["PUT"])
def update_producto(id_):
    d = request.json
    d["id"] = id_
    with get_db() as conn:
        conn.execute(
            "UPDATE productos SET desc=:desc,familia=:familia,ud=:ud,precio=:precio,iva=:iva WHERE id=:id", d)
    return ok(d)

@app.route("/api/productos/<id_>", methods=["DELETE"])
def delete_producto(id_):
    with get_db() as conn:
        conn.execute("DELETE FROM productos WHERE id=?", (id_,))
    return ok()

# ══════════════════════════════════════════════════════════════
# API: PRESUPUESTOS
# ══════════════════════════════════════════════════════════════
def _doc_seq(doc_id, prefix):
    try:
        parts = str(doc_id or "").split("-")
        if len(parts) == 3 and parts[0] == prefix:
            return int(parts[2])
    except Exception:
        pass
    return -1

def _next_doc_number(conn, table, prefix, cfg_key):
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    if count == 0:
        return 0
    row = conn.execute("SELECT value FROM config WHERE key=?", (cfg_key,)).fetchone()
    try:
        cfg = int(row[0]) if row else 0
    except Exception:
        cfg = 0
    ids = [r[0] for r in conn.execute(f"SELECT id FROM {table}").fetchall()]
    max_existing = max([_doc_seq(x, prefix) for x in ids] + [-1])
    return max(cfg, max_existing + 1)

@app.route("/api/presupuestos", methods=["GET"])
def get_presupuestos():
    q = "%" + request.args.get("q", "").lower() + "%"
    with get_db() as conn:
        rows = conn.execute("""
        SELECT p.*, c.nombre as nombre_cliente,
               COALESCE((SELECT SUM(l.cant*l.precio*(1+l.iva))
                         FROM lineas_pres l WHERE l.n_doc=p.id),0) as total
        FROM presupuestos p
        LEFT JOIN clientes c ON p.id_cliente=c.id
        WHERE lower(p.id) LIKE ? OR lower(c.nombre) LIKE ?
        ORDER BY p.created_at DESC
        """, (q, q)).fetchall()
    return ok(rows_to_list(rows))

@app.route("/api/presupuestos/<id_>", methods=["GET"])
def get_presupuesto(id_):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM presupuestos WHERE id=?", (id_,)).fetchone()
    if not row:
        return err("no encontrado", 404)
    return ok(dict(row))

@app.route("/api/presupuestos", methods=["POST"])
def create_presupuesto():
    with get_db() as conn:
        n = _next_doc_number(conn, "presupuestos", "PR", "prox_pres")
        id_ = f"PR-{date.today().year}-{n:04d}"
        while conn.execute("SELECT 1 FROM presupuestos WHERE id=?", (id_,)).fetchone():
            n += 1
            id_ = f"PR-{date.today().year}-{n:04d}"
        conn.execute("INSERT OR REPLACE INTO config VALUES('prox_pres',?)", (str(n+1),))
        d = request.json or {}
        cli_row = conn.execute("SELECT id FROM clientes LIMIT 1").fetchone()
        conn.execute("""INSERT INTO presupuestos(id,fecha,id_cliente,validez_dias,ref_obra,estado,notas)
            VALUES(?,?,?,?,?,?,?)""",
            (id_, d.get("fecha", date.today().isoformat()),
             d.get("id_cliente", cli_row[0] if cli_row else ""),
             d.get("validez_dias", 90),
             d.get("ref_obra", ""), d.get("estado", "Borrador"), d.get("notas", "")))
    return ok({"id": id_, "next": n + 1}), 201

@app.route("/api/presupuestos/<id_>", methods=["PUT"])
def update_presupuesto(id_):
    d = request.json
    with get_db() as conn:
        conn.execute("""UPDATE presupuestos SET fecha=:fecha,id_cliente=:id_cliente,
            validez_dias=:validez_dias,ref_obra=:ref_obra,estado=:estado,notas=:notas
            WHERE id=:id""",
            {**d, "id": id_})
    return ok(d)

@app.route("/api/presupuestos/<id_>", methods=["DELETE"])
def delete_presupuesto(id_):
    with get_db() as conn:
        conn.execute("DELETE FROM lineas_pres WHERE n_doc=?", (id_,))
        conn.execute("DELETE FROM presupuestos WHERE id=?", (id_,))
        count = conn.execute("SELECT COUNT(*) FROM presupuestos").fetchone()[0]
        if count == 0:
            conn.execute("INSERT OR REPLACE INTO config VALUES('prox_pres','0')")
    return ok()

@app.route("/api/presupuestos/<id_>/convertir", methods=["POST"])
def convertir_presupuesto(id_):
    with get_db() as conn:
        pres = conn.execute("SELECT * FROM presupuestos WHERE id=?", (id_,)).fetchone()
        if not pres:
            return err("presupuesto no encontrado", 404)
        lineas = conn.execute(
            "SELECT * FROM lineas_pres WHERE n_doc=? ORDER BY linea", (id_,)).fetchall()
        n = _next_doc_number(conn, "facturas", "F", "prox_fac")
        fac_id = f"F-{date.today().year}-{n:04d}"
        while conn.execute("SELECT 1 FROM facturas WHERE id=?", (fac_id,)).fetchone():
            n += 1
            fac_id = f"F-{date.today().year}-{n:04d}"
        venc_row = conn.execute("SELECT value FROM config WHERE key='venc_dias'").fetchone()
        venc = int(venc_row[0]) if venc_row else 30
        conn.execute("INSERT OR REPLACE INTO config VALUES('prox_fac',?)", (str(n+1),))
        conn.execute("""INSERT INTO facturas(id,fecha,id_cliente,venc_dias,pres_ref,estado,notas)
            VALUES(?,?,?,?,?,?,?)""",
            (fac_id, date.today().isoformat(), pres["id_cliente"],
             venc, id_, "BORRADOR", ""))
        for i, l in enumerate(lineas, 1):
            conn.execute("""INSERT INTO lineas_fac VALUES(?,?,?,?,?,?,?,?)""",
                (fac_id, i, l["id_prod"], l["desc"], l["ud"],
                 l["cant"], l["precio"], l["iva"]))
    return ok({"id": fac_id, "next": n + 1}), 201

# ── Líneas presupuesto ────────────────────────────────────────
@app.route("/api/presupuestos/<id_>/lineas", methods=["GET"])
def get_lineas_pres(id_):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM lineas_pres WHERE n_doc=? ORDER BY linea", (id_,)).fetchall()
    return ok(rows_to_list(rows))

@app.route("/api/presupuestos/<id_>/lineas", methods=["POST"])
def add_linea_pres(id_):
    d = request.json
    with get_db() as conn:
        row = conn.execute(
            "SELECT MAX(linea) FROM lineas_pres WHERE n_doc=?", (id_,)).fetchone()
        n = (row[0] or 0) + 1
        conn.execute(
            "INSERT INTO lineas_pres VALUES(?,?,?,?,?,?,?,?)",
            (id_, n, d.get("id_prod",""), d.get("desc",""), d.get("ud","UD"),
             float(d.get("cant",1)), float(d.get("precio",0)), float(d.get("iva",0.21))))
    return ok({"linea": n}), 201

@app.route("/api/presupuestos/<id_>/lineas/<int:linea>", methods=["PUT"])
def update_linea_pres(id_, linea):
    d = request.json or {}
    with get_db() as conn:
        conn.execute("""UPDATE lineas_pres
            SET id_prod=?, desc=?, ud=?, cant=?, precio=?, iva=?
            WHERE n_doc=? AND linea=?""",
            (d.get("id_prod",""), d.get("desc",""), d.get("ud","UD"),
             float(d.get("cant",1)), float(d.get("precio",0)), float(d.get("iva",0.21)),
             id_, linea))
    return ok({"linea": linea})

@app.route("/api/presupuestos/<id_>/lineas/<int:linea>", methods=["DELETE"])
def del_linea_pres(id_, linea):
    with get_db() as conn:
        conn.execute("DELETE FROM lineas_pres WHERE n_doc=? AND linea=?", (id_, linea))
    return ok()

# ══════════════════════════════════════════════════════════════
# API: FACTURAS
# ══════════════════════════════════════════════════════════════
@app.route("/api/facturas", methods=["GET"])
def get_facturas():
    q = "%" + request.args.get("q", "").lower() + "%"
    with get_db() as conn:
        rows = conn.execute("""
        SELECT f.*, c.nombre as nombre_cliente,
               COALESCE((SELECT SUM(l.cant*l.precio*(1+l.iva))
                         FROM lineas_fac l WHERE l.n_doc=f.id),0) as total
        FROM facturas f
        LEFT JOIN clientes c ON f.id_cliente=c.id
        WHERE lower(f.id) LIKE ? OR lower(c.nombre) LIKE ?
        ORDER BY f.created_at DESC
        """, (q, q)).fetchall()
    return ok(rows_to_list(rows))

@app.route("/api/facturas/<id_>", methods=["GET"])
def get_factura(id_):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM facturas WHERE id=?", (id_,)).fetchone()
    if not row:
        return err("no encontrada", 404)
    return ok(dict(row))

@app.route("/api/facturas", methods=["POST"])
def create_factura():
    with get_db() as conn:
        n = _next_doc_number(conn, "facturas", "F", "prox_fac")
        id_ = f"F-{date.today().year}-{n:04d}"
        while conn.execute("SELECT 1 FROM facturas WHERE id=?", (id_,)).fetchone():
            n += 1
            id_ = f"F-{date.today().year}-{n:04d}"
        conn.execute("INSERT OR REPLACE INTO config VALUES('prox_fac',?)", (str(n+1),))
        d = request.json or {}
        cli_row = conn.execute("SELECT id FROM clientes LIMIT 1").fetchone()
        conn.execute("""INSERT INTO facturas(id,fecha,id_cliente,venc_dias,pres_ref,estado,notas)
            VALUES(?,?,?,?,?,?,?)""",
            (id_, d.get("fecha", date.today().isoformat()),
             d.get("id_cliente", cli_row[0] if cli_row else ""),
             d.get("venc_dias", 30),
             d.get("pres_ref",""), d.get("estado","BORRADOR"), d.get("notas","")))
    return ok({"id": id_, "next": n + 1}), 201

@app.route("/api/facturas/<id_>", methods=["PUT"])
def update_factura(id_):
    d = request.json
    with get_db() as conn:
        conn.execute("""UPDATE facturas SET fecha=:fecha,id_cliente=:id_cliente,
            venc_dias=:venc_dias,pres_ref=:pres_ref,estado=:estado,notas=:notas
            WHERE id=:id""", {**d, "id": id_})
    return ok(d)

@app.route("/api/facturas/<id_>", methods=["DELETE"])
def delete_factura(id_):
    with get_db() as conn:
        conn.execute("DELETE FROM lineas_fac WHERE n_doc=?", (id_,))
        conn.execute("DELETE FROM facturas WHERE id=?", (id_,))
        count = conn.execute("SELECT COUNT(*) FROM facturas").fetchone()[0]
        if count == 0:
            conn.execute("INSERT OR REPLACE INTO config VALUES('prox_fac','0')")
    return ok()

# ── Líneas factura ────────────────────────────────────────────
@app.route("/api/facturas/<id_>/lineas", methods=["GET"])
def get_lineas_fac(id_):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM lineas_fac WHERE n_doc=? ORDER BY linea", (id_,)).fetchall()
    return ok(rows_to_list(rows))

@app.route("/api/facturas/<id_>/lineas", methods=["POST"])
def add_linea_fac(id_):
    d = request.json
    with get_db() as conn:
        row = conn.execute(
            "SELECT MAX(linea) FROM lineas_fac WHERE n_doc=?", (id_,)).fetchone()
        n = (row[0] or 0) + 1
        conn.execute(
            "INSERT INTO lineas_fac VALUES(?,?,?,?,?,?,?,?)",
            (id_, n, d.get("id_prod",""), d.get("desc",""), d.get("ud","UD"),
             float(d.get("cant",1)), float(d.get("precio",0)), float(d.get("iva",0.21))))
    return ok({"linea": n}), 201

@app.route("/api/facturas/<id_>/lineas/<int:linea>", methods=["PUT"])
def update_linea_fac(id_, linea):
    d = request.json or {}
    with get_db() as conn:
        conn.execute("""UPDATE lineas_fac
            SET id_prod=?, desc=?, ud=?, cant=?, precio=?, iva=?
            WHERE n_doc=? AND linea=?""",
            (d.get("id_prod",""), d.get("desc",""), d.get("ud","UD"),
             float(d.get("cant",1)), float(d.get("precio",0)), float(d.get("iva",0.21)),
             id_, linea))
    return ok({"linea": linea})

@app.route("/api/facturas/<id_>/lineas/<int:linea>", methods=["DELETE"])
def del_linea_fac(id_, linea):
    with get_db() as conn:
        conn.execute("DELETE FROM lineas_fac WHERE n_doc=? AND linea=?", (id_, linea))
    return ok()

# ══════════════════════════════════════════════════════════════
# API: CONFIG
# ══════════════════════════════════════════════════════════════
@app.route("/api/config", methods=["GET"])
def get_config():
    with get_db() as conn:
        rows = conn.execute("SELECT key,value FROM config").fetchall()
    return ok({r["key"]: r["value"] for r in rows})

@app.route("/api/config", methods=["PUT"])
def update_config():
    d = request.json
    with get_db() as conn:
        for k, v in d.items():
            conn.execute("INSERT OR REPLACE INTO config VALUES(?,?)", (k, str(v)))
    return ok()

# ── Guardar PDF en carpeta configurada ───────────────────────
@app.route("/api/save-pdf", methods=["POST"])
def save_pdf():
    """Recibe PDF en base64 y lo guarda en la carpeta configurada."""
    import base64, re as _re
    d = request.json
    tipo      = d.get("tipo", "DOCUMENTO")        # PRESUPUESTO | FACTURA
    doc_id    = d.get("doc_id", "DOC")
    fecha     = d.get("fecha", date.today().isoformat())
    cliente   = d.get("cliente_nombre", "")
    pdf_b64   = d.get("pdf_base64", "")

    # Carpeta base según tipo
    cfg_key   = "pdf_folder_presupuesto" if tipo == "PRESUPUESTO" else "pdf_folder_factura"
    with get_db() as conn:
        row = conn.execute("SELECT value FROM config WHERE key=?", (cfg_key,)).fetchone()
    base_folder = row[0] if (row and row[0]) else str(BASE / ("PDFs_Presupuestos" if tipo=="PRESUPUESTO" else "PDFs_Facturas"))

    # Subcarpeta año-mes
    year_month = fecha[:7] if len(fecha) >= 7 else date.today().strftime("%Y-%m")
    out_dir = Path(base_folder) / year_month
    out_dir.mkdir(parents=True, exist_ok=True)

    # Nombre fichero: fecha_cliente_docid.pdf
    safe_cli  = _re.sub(r'[^\w\s-]', '', cliente).strip().replace(' ', '_')[:30]
    safe_id   = doc_id.replace("/","_").replace("\\","_")
    fname     = f"{fecha}_{safe_cli}_{safe_id}.pdf"
    out_path  = out_dir / fname

    # Decodificar y guardar
    try:
        pdf_bytes = base64.b64decode(pdf_b64)
        with open(out_path, "wb") as f:
            f.write(pdf_bytes)
        return ok({"path": str(out_path), "filename": fname})
    except Exception as e:
        return err(f"Error guardando PDF: {e}")

@app.route("/api/pdf-folders", methods=["GET"])
def get_pdf_folders():
    with get_db() as conn:
        pres = conn.execute("SELECT value FROM config WHERE key='pdf_folder_presupuesto'").fetchone()
        fac  = conn.execute("SELECT value FROM config WHERE key='pdf_folder_factura'").fetchone()
    return ok({
        "presupuesto": pres[0] if pres else "",
        "factura":     fac[0]  if fac  else "",
        "default_pres": str(BASE / "PDFs_Presupuestos"),
        "default_fac":  str(BASE / "PDFs_Facturas"),
    })

# ══════════════════════════════════════════════════════════════
# API: KPIs
# ══════════════════════════════════════════════════════════════
@app.route("/api/kpis", methods=["GET"])
def get_kpis():
    with get_db() as conn:
        n_cli  = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        n_prod = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
        n_pres = conn.execute("SELECT COUNT(*) FROM presupuestos").fetchone()[0]
        n_fac  = conn.execute("SELECT COUNT(*) FROM facturas").fetchone()[0]
        b_pres = conn.execute(
            "SELECT COUNT(*) FROM presupuestos WHERE estado='Borrador'").fetchone()[0]
        b_fac  = conn.execute(
            "SELECT COUNT(*) FROM facturas WHERE estado='BORRADOR'").fetchone()[0]
        tot_pres = conn.execute(
            "SELECT COALESCE(SUM(cant*precio*(1+iva)),0) FROM lineas_pres").fetchone()[0]
        tot_fac  = conn.execute(
            "SELECT COALESCE(SUM(cant*precio*(1+iva)),0) FROM lineas_fac").fetchone()[0]
        last5_pres = conn.execute("""
            SELECT p.id,c.nombre as cliente,
                   COALESCE((SELECT SUM(l.cant*l.precio*(1+l.iva)) FROM lineas_pres l WHERE l.n_doc=p.id),0) as total,
                   p.estado
            FROM presupuestos p LEFT JOIN clientes c ON p.id_cliente=c.id
            ORDER BY p.created_at DESC LIMIT 5""").fetchall()
        last5_fac = conn.execute("""
            SELECT f.id,c.nombre as cliente,
                   COALESCE((SELECT SUM(l.cant*l.precio*(1+l.iva)) FROM lineas_fac l WHERE l.n_doc=f.id),0) as total,
                   f.estado
            FROM facturas f LEFT JOIN clientes c ON f.id_cliente=c.id
            ORDER BY f.created_at DESC LIMIT 5""").fetchall()
    return ok({
        "n_cli": n_cli, "n_prod": n_prod, "n_pres": n_pres, "n_fac": n_fac,
        "b_pres": b_pres, "b_fac": b_fac,
        "tot_pres": round(tot_pres, 2), "tot_fac": round(tot_fac, 2),
        "last5_pres": rows_to_list(last5_pres),
        "last5_fac": rows_to_list(last5_fac),
    })

# ══════════════════════════════════════════════════════════════
# API: BACKUPS
# ══════════════════════════════════════════════════════════════
def _crear_backup_archivo(local_json=None, motivo="manual"):
    """Crea un backup ZIP de la base SQLite y, si llega, del JSON local del navegador."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = BACKUP_DIR / f"chacha_backup_{ts}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        if DB_PATH.exists():
            z.write(DB_PATH, "chacha_obras.db")
        z.writestr("backup_info.json", json.dumps({
            "timestamp": ts,
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "motivo": motivo,
            "includes_local_json": local_json is not None
        }, ensure_ascii=False, indent=2))
        if local_json is not None:
            if isinstance(local_json, str):
                z.writestr("chacha_local.json", local_json)
            else:
                z.writestr("chacha_local.json", json.dumps(local_json, ensure_ascii=False, indent=2))
    _cleanup_backups()
    return {"file": str(zip_path), "filename": zip_path.name, "ts": ts}

@app.route("/api/backup", methods=["POST"])
def create_backup():
    payload = request.get_json(silent=True) or {}
    local_json = payload.get("local_json")
    return ok(_crear_backup_archivo(local_json, motivo="manual"))

@app.route("/api/sync-local", methods=["POST"])
def sync_local():
    payload = request.get_json(silent=True) or {}
    data = payload.get("local_json", payload)
    if isinstance(data, str):
        data = json.loads(data)
    if not isinstance(data, dict):
        return err("json local no valido", 400)

    # Backup previo automatico antes de sobreescribir la base del servidor.
    create_backup()

    def pick(d, *keys, default=""):
        for k in keys:
            if isinstance(d, dict) and d.get(k) not in (None, ""):
                return d.get(k)
        return default

    def num(v, default=0):
        try:
            return float(v)
        except Exception:
            return default

    def entero(v, default=0):
        try:
            return int(v)
        except Exception:
            return default

    with get_db() as conn:
        conn.execute("DELETE FROM lineas_fac")
        conn.execute("DELETE FROM lineas_pres")
        conn.execute("DELETE FROM facturas")
        conn.execute("DELETE FROM presupuestos")
        conn.execute("DELETE FROM productos")
        conn.execute("DELETE FROM clientes")

        for c in data.get("clis", []):
            conn.execute(
                "INSERT OR REPLACE INTO clientes VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    pick(c, "id"),
                    pick(c, "nombre"),
                    pick(c, "nif"),
                    pick(c, "dir"),
                    pick(c, "cp"),
                    pick(c, "pob"),
                    pick(c, "prov"),
                    pick(c, "tel"),
                    pick(c, "email"),
                ),
            )

        for p in data.get("prods", []):
            conn.execute(
                "INSERT OR REPLACE INTO productos VALUES(?,?,?,?,?,?)",
                (
                    pick(p, "id"),
                    pick(p, "desc"),
                    pick(p, "familia"),
                    pick(p, "ud", default="UD"),
                    num(pick(p, "precio", default=0)),
                    num(pick(p, "iva", default=0.21), 0.21),
                ),
            )

        for p in data.get("presups", []):
            conn.execute(
                """INSERT OR REPLACE INTO presupuestos
                   (id,fecha,id_cliente,validez_dias,ref_obra,estado,notas,created_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (
                    pick(p, "id"),
                    pick(p, "fecha", default=date.today().isoformat()),
                    pick(p, "id_cliente", "idCliente"),
                    entero(pick(p, "validez_dias", "validezDias", default=90), 90),
                    pick(p, "ref_obra", "refObra"),
                    pick(p, "estado", default="Borrador"),
                    pick(p, "notas"),
                    pick(p, "created_at", "createdAt", default=datetime.now().isoformat()),
                ),
            )

        for l in data.get("linesPres", []):
            conn.execute(
                "INSERT OR REPLACE INTO lineas_pres VALUES(?,?,?,?,?,?,?,?)",
                (
                    pick(l, "n_doc", "nDoc"),
                    entero(pick(l, "linea", default=1), 1),
                    pick(l, "id_prod", "idProd"),
                    pick(l, "desc"),
                    pick(l, "ud", default="UD"),
                    num(pick(l, "cant", default=1), 1),
                    num(pick(l, "precio", default=0)),
                    num(pick(l, "iva", default=0.21), 0.21),
                ),
            )

        for f in data.get("facts", []):
            conn.execute(
                """INSERT OR REPLACE INTO facturas
                   (id,fecha,id_cliente,venc_dias,pres_ref,estado,notas,created_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (
                    pick(f, "id"),
                    pick(f, "fecha", default=date.today().isoformat()),
                    pick(f, "id_cliente", "idCliente"),
                    entero(pick(f, "venc_dias", "vencDias", default=30), 30),
                    pick(f, "pres_ref", "presRef"),
                    pick(f, "estado", default="BORRADOR"),
                    pick(f, "notas"),
                    pick(f, "created_at", "createdAt", default=datetime.now().isoformat()),
                ),
            )

        for l in data.get("linesFac", []):
            conn.execute(
                "INSERT OR REPLACE INTO lineas_fac VALUES(?,?,?,?,?,?,?,?)",
                (
                    pick(l, "n_doc", "nDoc"),
                    entero(pick(l, "linea", default=1), 1),
                    pick(l, "id_prod", "idProd"),
                    pick(l, "desc"),
                    pick(l, "ud", default="UD"),
                    num(pick(l, "cant", default=1), 1),
                    num(pick(l, "precio", default=0)),
                    num(pick(l, "iva", default=0.21), 0.21),
                ),
            )

        cfg = data.get("config", {}) or {}
        cfg_map = {
            "prox_pres": pick(cfg, "proxPres", "prox_pres", default="0"),
            "prox_fac": pick(cfg, "proxFac", "prox_fac", default="0"),
            "iva_def": pick(cfg, "ivaDef", "iva_def", default="0.21"),
            "validez_dias": pick(cfg, "validezDias", "validez_dias", default="90"),
            "venc_dias": pick(cfg, "vencDias", "venc_dias", default="30"),
        }
        pres_nums = [_doc_seq(pick(p, "id"), "PR") for p in data.get("presups", [])]
        fac_nums = [_doc_seq(pick(f, "id"), "F") for f in data.get("facts", [])]
        cfg_map["prox_pres"] = max(entero(cfg_map.get("prox_pres"), 0), max(pres_nums) + 1) if pres_nums else 0
        cfg_map["prox_fac"] = max(entero(cfg_map.get("prox_fac"), 0), max(fac_nums) + 1) if fac_nums else 0
        emp = data.get("empresa", {}) or {}
        for k, v in emp.items():
            cfg_map[f"emp_{k}"] = v
        for k, v in cfg_map.items():
            conn.execute("INSERT OR REPLACE INTO config VALUES(?,?)", (k, str(v)))

    return ok({"message": "Cambios locales copiados al servidor"})

def _cleanup_backups():
    with get_db() as conn:
        row = conn.execute("SELECT value FROM config WHERE key='max_backups'").fetchone()
    max_b = int(row[0]) if row else 30
    backups = sorted(BACKUP_DIR.glob("chacha_backup_*.zip"))
    while len(backups) > max_b:
        backups[0].unlink()
        backups = backups[1:]

@app.route("/api/backups", methods=["GET"])
def list_backups():
    backups = sorted(BACKUP_DIR.glob("chacha_backup_*.zip"), reverse=True)
    result = []
    for bp in backups:
        ts_str = bp.stem.replace("chacha_backup_", "")
        try:
            dt = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            label = dt.strftime("%d/%m/%Y  %H:%M:%S")
        except:
            label = ts_str
        result.append({
            "label": label,
            "size_kb": bp.stat().st_size // 1024,
            "filename": bp.name,
            "path": str(bp)
        })
    return ok(result)

@app.route("/api/backups/<filename>/download", methods=["GET"])
def download_backup(filename):
    return send_from_directory(str(BACKUP_DIR), filename, as_attachment=True)

@app.route("/api/backups/<filename>", methods=["DELETE"])
def delete_backup(filename):
    p = BACKUP_DIR / filename
    if p.exists():
        p.unlink()
    return ok()

@app.route("/api/restore/<filename>", methods=["POST"])
def restore_backup(filename):
    """Restaura la BD desde un backup. Hace backup previo automático."""
    create_backup()  # Backup de seguridad antes de restaurar
    zip_path = BACKUP_DIR / filename
    if not zip_path.exists():
        return err("backup no encontrado", 404)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extract("chacha_obras.db", BASE)
    return ok({"message": "Restaurado. Recarga la página."})


@app.route("/api/salir-seguro", methods=["POST"])
def salir_seguro():
    """Guarda backup final y apaga el servidor local."""
    payload = request.get_json(silent=True) or {}
    local_json = payload.get("local_json")
    backup = _crear_backup_archivo(local_json, motivo="salida_segura")

    shutdown = request.environ.get("werkzeug.server.shutdown")

    def apagar_servidor():
        try:
            if shutdown:
                shutdown()
        except Exception:
            pass
        # Con pythonw.exe no hay consola visible, pero esto garantiza que no quede el servidor abierto.
        os._exit(0)

    threading.Timer(1.0, apagar_servidor).start()
    return ok({"message": "Backup final creado. Cerrando servidor.", "backup": backup})

# ══════════════════════════════════════════════════════════════
# ARRANQUE
# ══════════════════════════════════════════════════════════════
def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == "__main__":
    init_db()
    print(f"""
╔══════════════════════════════════════════════╗
║  CHACHA OBRAS  ·  Servidor local v2.0        ║
║  http://localhost:{PORT}                      ║
║  Ctrl+C para detener                         ║
╚══════════════════════════════════════════════╝""")
    # El portal principal abre el navegador; se evita abrir esta app por separado.
    # threading.Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)
