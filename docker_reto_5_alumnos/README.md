Este proyecto proporciona un entorno Docker con una base de datos MySQL preparada y cargada a partir de los archivos datos/df_limpio.csv y datos/df_prediccion_prima.csv.

El cargador une ambos archivos por la columna ID y guarda los préstamos junto con las predicciones en la tabla prestamos. La base de datos utiliza almacenamiento persistente mediante un volumen Docker.

## Arranque

Para construir las imágenes y arrancar los servicios:

docker compose up --build

Para arrancar en segundo plano:

docker compose up -d

Para comprobar el estado:

docker compose ps

Servicios disponibles:

- API Flask: http://localhost:8000
- MySQL: localhost:3307
- Base de datos: creditos
- Usuario: clase
- Contraseña: clase123
- Tabla: prestamos

## Estructura
.
├── api/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── datos/
│   ├── df_limpio.csv
│   └── df_prediccion_prima.csv
│
├── loader/
│   ├── Dockerfile
│   ├── load_data.py
│   └── requirements.txt
│
├── docker-compose.yml
└── README.md
El trabajo sobre la API se realizará principalmente en:
api/main.py
La API conserva las rutas principales del proyecto: listado y consulta de préstamos, creación, actualización, eliminación y conversión de moneda.

## Persistencia
- Los datos de MySQL se almacenan en un volumen Docker y se mantienen aunque se detengan los contenedores:
docker compose down
- Para volver a levantar el entorno:
docker compose up
- Si se elimina el volumen:
docker compose down -v
la base de datos se volverá a generar a partir de los dos CSV en el siguiente arranque.

## Endpoints de la API

La API permite consultar y gestionar préstamos, así como obtener información relacionada con las predicciones.

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/prestamos` | Obtener préstamos |
| GET | `/api/v1/prestamos/<id>` | Consultar un préstamo por ID |
| POST | `/api/v1/prestamos` | Crear un préstamo |
| PATCH | `/api/v1/prestamos/<id>` | Actualizar un préstamo |
| DELETE | `/api/v1/prestamos/<id>` | Eliminar un préstamo |
| GET | `/api/v1/prestamos/<id>/conversion` | Convertir el importe a otra moneda |

## Ejemplos de uso

### Consultar todos los préstamos

```http
GET /api/v1/prestamos
```

### Consultar un préstamo concreto

```http
GET /api/v1/prestamos/123456
```

### Filtrar préstamos por impago

```http
GET /api/v1/prestamos?impago=1
```

### Filtrar préstamos por estudios

```http
GET /api/v1/prestamos?estudios=Universidad
```

### Limitar el número de resultados

```http
GET /api/v1/prestamos?limit=10
```

### Convertir un importe a dólares

```http
GET /api/v1/prestamos/123456/conversion?moneda=USD
```

Las respuestas de la API se devuelven en formato JSON.