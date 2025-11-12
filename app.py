from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Permitir CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


def enviar_correo_confirmacion(destinatario, nombre, email, telefono, plan_interes, mensaje_cliente):
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    app.logger.info(f"📧 Intentando enviar correo desde: {remitente} -> {destinatario}")
    app.logger.info(f"🔒 ¿Contraseña presente?: {'SÍ' if password else 'NO'}")

    if not remitente or not password:
        app.logger.error("❌ Faltan credenciales de correo (EMAIL_USER o EMAIL_PASSWORD).")
        return False

    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = f"📋 Nueva cotización de seguros - {nombre}"

    cuerpo = f"""
    📋 NUEVA SOLICITUD DE COTIZACIÓN - PROTECCIÓN TOTAL

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

    mensaje.attach(MIMEText(cuerpo, 'plain'))

    try:
        # Crear contexto SSL compatible
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')

        app.logger.info("🔧 Intentando conexión SSL con Gmail (puerto 465)...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(remitente, password)
            server.send_message(mensaje)
        app.logger.info(f"✅ Correo enviado correctamente a {destinatario} (SSL)")
        return True

    except Exception as e:
        app.logger.error(f"❌ Error con SSL: {e}")

        try:
            app.logger.info("🔧 Reintentando con STARTTLS (puerto 587)...")
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls(context=context)
                server.login(remitente, password)
                server.send_message(mensaje)
            app.logger.info(f"✅ Correo enviado correctamente a {destinatario} (STARTTLS)")
            return True
        except Exception as e2:
            app.logger.error(f"❌ Error con STARTTLS: {e2}")
            return False


@app.route("/enviar-cotizacion", methods=["POST", "OPTIONS"])
def enviar_cotizacion():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    try:
        data = request.get_json()
        app.logger.info(f"📨 Datos recibidos: {data}")

        if not data:
            return jsonify({"error": "Datos incompletos"}), 400

        nombre = data.get("name", "").strip()
        email = data.get("email", "").strip()
        telefono = data.get("phone", "").strip()
        plan_interes = data.get("plan_type", "").strip()
        mensaje = data.get("message", "").strip()

        if not nombre or not email or not telefono:
            return jsonify({"error": "Por favor completa todos los campos requeridos"}), 400

        destinatario = os.getenv("ASESORA_SEGUROS_EMAIL")  # Asegúrate de que coincide con tu variable Render
        if not destinatario:
            app.logger.error("❌ No se encontró ASESORA_SEGUROS_EMAIL en las variables de entorno.")
            return jsonify({"error": "Error interno: Falta variable de destino."}), 500

        if enviar_correo_confirmacion(destinatario, nombre, email, telefono, plan_interes, mensaje):
            app.logger.info(f"✅ Cotización enviada a {destinatario} por {nombre}")
            return jsonify({
                "status": "success",
                "message": "¡Gracias! Nuestra asesora te contactará en menos de 24 horas."
            })
        else:
            return jsonify({"error": "Error al enviar la solicitud. Intenta nuevamente."}), 500

    except Exception as e:
        app.logger.error(f"❌ Error en /enviar-cotizacion: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route("/debug-email")
def debug_email():
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    destinatario = os.getenv("ASESORA_SEGUROS_EMAIL")

    info = {
        "EMAIL_USER": remitente,
        "EMAIL_PASSWORD_set": "SÍ" if password else "NO",
        "ASESORA_SEGUROS_EMAIL": destinatario,
        "longitud_password": len(password) if password else 0
    }

    return jsonify(info)


@app.route('/')
def landing_page():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.logger.info("🚀 Iniciando servidor de Protección Total...")
    app.run(host='0.0.0.0', port=port, debug=True)
