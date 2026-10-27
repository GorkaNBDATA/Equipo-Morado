import uuid         

import requests
from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///prestamos.db"
db = SQLAlchemy(app)


class Prestamo(db.Model):
    __tablename__ = "prestamos"

    ID = db.Column(db.String(10), primary_key=True)
    Edad = db.Column(db.Integer)
    Ingresos = db.Column(db.Float)
    Monto_Inicial = db.Column(db.Float, nullable=False)
    Scoring_Crediticio = db.Column(db.Integer)
    Meses_Empleo = db.Column(db.Float)
    Num_Creditos = db.Column(db.Integer)
    Ratio_Interes = db.Column(db.Float)
    Duracion = db.Column(db.Float, nullable=False)
    Ratio_Deuda_Ingresos = db.Column(db.Float)
    Estudios = db.Column(db.String(50))
    Tipo_Jornada_Laboral = db.Column(db.String(50))
    Estado_Civil = db.Column(db.String(50))
    Posesion_Hipoteca = db.Column(db.Float)
    Personas_Cargo = db.Column(db.Float)
    Proposito = db.Column(db.String(50))
    Fiador = db.Column(db.Float)
    Impago = db.Column(db.Integer)
    Prima = db.Column(db.Float)


def a_diccionario(prestamo: Prestamo) -> dict:
    """Convierte un objeto Prestamo en un diccionario (para devolverlo como JSON)."""
    return {col.name: getattr(prestamo, col.name) for col in Prestamo.__table__.columns}


def buscar_prestamo(id: str) -> Prestamo:
    """Devuelve el préstamo o corta la petición con un 404."""
    prestamo = db.session.get(Prestamo, id)
    if prestamo is None:
        abort(404, description=f"Préstamo {id} no encontrado")
    return prestamo


#  Endpoints (recurso: prestamos) 

@app.get("/api/v1/prestamos")
def listar_prestamos():
    """Lista préstamos. Filtros opcionales: ?impago=0|1 &estudios=... &limit=..."""
    impago = request.args.get("impago", type=int)
    estudios = request.args.get("estudios")
    limit = request.args.get("limit", type=int)

    consulta = db.select(Prestamo)
    if impago is not None:
        consulta = consulta.where(Prestamo.Impago == impago)
    if estudios:
        consulta = consulta.where(Prestamo.Estudios == estudios)
    if limit:
        consulta = consulta.limit(limit)

    prestamos = db.session.execute(consulta).scalars().all()
    return jsonify([a_diccionario(p) for p in prestamos])


@app.get("/api/v1/prestamos/<id>")
def obtener_prestamo(id):
    """Devuelve un préstamo concreto."""
    return jsonify(a_diccionario(buscar_prestamo(id)))

@app.get("/")
def inicio():
    return jsonify({
        "mensaje": "API de préstamos funcionando correctamente",
        "endpoints": {
            "listar_prestamos": "/api/v1/prestamos",
            "consultar_prestamo": "/api/v1/prestamos/<id>"
        }
    })

@app.post("/api/v1/prestamos")
def crear_prestamo():
    """Crea un préstamo nuevo a partir de un JSON. Obligatorios: Monto_Inicial y Duracion."""
    datos = request.get_json(silent=True)
    if not datos or "Monto_Inicial" not in datos or "Duracion" not in datos:
        abort(400, description="Faltan campos obligatorios: Monto_Inicial y Duracion")

    # Nos quedamos solo con columnas que existan 
    columnas = Prestamo.__table__.columns.keys()

    # Guardamos solo los datos que pertenecen a la tabla
    # El ID no se incluye porque lo generamos nosotros
    valores = {k: v for k, v in datos.items() if k in columnas and k != "ID"}

    # Generamos un identificador para el nuevo préstamo
    valores["ID"] = uuid.uuid4().hex[:6].upper()

    prestamo = Prestamo(**valores)
    db.session.add(prestamo)
    db.session.commit()
    return jsonify(a_diccionario(prestamo)), 201


@app.delete("/api/v1/prestamos/<id>")
def eliminar_prestamo(id):
    """Borra un préstamo."""
    prestamo = buscar_prestamo(id)
    db.session.delete(prestamo)
    db.session.commit()
    return "", 204


# Integrar con una API externa 

@app.get("/api/v1/prestamos/<id>/conversion")
def convertir_monto(id):
    """Convierte el Monto_Inicial de euros a otra moneda: ?moneda=USD"""
    moneda = request.args.get("moneda", default="USD").upper()
    prestamo = buscar_prestamo(id)

    try:
        respuesta = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": "EUR", "symbols": moneda},
            timeout=5,
        )
        respuesta.raise_for_status()
        tasa = respuesta.json()["rates"][moneda]
    except (requests.RequestException, KeyError):
        abort(502, description="No se pudo consultar la API externa de tipos de cambio")

    return jsonify({
        "id": id,
        "monto_eur": prestamo.Monto_Inicial,
        "moneda": moneda,
        "tasa": tasa,
        "monto_convertido": round(prestamo.Monto_Inicial * tasa, 2),
    })


# que los errores: siempre estén en formato JSON

@app.errorhandler(HTTPException)
def manejar_error(error):
    return jsonify({"error": {"code": error.code, "message": error.description}}), error.code


if __name__ == "__main__":
    app.run(debug=True)