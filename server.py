# ChachaObras v2.0 – Flask + SQLite
### Construcciones y Reformas Chacha S.L.

---

## 🚀 Uso rápido

### Opción A — Doble clic (Windows)
```
iniciar.bat   ← doble clic, se abre el navegador solo
```

### Opción B — Terminal
```bash
pip install flask reportlab
python server.py
# Abre http://localhost:5757
```

---

## 📂 Estructura

```
chacha_flask/
├── server.py          ← Servidor Flask + SQLite + API REST
├── static/
│   └── index.html     ← Frontend (React + jsPDF)
├── chacha_obras.db    ← Base de datos SQLite (se crea sola)
├── backups/           ← Backups ZIP automáticos
├── requirements.txt
├── iniciar.bat        ← Arranque Windows
├── build_exe.bat      ← Generar .exe
└── README.md
```

---

## 🔌 API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /api/clientes | Listar clientes |
| POST | /api/clientes | Crear cliente |
| PUT | /api/clientes/:id | Actualizar cliente |
| DELETE | /api/clientes/:id | Eliminar cliente |
| GET | /api/productos | Listar catálogo |
| POST | /api/productos | Crear partida |
| GET | /api/presupuestos | Listar presupuestos |
| POST | /api/presupuestos | Nuevo presupuesto |
| PUT | /api/presupuestos/:id | Actualizar cabecera |
| DELETE | /api/presupuestos/:id | Eliminar + líneas |
| POST | /api/presupuestos/:id/convertir | → Factura |
| GET | /api/presupuestos/:id/lineas | Líneas del pres. |
| POST | /api/presupuestos/:id/lineas | Añadir línea |
| DELETE | /api/presupuestos/:id/lineas/:n | Borrar línea |
| GET | /api/facturas | Listar facturas |
| POST | /api/facturas | Nueva factura |
| GET | /api/facturas/:id/lineas | Líneas de factura |
| POST | /api/facturas/:id/lineas | Añadir línea |
| GET | /api/config | Configuración |
| PUT | /api/config | Guardar config |
| GET | /api/kpis | KPIs dashboard |
| POST | /api/backup | Crear backup ZIP |
| GET | /api/backups | Listar backups |
| GET | /api/backups/:file/download | Descargar backup |
| POST | /api/restore/:file | Restaurar backup |
| DELETE | /api/backups/:file | Eliminar backup |

---

## 💾 Backups

- Los backups son ZIP con el archivo `chacha_obras.db` completo
- Se guardan en `backups/` junto al servidor
- Se conservan los últimos **30** (configurable)
- Antes de restaurar se crea un backup automático de seguridad
- Descargables desde la interfaz como archivo `.zip`

---

## 📦 Generar ejecutable .exe

```
build_exe.bat
```
Requiere Python 3.10+ instalado. El `.exe` resultante en `dist/` ya incluye Flask y todo — solo necesita Python para la primera instalación de dependencias.

---

*ChachaObras v2.0 · Flask + SQLite · Puerto 5757*

## Actualizacion - Salir y guardar

Esta version incluye un boton nuevo en el menu lateral: **Salir y guardar**.

Al pulsarlo:
- Crea un backup final en la carpeta `backups`.
- Incluye la base SQLite `chacha_obras.db` y una copia JSON de los datos del navegador.
- Cierra el servidor local para que no quede la aplicacion abierta en segundo plano.

Para iniciar la aplicacion usa `ABRIR_APLICACION.bat` o `iniciar.bat`.
