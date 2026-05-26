# Tp2Docker-Diosquez-Hermosilla

Comandos desde cero:

Estos van en orden, uno por uno:
Limpiar todo lo anterior

docker stop flask-container mysql-container
docker rm flask-container mysql-container
docker network rm mi-red
docker rmi mi-flask


Levantar todo de nuevo

docker network create mi-red

docker run -d --name mysql-container --network mi-red -e MYSQL_ROOT_PASSWORD=1234 -e MYSQL_DATABASE=midb mysql:8

docker build -t mi-flask .

docker run -d --name flask-container --network mi-red -p 5000:5000 -e DB_HOST=mysql-container -e DB_USER=root -e DB_PASSWORD=1234 -e DB_NAME=midb mi-flask


curl http://localhost:5000/health
curl http://localhost:5000/db-status
curl -X POST http://localhost:5000/items -H "Content-Type: application/json" -d '{"nombre": "cosa1"}'
curl http://localhost:5000/items





Probar los endpoints
# Health
curl http://localhost:5000/health

# DB Status
curl http://localhost:5000/db-status

# Crear un item
curl -X POST http://localhost:5000/items -H "Content-Type: application/json" -d '{"nombre": "cosa1"}'

# Ver todos los items
curl http://localhost:5000/items





¿Qué es una imagen Docker?
Antes de tener un contenedor, necesitás una imagen.
Pensalo así:

La imagen es el molde.
El contenedor es el producto que sale de ese molde.

Si querés hacer 10 flanes, usás el mismo molde 10 veces. Con Docker igual: de una imagen podés crear muchos contenedores.

¿Qué construimos nosotros?
Construimos dos contenedores que trabajan juntos:
┌─────────────────────────────────────────┐
│              Red Docker                  │
│                                         │
│   ┌──────────────┐   ┌───────────────┐  │
│   │    Flask     │──▶│     MySQL     │  │
│   │  (la API)    │   │  (la base de  │  │
│   │              │   │    datos)     │  │
│   └──────────────┘   └───────────────┘  │
│          ▲                              │
└──────────│──────────────────────────────┘
           │
     Tu navegador

Contenedor 1 → La API hecha con Flask
Contenedor 2 → La base de datos MySQL
La red Docker → El cable que los conecta


¿Qué es Flask?
Flask es una librería de Python que convierte tu programa en un servidor web.
Sin Flask, tu programa Python no puede recibir pedidos de internet.
Con Flask, tu programa escucha y responde como cualquier página web.
Ejemplo cotidiano:

Cuando entrás a Google y buscás algo, tu navegador le manda un pedido a los servidores de Google y Google te devuelve una respuesta.
Flask hace exactamente eso, pero en pequeño y hecho por nosotros.


¿Qué es un endpoint?
Un endpoint es una dirección URL que el servidor entiende y sabe cómo responder.
Igual que en una empresa:


Querés hablar de ventas → vas al piso 1
Querés hablar de soporte → vas al piso 2


En nuestra API:


Querés saber si está viva → vas a /health
Querés saber si la base de datos funciona → vas a /db-status
Querés guardar algo → vas a /items
Querés ver lo guardado → también vas a /items



¿Qué son las variables de entorno?
Son notitas secretas que Docker le entrega al programa cuando arranca.
¿Por qué no escribimos la contraseña directo en el código?
Imaginá que escribís tu contraseña del banco en un papel y lo pegás en la puerta de tu casa. Cualquiera que vea el código vería la contraseña.
Con variables de entorno, el código dice:

"Yo no sé cuál es la contraseña. Me la van a dar cuando arranque."

Y Docker se la entrega en el momento. El código nunca tiene la contraseña escrita.

¿Qué es la red Docker?
Es un pasillo invisible entre contenedores.
Sin la red, el contenedor de Flask no puede hablar con el de MySQL. Estarían aislados como dos personas en cuartos sin puerta.
Con la red, Flask puede decir:

"Quiero conectarme a mysql-container"

Y Docker sabe exactamente a quién se refiere.


