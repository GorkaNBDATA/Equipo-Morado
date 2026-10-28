# Equipo-Morado

API REST de préstamos
1. Descripción

Esta API REST está desarrollada con Python y Flask. Permite consultar, crear, actualizar y eliminar préstamos almacenados en una base de datos SQLite.

Además, integra la API externa Frankfurter para convertir el importe inicial de un préstamo de euros a otra moneda.

2. Tecnologías utilizadas
Python
Flask
Flask-SQLAlchemy
SQLite
Pandas
Requests
API externa Frankfurter
3. Instalación y ejecución

Instalar las dependencias:

bash
pip install flask flask-sqlalchemy pandas requests


Crear la base de datos y cargar los datos del CSV:

bash
python bd_seguros.py


Iniciar la API:

bash
python app_seguros.py


La API estará disponible en http://127.0.0.1:5000.

4. Endpoints disponibles
Método	Endpoint	Descripción
GET	/	Comprueba que la API funciona.
GET	/api/v1/prestamos	Lista todos los préstamos.
GET	/api/v1/prestamos/<id>	Consulta un préstamo por ID.
POST	/api/v1/prestamos	Crea un préstamo nuevo.
PATCH	/api/v1/prestamos/<id>	Actualiza los datos de un préstamo.
DELETE	/api/v1/prestamos/<id>	Elimina un préstamo.
GET	/api/v1/prestamos/<id>/conversion?moneda=USD	Convierte el importe del préstamo a otra moneda.
5. Filtros de consulta

El endpoint de listado permite aplicar filtros opcionales:

impago: filtra por estado de impago.
estudios: filtra por nivel de estudios.
limit: limita el número de resultados.

Ejemplo:

GET /api/v1/prestamos?impago=0&estudios=Universitarios&limit=10

6. Ejemplo de creación de un préstamo

Petición:

POST /api/v1/prestamos

Cuerpo JSON:

json
{
    "Monto_Inicial": 10000,
    "Duracion": 36,
    "Edad": 30,
    "Ingresos": 2500,
    "Scoring_Crediticio": 700
}


La API genera automáticamente el ID y devuelve el préstamo creado con el código HTTP 201 Created.

7. Integración con una API externa

El endpoint de conversión consulta Frankfurter para obtener el tipo de cambio actual disponible.

Ejemplo:

GET /api/v1/prestamos/ABC123/conversion?moneda=USD

La respuesta incluye el ID del préstamo, el importe original en euros, la moneda de destino, el tipo de cambio y el importe convertido.

Si no se puede consultar la API externa, se devuelve un error 502 Bad Gateway.

8. Gestión de errores

Los errores HTTP se devuelven en formato JSON.

Ejemplo de préstamo no encontrado:

json
{
    "error": {
        "code": 404,
        "message": "Préstamo ABC123 no encontrado"
    }
}


Los principales códigos utilizados son:

200 OK: consulta o actualización correcta.
201 Created: préstamo creado.
204 No Content: préstamo eliminado.
400 Bad Request: petición incorrecta.
404 Not Found: préstamo inexistente.
502 Bad Gateway: error al consultar la API externa.