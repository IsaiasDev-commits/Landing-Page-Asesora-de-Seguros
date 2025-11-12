from flask import Flask, request, jsonify
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Envío de correo con configuración comprobada
def enviar_correo_confirmacion(destinatario, nombre, email, telefono, plan_interes, mensaje_cliente):
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    if not remitente or not password:
        print("❌ Credenciales de Gmail no configuradas.")
        return False

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = f"📋 Nueva cotización de seguros - {nombre}"

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
    mensaje.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remitente, password)
            server.send_message(mensaje)
        print(f"✅ Correo enviado a {destinatario}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False


@app.route("/enviar-cotizacion", methods=["POST"])
def enviar_cotizacion():
    try:
        data = request.get_json()
        nombre = data.get("name", "")
        email = data.get("email", "")
        telefono = data.get("phone", "")
        plan_interes = data.get("plan_type", "")
        mensaje = data.get("message", "")

        if not nombre or not email or not telefono:
            return jsonify({"error": "Por favor completa todos los campos requeridos"}), 400

        destinatario = os.getenv("ASESORA_SEGUROS_EMAIL")
        if enviar_correo_confirmacion(destinatario, nombre, email, telefono, plan_interes, mensaje):
            return jsonify({"status": "success", "message": "¡Gracias! Nuestra asesora te contactará pronto."})
        else:
            return jsonify({"error": "No se pudo enviar el correo. Verifica las credenciales."}), 500

    except Exception as e:
        print(f"❌ Error en /enviar-cotizacion: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/")
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
