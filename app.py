from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
import resend

# Cargar variables del entorno (.env o Render)
load_dotenv()

app = Flask(__name__)

# ✉️ FUNCIÓN DE ENVÍO DE CORREO CON RESEND
def enviar_correo_cotizacion(nombre, email, telefono, plan, mensaje_cliente):
    try:
        # API KEY FIJA PARA TU PROGRAMA
        resend.api_key = os.getenv("RESEND_API_KEY")

        remitente = os.getenv("RESEND_SENDER")
        destinatario = "asesoriadeseguro123@gmail.com"  # correo fijo que recibe todas las cotizaciones

        print(f"🔧 RESEND_API_KEY configurada: {'Sí' if resend.api_key else 'No'}")
        print(f"🔧 Remitente: {remitente}")
        print(f"🔧 Destinatario fijo: {destinatario}")

        if not resend.api_key:
            print("❌ ERROR: RESEND_API_KEY no configurada en Render.")
            return False

        if not remitente:
            print("❌ ERROR: RESEND_SENDER no configurado en Render.")
            return False

        # Construcción del HTML bonito
        html = f"""
        <h2>📋 NUEVA COTIZACIÓN DE SEGUROS</h2>

        <p><strong>👤 Nombre:</strong> {nombre}</p>
        <p><strong>📧 Email:</strong> {email}</p>
        <p><strong>📞 Teléfono:</strong> {telefono}</p>
        <p><strong>🛡️ Plan de interés:</strong> {plan}</p>

        <h3>💬 Mensaje del cliente:</h3>
        <p>{mensaje_cliente}</p>

        <hr>
        <p>📅 Enviado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        """

        # Enviar correo
        response = resend.Emails.send({
            "from": f"Asesoría de Seguros <{remitente}>",
            "to": destinatario,
            "subject": f"📋 Nueva Cotización - {nombre}",
            "html": html
        })

        print("✅ Correo enviado correctamente:", response)
        return True

    except Exception as e:
        print("❌ ERROR enviando correo con Resend:", e)
        return False


# 🔥 ENDPOINT PARA RECIBIR COTIZACIONES DESDE EL FRONTEND
@app.route("/enviar-cotizacion", methods=["POST"])
def enviar_cotizacion():
    try:
        data = request.get_json()
        print(f"📝 Datos recibidos:", data)

        nombre = data.get("name")
        email = data.get("email")
        telefono = data.get("phone")
        plan = data.get("plan_type")
        mensaje = data.get("message")

        if not nombre or not email or not telefono:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        if enviar_correo_cotizacion(nombre, email, telefono, plan, mensaje):
            return jsonify({"status": "success", "message": "¡Gracias! Tu cotización fue enviada correctamente."})
        else:
            return jsonify({"error": "Error enviando el correo"}), 500

    except Exception as e:
        print("❌ ERROR en /enviar-cotizacion:", e)
        return jsonify({"error": "Error interno del servidor"}), 500


# 🌐 SERVIR TU LANDING PAGE
@app.route("/")
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# Servir logos e imágenes estáticas
@app.route('/static/<path:path>')
def serve_static(path):
    return app.send_static_file(path)


# 🚀 EJECUCIÓN EN PRODUCCIÓN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
