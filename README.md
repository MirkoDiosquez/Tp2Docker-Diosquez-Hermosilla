# Tp2Docker-Diosquez-Hermosilla

Comandos desde cero:

Estos van en orden, uno por uno:
Limpiar todo lo anterior
bashdocker stop flask-container mysql-container
docker rm flask-container mysql-container
docker network rm mi-red
docker rmi mi-flask
Levantar todo de nuevo
bashdocker network create mi-red
bashdocker run -d --name mysql-container --network mi-red -e MYSQL_ROOT_PASSWORD=1234 -e MYSQL_DATABASE=midb mysql:8
bashdocker build -t mi-flask .
bashdocker run -d --name flask-container --network mi-red -p 5000:5000 -e DB_HOST=mysql-container -e DB_USER=root -e DB_PASSWORD=1234 -e DB_NAME=midb mi-flask
Probar los endpoints
bash# Health
curl http://localhost:5000/health

# DB Status
curl http://localhost:5000/db-status

# Crear un item
curl -X POST http://localhost:5000/items -H "Content-Type: application/json" -d '{"nombre": "cosa1"}'

# Ver todos los items
curl http://localhost:5000/items