Explicación del código por bloques
Bloque 1 — Las importaciones
pythonimport os
import pymysql
from flask import Flask, jsonify, request

os → permite leer las variables de entorno que Docker entrega
pymysql → es el "traductor" entre Python y MySQL
Flask, jsonify, request → herramientas de Flask para crear la API


Bloque 2 — Crear la aplicación
pythonapp = Flask(__name__)
Esta línea crea la aplicación Flask. Es como encender el servidor. A partir de acá Flask empieza a existir y puede recibir pedidos.

Bloque 3 — La conexión a MySQL
pythondef get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
Esta función es como marcar un teléfono. Cada vez que necesitamos hablar con MySQL la llamamos.

host → dónde está MySQL (el nombre del contenedor)
user → el usuario de la base de datos
password → la contraseña
database → cuál de las bases de datos usar

Todo viene de variables de entorno, nunca escrito a mano.

Bloque 4 — Crear la tabla automáticamente
pythondef init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error iniciando DB: {e}")
Esta función corre una vez cuando Flask arranca y crea la tabla items si no existe.

IF NOT EXISTS → si la tabla ya existe, no hace nada. Si no existe, la crea.
AUTO_INCREMENT → el id se asigna solo, no hay que mandarlo
DEFAULT CURRENT_TIMESTAMP → la fecha se guarda sola


Bloque 5 — Endpoint /health
python@app.route("/health")
def health():
    return jsonify({"status": "ok"})
El más simple. No toca la base de datos. Solo dice que Flask está vivo.
Es como preguntarle a alguien: "¿Estás despierto?" y que responda "Sí".
Respuesta:
json{"status": "ok"}

Bloque 6 — Endpoint /db-status
python@app.route("/db-status")
def db_status():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"database": "connected"})
    except Exception as e:
        return jsonify({"database": "error", "detail": str(e)})
Intenta conectarse a MySQL. Si puede, dice connected. Si no puede, dice error.
Es como tocar el timbre de la base de datos y esperar respuesta.

try → intentá esto
except → si algo falla, hacé esto otro


Bloque 7 — Endpoint POST /items
python@app.route("/items", methods=["POST"])
def create_item():
    try:
        data = request.get_json()
        nombre = data["nombre"]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (nombre) VALUES (%s)", (nombre,))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "item creado", "nombre": nombre}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
Recibe un JSON con un nombre y lo guarda en la tabla.
Ejemplo de lo que recibe:
json{"nombre": "cosa1"}
Paso a paso:

Lee el JSON que mandaron
Saca el campo "nombre"
Se conecta a MySQL
Inserta el nombre en la tabla
Confirma el guardado con commit
Responde que se creó correctamente


Bloque 8 — Endpoint GET /items
python@app.route("/items", methods=["GET"])
def get_items():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, created_at FROM items")
        rows = cursor.fetchall()
        conn.close()
        items = [{"id": r[0], "nombre": r[1], "created_at": str(r[2])} for r in rows]
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
Devuelve todos los items guardados en la tabla.
Paso a paso:

Se conecta a MySQL
Pide todos los registros de la tabla
Los convierte a formato JSON
Los devuelve

Respuesta ejemplo:
json[
  {"id": 1, "nombre": "cosa1", "created_at": "2026-05-26 10:00:00"},
  {"id": 2, "nombre": "cosa2", "created_at": "2026-05-26 10:05:00"}
]

Bloque 9 — Arranque del servidor
pythonif __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
Estas son las últimas líneas que se ejecutan cuando arranca Flask:

init_db() → crea la tabla si no existe
app.run → arranca el servidor en el puerto 5000
host="0.0.0.0" → acepta conexiones desde cualquier lugar, no solo desde adentro del contenedor


Los archivos del proyecto
requirements.txt
flask
pymysql
Lista de librerías que Python necesita instalar. Sin esto Flask y pymysql no existen.

Dockerfile
dockerfileFROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]

FROM → usá Python 3.11 como base
WORKDIR → trabajá dentro de la carpeta /app
COPY → copiá los archivos al contenedor
RUN → instalá las librerías
CMD → cuando arranque el contenedor, ejecutá app.py


