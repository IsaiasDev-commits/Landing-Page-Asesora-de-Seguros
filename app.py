from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
import resend

# Cargar variables del entorno (.env o Render)
load_dotenv()

app = Flask(__name__)

# ✉️ FUNCIÓN DE ENVÍO DE CORREO CON RESEND (CORRECTA)
def enviar_correo_confirmacion(nombre, email, telefono, plan_interes, mensaje_cliente):
    api_key = os.getenv("RESEND_API_KEY")
    remitente = os.getenv("RESEND_SENDER")

    # DESTINATARIO FIJO (tu correo)
    destinatario = "asesoriadeseguro123@gmail.com"

    print(f"🔧 RESEND API KEY: {'CONFIGURADA' if api_key else 'NO CONFIGURADA'}")
    print(f"🔧 REMITENTE: {remitente}")
    print(f"🔧 DESTINATARIO FIJO: {destinatario}")

    if not api_key or not remitente:
        print("❌ Falta RESEND_API_KEY o RESEND_SENDER")
        return False

    resend.api_key = api_key

    # Construcción del correo HTML
    html = f"""
        <h2>📋 NUEVA SOLICITUD DE COTIZACIÓN</h2>

        <p><strong>👤 Nombre:</strong> {nombre}</p>
        <p><strong>📧 Email:</strong> {email}</p>
        <p><strong>📞 Teléfono:</strong> {telefono}</p>
        <p><strong>🏦 Plan de interés:</strong> {plan_interes}</p>

        <h3>💬 Mensaje del cliente:</h3>
        <p>{mensaje_cliente}</p>

        <hr>
        <p>📅 Enviado el {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        <p>🔔 Contactar al cliente lo antes posible.</p>
    """

    try:
        response = resend.Emails.send({
            "from": f"Protección Total <{remitente}>",
            "to": destinatario,
            "subject": f"📋 Nueva cotización de seguros - {nombre}",
            "html": html
        })

        print("✅ Correo enviado mediante Resend:", response)
        return True

    except Exception as e:
        print("❌ Error Resend:", e)
        return False


# 🔥 ENDPOINT QUE RECIBE EL FORMULARIO DEL FRONTEND
@app.route("/enviar-cotizacion", methods=["POST"])
def enviar_cotizacion():
    try:
        data = request.get_json()
        print(f"📝 Datos recibidos: {data}")
        
        nombre = data.get("name", "")
        email = data.get("email", "")
        telefono = data.get("phone", "")
        plan_interes = data.get("plan_type", "")
        mensaje = data.get("message", "")

        if not nombre or not email or not telefono:
            return jsonify({"error": "Por favor completa todos los campos requeridos"}), 400
        
        # Llama a la función SIN necesidad de destinatario
        if enviar_correo_confirmacion(nombre, email, telefono, plan_interes, mensaje):
            return jsonify({"status": "success", "message": "¡Gracias! Nuestra asesora te contactará pronto."})
        else:
            return jsonify({"error": "Error al enviar el correo. Intenta nuevamente más tarde."}), 500

    except Exception as e:
        print(f"❌ Error en /enviar-cotizacion: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# 🌐 SERVIR TU LANDING PAGE
@app.route("/")
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# Servir archivos estáticos (logos, imágenes)
@app.route('/static/<path:path>')
def serve_static(path):
    return app.send_static_file(path)


# 🚀 EJECUCIÓN EN PRODUCCIÓN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
