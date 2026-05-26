import os
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def init_db():
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

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/db-status")
def db_status():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"database": "connected"})
    except Exception as e:
        return jsonify({"database": "error", "detail": str(e)})

@app.route("/items", methods=["POST"])
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

@app.route("/items", methods=["GET"])
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

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)