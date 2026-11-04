import uuid

import requests
from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from werkzeug.exceptions import HTTPException
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://clase:clase123@db:3306/creditos"
)

db = SQLAlchemy(app)


class Prestamo(db.Model):
    """Modelo de la tabla prestamos cargada por load_data.py."""
    __tablename__ = "prestamos"

    ID = db.Column(String(10), primary_key=True)
    Edad = db.Column(db.Integer)
    Ingresos = db.Column(db.Float)
    Monto_Inicial = db.Column(db.Float, nullable=False)
    Scoring_Crediticio = db.Column(db.Integer)
    Meses_Empleo = db.Column(db.Float)
    Num_Creditos = db.Column(db.Integer)
    Ratio_Interes = db.Column(db.Float)
    Duracion = db.Column(db.Float, nullable=False)
    Ratio_Deuda_Ingresos = db.Column(db.Float)
    Estudios = db.Column(db.String(100))
    Tipo_Jornada_Laboral = db.Column(db.String(100))
    Estado_Civil = db.Column(db.String(100))
    Posesion_Hipoteca = db.Column(db.Float)
    Personas_Cargo = db.Column(db.Float)
    Proposito = db.Column(db.String(100))
    Fiador = db.Column(db.Float)
    Impago = db.Column(db.Integer)
    Prima = db.Column(db.Float)
    prob_impago = db.Column(db.Float)
    prediccion = db.Column(db.Integer)
    predicciones_Prima = db.Column(db.Float)


def a_diccionario(prestamo):
    return {
        columna.name: getattr(prestamo, columna.name)
        for columna in Prestamo.__table__.columns
    }


def buscar_prestamo(id):
    prestamo = db.session.get(Prestamo, id)
    if prestamo is None:
        abort(404, description=f"Préstamo {id} no encontrado")
    return prestamo


@app.get("/")
def inicio():
    return jsonify({
        "mensaje": "API de préstamos funcionando correctamente",
        "endpoints": {
            "listar_prestamos": "/api/v1/prestamos",
            "consultar_prestamo": "/api/v1/prestamos/<id>",
        },
    })


@app.get("/api/v1/prestamos")
def listar_prestamos():
    impago = request.args.get("impago", type=int)
    estudios = request.args.get("estudios")
    limit = request.args.get("limit", type=int)

    consulta = db.select(Prestamo)
    if impago is not None:
        consulta = consulta.where(Prestamo.Impago == impago)
    if estudios:
        consulta = consulta.where(Prestamo.Estudios == estudios)
    if limit is not None:
        if limit < 1:
            abort(400, description="limit debe ser un número mayor que 0")
        consulta = consulta.limit(limit)

    prestamos = db.session.execute(consulta).scalars().all()
    return jsonify([a_diccionario(p) for p in prestamos])


@app.get("/api/v1/prestamos/<id>")
def obtener_prestamo(id):
    return jsonify(a_diccionario(buscar_prestamo(id)))


@app.post("/api/v1/prestamos")
def crear_prestamo():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        abort(400, description="Debes enviar un objeto JSON")
    if datos.get("Monto_Inicial") is None or datos.get("Duracion") is None:
        abort(400, description="Faltan Monto_Inicial y Duracion")

    columnas = Prestamo.__table__.columns.keys()
    valores = {k: v for k, v in datos.items() if k in columnas and k != "ID"}
    valores["ID"] = uuid.uuid4().hex[:6].upper()
    prestamo = Prestamo(**valores)
    db.session.add(prestamo)
    db.session.commit()
    return jsonify(a_diccionario(prestamo)), 201


@app.patch("/api/v1/prestamos/<id>")
def actualizar_prestamo(id):
    prestamo = buscar_prestamo(id)
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or not datos:
        abort(400, description="Debes enviar un JSON con datos")

    columnas = Prestamo.__table__.columns.keys()
    for campo, valor in datos.items():
        if campo in columnas and campo != "ID":
            setattr(prestamo, campo, valor)
    db.session.commit()
    return jsonify(a_diccionario(prestamo))


@app.delete("/api/v1/prestamos/<id>")
def eliminar_prestamo(id):
    prestamo = buscar_prestamo(id)
    db.session.delete(prestamo)
    db.session.commit()
    return "", 204


@app.get("/api/v1/prestamos/<id>/conversion")
def convertir_monto(id):
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


@app.errorhandler(HTTPException)
def manejar_error(error):
    return jsonify({
        "error": {"code": error.code, "message": error.description}
    }), error.code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
