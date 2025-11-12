from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# Cargar variables del entorno (.env o Render)
load_dotenv()

app = Flask(__name__)

# ✉️ Envío de correo con Mailjet API - VERSIÓN CORREGIDA
def enviar_correo_confirmacion(destinatario, nombre, email, telefono, plan_interes, mensaje_cliente):
    api_key = os.getenv("MAILJET_API_KEY")
    api_secret = os.getenv("MAILJET_SECRET_KEY")
    remitente = os.getenv("MAILJET_SENDER")

    print(f"🔧 Debug: API Key: {api_key[:8]}...")  # Solo mostrar primeros 8 chars
    print(f"🔧 Debug: API Secret: {api_secret[:8]}...")
    print(f"🔧 Debug: Remitente: {remitente}")
    print(f"🔧 Debug: Destinatario: {destinatario}")

    if not all([api_key, api_secret, remitente, destinatario]):
        print("❌ Variables de entorno Mailjet faltantes.")
        return False

    cuerpo = f"""
    📋 NUEVA SOLICITUD DE COTIZACIÓN

    👤 Nombre: {nombre}
    📧 Email: {email}
    📞 Teléfono: {telefono}
    🏦 Plan de interés: {plan_interes if plan_interes else 'No especificado'}

    💬 Mensaje del cliente:
    {mensaje_cliente}

    ---
    📅 Enviado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}
    🔔 Contactar al cliente lo antes posible.
    """

    data = {
        "Messages": [
            {
                "From": {"Email": remitente, "Name": "Cotizador de Seguros"},
                "To": [{"Email": destinatario, "Name": "Asesora de Seguros"}],
                "Subject": f"📋 Nueva cotización de seguros - {nombre}",
                "TextPart": cuerpo,
            }
        ]
    }

    try:
        print("📤 Intentando enviar correo via Mailjet...")
        response = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(api_key, api_secret),
            json=data,
            timeout=30
        )

        print(f"📨 Respuesta Mailjet - Status: {response.status_code}")
        print(f"📨 Respuesta Mailjet - Text: {response.text}")

        if response.status_code == 200:
            print(f"✅ Correo enviado correctamente a {destinatario}")
            return True
        else:
            print(f"❌ Error Mailjet: {response.status_code}")
            # Intentar parsear el error de Mailjet
            try:
                error_data = response.json()
                print(f"❌ Detalles del error: {error_data}")
            except:
                print(f"❌ Error sin detalles: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error al enviar correo: {str(e)}")
        return False


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

        destinatario = os.getenv("ASESORA_SEGUROS_EMAIL")
        print(f"🎯 Enviando a: {destinatario}")
        
        if enviar_correo_confirmacion(destinatario, nombre, email, telefono, plan_interes, mensaje):
            return jsonify({"status": "success", "message": "¡Gracias! Nuestra asesora te contactará pronto."})
        else:
            return jsonify({"error": "Error al enviar el correo. Intenta nuevamente más tarde."}), 500

    except Exception as e:
        print(f"❌ Error en /enviar-cotizacion: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/")
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# Servir archivos estáticos (para los logos)
@app.route('/static/<path:path>')
def serve_static(path):
    return app.send_static_file(path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)