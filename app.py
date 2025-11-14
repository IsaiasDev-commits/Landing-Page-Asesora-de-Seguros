from flask import Flask, request, jsonify
from datetime import datetime
import os
import resend
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

app = Flask(__name__)

# -------------------------------------------------------
# 🩺 HEALTH CHECK ENDPOINT (CRÍTICO PARA RENDER)
# -------------------------------------------------------

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Servidor funcionando"}), 200

@app.route('/ping')
def ping():
    return 'pong', 200

# -------------------------------------------------------
# ✉️ FUNCIÓN PARA ENVIAR LOS CORREOS (ESTILO EQUILIBRA)
# -------------------------------------------------------

def enviar_correo_resend_seguros(nombre, correo, telefono, plan, mensaje_cliente):
    try:
        resend_api_key = os.getenv("RESEND_API_KEY")

        if not resend_api_key:
            print("❌ ERROR: RESEND_API_KEY no configurada en Render.")
            return False

        resend.api_key = resend_api_key

        # HTML del correo — estilo profesional como Equilibra
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto;">
            <h2 style="color: #003366; text-align: center;">📩 NUEVA SOLICITUD DE INFORMACIÓN - SEGUROS</h2>

            <div style="background: #f4f6f9; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <p><strong>Nombre Completo:</strong> {nombre}</p>
                <p><strong>Correo Electrónico:</strong> {correo}</p>
                <p><strong>Teléfono:</strong> {telefono}</p>
                <p><strong>Plan de interés:</strong> {plan}</p>
                <p><strong>Mensaje del usuario:</strong><br>{mensaje_cliente}</p>
            </div>

            <p>El usuario ha solicitado información desde la página web.</p>
            <p>Por favor contáctalo cuanto antes para brindarle asesoría.</p>

            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #003366;">
                <p>Saludos,<br>
                <strong>Protección Total</strong> - Tu Proveedor de Seguros.</p>
            </div>
        </div>
        """

        # Envío del correo
        response = resend.Emails.send({
            "from": "Protección Total <onboarding@resend.dev>",
            "to": "asesoriadeseguro123@gmail.com",   # DESTINATARIO FIJO
            "subject": f"📩 Nueva solicitud - {nombre}",
            "html": html_body
        })

        print(f"📧 Correo enviado correctamente vía Resend: {response}")
        return True

    except Exception as e:
        print(f"❌ ERROR enviando correo con Resend: {e}")
        return False


# -------------------------------------------------------
# 🔥 ENDPOINT QUE RECIBE EL FORMULARIO DEL SITIO WEB
# -------------------------------------------------------

@app.route("/enviar-cotizacion", methods=["POST"])
def enviar_cotizacion():
    try:
        data = request.get_json()
        print(f"📝 Datos recibidos: {data}")

        nombre = data.get("name")
        correo = data.get("email")
        telefono = data.get("phone")
        plan = data.get("plan_type")
        mensaje = data.get("message")

        if not nombre or not correo or not telefono:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        enviado = enviar_correo_resend_seguros(nombre, correo, telefono, plan, mensaje)

        if enviado:
            return jsonify({
                "status": "success",
                "message": "¡Gracias! Tu solicitud fue enviada correctamente."
            })
        else:
            return jsonify({"error": "No se pudo enviar el correo."}), 500

    except Exception as e:
        print(f"❌ ERROR en /enviar-cotizacion: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# -------------------------------------------------------
# 🌐 SERVIR TU LANDING PAGE
# -------------------------------------------------------

@app.route("/")
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route("/static/<path:path>")
def serve_static(path):
    return app.send_static_file(path)


# -------------------------------------------------------
# 🚀 EJECUCIÓN (GUNICORN SE ENCARGA EN PRODUCCIÓN)
# -------------------------------------------------------

if __name__ == "__main__":
    # Solo para desarrollo local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
